
import os
import sys
import json
import time
import logging
from pathlib import Path
# 强制标准输出和错误输出使用 UTF-8
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")
import pymysql
import redis

from dotenv import load_dotenv
from pydantic import BaseModel, Field, ValidationError
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)
from mcp.server.fastmcp import FastMCP


# =================================
# 1. 环境变量与日志配置
# =================================

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR.parent / ".env")

CURRENT_USER_ID = os.getenv("ORDER_AGENT_USER_ID", "1")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stderr)
    ]
)

logger = logging.getLogger("OrderMCP")

mcp = FastMCP("Order MCP Server")


# =================================
# 2. Redis 配置
# =================================

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", "6379")),
    db=int(os.getenv("REDIS_DB", "0")),
    password=os.getenv("REDIS_PASSWORD") or None,
    decode_responses=True,
    socket_connect_timeout=3,
    socket_timeout=3
)


# =================================
# 3. MySQL 配置
# =================================

MYSQL_CONFIG = {
    "host": os.getenv("MYSQL_HOST"),
    "port": int(os.getenv("MYSQL_PORT", "3306")),
    "user": os.getenv("MYSQL_USER"),
    "password": os.getenv("MYSQL_PASSWORD"),
    "database": os.getenv("MYSQL_DATABASE"),
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor,
    "connect_timeout": 5
}


# =================================
# 4. Pydantic 参数校验
# =================================

class OrderQueryInput(BaseModel):
    order_no: str = Field(
        min_length=5,
        max_length=5,
        pattern=r"^A\d{4}$",
        description="订单编号，例如 A1001"
    )


class OrderCalculateInput(BaseModel):
    price: float = Field(gt=0, description="商品单价")
    quantity: int = Field(gt=0, description="购买数量")
    discount: float = Field(
        ge=0,
        le=1,
        description="折扣比例，例如 0.8 表示八折"
    )


# =================================
# 5. MySQL 查询：带 Retry
# =================================

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(
        multiplier=1,
        min=1,
        max=4
    ),
    retry=retry_if_exception_type((
        pymysql.OperationalError,
        pymysql.InterfaceError
    )),
    before_sleep=before_sleep_log(
        logger,
        logging.WARNING
    ),
    reraise=True
)
def query_mysql(order_no: str):

    connection = None

    try:
        connection = pymysql.connect(**MYSQL_CONFIG)

        with connection.cursor() as cursor:
            sql = """
                SELECT order_no, status, amount, user_id
                FROM orders
                WHERE order_no = %s
            """

            cursor.execute(sql, (order_no,))

            return cursor.fetchone()

    finally:
        if connection is not None:
            connection.close()


# =================================
# 6. 用户权限验证
# =================================

def check_order_permission(order: dict) -> bool:

    if str(order["user_id"]) != str(CURRENT_USER_ID):

        logger.warning(
            "权限拒绝：当前用户 %s 尝试访问订单 %s（所属用户 %s）",
            CURRENT_USER_ID,
            order["order_no"],
            order["user_id"]
        )

        return False

    return True


# =================================
# 7. MCP Tool：订单查询
# =================================

@mcp.tool()
def query_order(order_no: str) -> str:
    """
    查询当前用户自己的订单。
    优先使用 Redis，缓存未命中时查询 MySQL。
    记录 Redis、MySQL 和整体工具执行耗时。
    """

    # 记录整个订单查询的开始时间
    total_start = time.perf_counter()

    try:

        # ---------- 7.1 输入校验 ----------

        validated = OrderQueryInput(order_no=order_no)
        order_no = validated.order_no

        cache_key = f"order:{order_no}"

        order = None

        # ---------- 7.2 Redis 查询计时 ----------

        redis_start = time.perf_counter()

        try:
            cached_data = redis_client.get(cache_key)

            redis_elapsed = (
                time.perf_counter() - redis_start
            ) * 1000

            logger.info(
                "Redis GET 耗时：%.3f ms",
                redis_elapsed
            )

            if cached_data:

                order = json.loads(cached_data)

                logger.info(
                    "Redis 缓存命中：%s",
                    order_no
                )

            else:

                logger.info(
                    "Redis 缓存未命中：%s",
                    order_no
                )

        except (
            redis.RedisError,
            json.JSONDecodeError,
            TypeError
        ):

            redis_elapsed = (
                time.perf_counter() - redis_start
            ) * 1000

            logger.exception(
                "Redis 读取异常，降级查询 MySQL，耗时 %.3f ms",
                redis_elapsed
            )

        # ---------- 7.3 MySQL 查询计时 ----------

        if order is None:

            logger.info(
                "开始查询 MySQL：%s",
                order_no
            )

            mysql_start = time.perf_counter()

            order = query_mysql(order_no)

            mysql_elapsed = (
                time.perf_counter() - mysql_start
            ) * 1000

            logger.info(
                "MySQL 查询耗时：%.3f ms",
                mysql_elapsed
            )

            if order is None:

                logger.info(
                    "订单不存在：%s",
                    order_no
                )

                return (
                    f"没有找到订单编号为 {order_no} 的订单。"
                )

            # 将 Decimal 金额转换为字符串，方便 JSON 序列化
            order["amount"] = str(order["amount"])

            # ---------- 7.4 Redis 写入计时 ----------

            redis_write_start = time.perf_counter()

            try:

                result = redis_client.set(
                    cache_key,
                    json.dumps(
                        order,
                        ensure_ascii=False
                    ),
                    ex=300
                )

                redis_write_elapsed = (
                    time.perf_counter() - redis_write_start
                ) * 1000

                logger.info(
                    "Redis SET 耗时：%.3f ms",
                    redis_write_elapsed
                )

                if result:

                    logger.info(
                        "Redis 缓存写入成功：%s",
                        order_no
                    )

                else:

                    logger.warning(
                        "Redis 缓存写入未成功：%s",
                        order_no
                    )

            except redis.RedisError:

                redis_write_elapsed = (
                    time.perf_counter() - redis_write_start
                ) * 1000

                logger.exception(
                    "Redis 写入异常，耗时 %.3f ms",
                    redis_write_elapsed
                )

        # ---------- 7.5 权限检查 ----------

        if not check_order_permission(order):

            return "权限不足：你无权查询该订单。"

        # ---------- 7.6 返回订单结果 ----------

        logger.info(
            "订单查询成功：%s",
            order_no
        )

        return (
            f"订单编号：{order['order_no']}\n"
            f"订单状态：{order['status']}\n"
            f"订单金额：{order['amount']} 元\n"
            f"用户ID：{order['user_id']}"
        )

    except ValidationError:

        logger.warning(
            "订单编号格式错误：%s",
            order_no
        )

        return "订单编号格式错误，请使用 A1001 这样的格式。"

    except pymysql.MySQLError as e:

        logger.exception("MySQL 查询失败")

        return f"MySQL 查询失败：{type(e).__name__}"

    except Exception as e:

        logger.exception("订单查询出现异常")

        return f"订单查询失败：{type(e).__name__}"

    finally:

        # 无论成功还是失败，都记录整个工具的耗时
        total_elapsed = (
            time.perf_counter() - total_start
        ) * 1000

        logger.info(
            "订单工具总耗时：%.3f ms",
            total_elapsed
        )


# =================================
# 8. MCP Tool：订单金额计算
# =================================

@mcp.tool()
def calculate_order(
    price: float,
    quantity: int,
    discount: float
) -> str:
    """
    根据商品单价、购买数量和折扣计算订单总金额。
    """

    try:

        data = OrderCalculateInput(
            price=price,
            quantity=quantity,
            discount=discount
        )

        total = (
            data.price
            * data.quantity
            * data.discount
        )

        logger.info(
            "订单金额计算成功：%.2f",
            total
        )

        return f"订单总金额：{total:.2f} 元"

    except ValidationError as e:

        logger.warning(
            "订单金额计算参数校验失败"
        )

        return f"参数校验失败：{e}"


# =================================
# 9. 启动 MCP Server
# =================================

if __name__ == "__main__":

    logger.info("Order MCP Server 启动")

    mcp.run(transport="stdio")
