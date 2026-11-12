
import os
import json
from pathlib import Path

import pymysql
import redis

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP


# =================================
# 1. 加载环境变量
# =================================

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR.parent / ".env")


# =================================
# 2. 创建 MCP Server
# =================================

mcp = FastMCP("Order MCP Server")


# =================================
# 3. Redis 配置
# =================================

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", "6379")),
    db=int(os.getenv("REDIS_DB", "0")),
    password=os.getenv("REDIS_PASSWORD") or None,
    decode_responses=True
)


# =================================
# 4. MySQL 配置
# =================================

MYSQL_CONFIG = {
    "host": os.getenv("MYSQL_HOST"),
    "port": int(os.getenv("MYSQL_PORT", "3306")),
    "user": os.getenv("MYSQL_USER"),
    "password": os.getenv("MYSQL_PASSWORD"),
    "database": os.getenv("MYSQL_DATABASE"),
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor
}


# =================================
# 5. MySQL 查询函数
# =================================

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
# 6. MCP Tool：订单查询
# =================================

@mcp.tool()
def query_order(order_no: str) -> str:
    """
    根据订单编号查询订单。
    优先使用 Redis 缓存，缓存未命中时查询 MySQL。
    """

    cache_key = f"order:{order_no}"

    # 先查询 Redis
    try:
        cached_data = redis_client.get(cache_key)

        if cached_data:
            order = json.loads(cached_data)

            return (
                f"数据来源：Redis 缓存\n"
                f"订单编号：{order['order_no']}\n"
                f"订单状态：{order['status']}\n"
                f"订单金额：{order['amount']} 元\n"
                f"用户ID：{order['user_id']}"
            )

    except redis.RedisError:
        pass

    # 缓存未命中，查询 MySQL
    try:
        order = query_mysql(order_no)

        if order is None:
            return f"没有找到订单编号为 {order_no} 的订单。"

        order["amount"] = str(order["amount"])

        # 回填 Redis 缓存
        try:
            redis_client.set(
                cache_key,
                json.dumps(order, ensure_ascii=False),
                ex=300
            )
        except redis.RedisError:
            pass

        return (
            f"数据来源：MySQL 数据库\n"
            f"订单编号：{order['order_no']}\n"
            f"订单状态：{order['status']}\n"
            f"订单金额：{order['amount']} 元\n"
            f"用户ID：{order['user_id']}"
        )

    except pymysql.MySQLError as e:
        return f"MySQL 查询失败：{type(e).__name__}"


# =================================
# 7. MCP Tool：订单金额计算
# =================================

class OrderInput(BaseModel):
    price: float = Field(gt=0, description="商品单价")
    quantity: int = Field(gt=0, description="购买数量")
    discount: float = Field(
        ge=0,
        le=1,
        description="折扣比例，例如 0.8 表示八折"
    )


@mcp.tool()
def calculate_order(
    price: float,
    quantity: int,
    discount: float
) -> str:
    """
    根据商品单价、购买数量和折扣计算订单总金额。
    """

    if price <= 0 or quantity <= 0:
        return "单价和购买数量必须大于 0。"

    if not 0 <= discount <= 1:
        return "折扣比例必须在 0 到 1 之间。"

    total = price * quantity * discount

    return f"订单总金额：{total:.2f} 元"


# =================================
# 8. 启动 MCP Server
# =================================

if __name__ == "__main__":
    mcp.run(transport="stdio")
