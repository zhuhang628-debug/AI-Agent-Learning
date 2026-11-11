
import os
import json
from pathlib import Path

import pymysql
import redis
from dotenv import load_dotenv
from pydantic import BaseModel, Field

from langchain.agents import create_agent
from langchain.tools import tool
from langchain_openai import ChatOpenAI


# ==============================
# 1. 加载环境变量
# ==============================

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR.parent / ".env")


# ==============================
# 2. Redis 配置
# ==============================

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", "6379")),
    db=int(os.getenv("REDIS_DB", "0")),
    password=os.getenv("REDIS_PASSWORD") or None,
    decode_responses=True
)


# ==============================
# 3. MySQL 配置
# ==============================

MYSQL_CONFIG = {
    "host": os.getenv("MYSQL_HOST"),
    "port": int(os.getenv("MYSQL_PORT", "3306")),
    "user": os.getenv("MYSQL_USER"),
    "password": os.getenv("MYSQL_PASSWORD"),
    "database": os.getenv("MYSQL_DATABASE"),
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor
}


# ==============================
# 4. 定义 Tool 参数
# ==============================

class OrderQueryInput(BaseModel):
    order_no: str = Field(
        description="需要查询的订单编号，例如 A1001"
    )


# ==============================
# 5. MySQL 查询函数
# ==============================

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


# ==============================
# 6. Redis + MySQL 缓存 Tool
# ==============================

@tool(args_schema=OrderQueryInput)
def query_order(order_no: str) -> str:
    """根据订单编号查询订单，优先读取 Redis，缓存未命中时查询 MySQL。"""

    cache_key = f"order:{order_no}"

    # 先查询 Redis
    try:
        cached_data = redis_client.get(cache_key)

        if cached_data:

            print(f"[Redis] Cache HIT: {cache_key}")

            order = json.loads(cached_data)

            return (
                f"数据来源：Redis 缓存\n"
                f"订单编号：{order['order_no']}\n"
                f"订单状态：{order['status']}\n"
                f"订单金额：{order['amount']} 元\n"
                f"用户ID：{order['user_id']}"
            )

        print(f"[Redis] Cache MISS: {cache_key}")

    except redis.RedisError as e:
        print(f"[Redis] 缓存读取失败：{type(e).__name__}")

    # Redis 未命中，查询 MySQL
    try:
        order = query_mysql(order_no)

        if order is None:
            return f"没有找到订单编号为 {order_no} 的订单。"

        # Decimal 转成字符串，方便 JSON 序列化
        order["amount"] = str(order["amount"])

        # 查询结果写入 Redis，缓存 300 秒
        try:
            redis_client.set(
                cache_key,
                json.dumps(order, ensure_ascii=False),
                ex=300
            )

            print(f"[Redis] Cache SET: {cache_key}, TTL=300s")

        except redis.RedisError as e:
            print(f"[Redis] 缓存写入失败：{type(e).__name__}")

        return (
            f"数据来源：MySQL 数据库\n"
            f"订单编号：{order['order_no']}\n"
            f"订单状态：{order['status']}\n"
            f"订单金额：{order['amount']} 元\n"
            f"用户ID：{order['user_id']}"
        )

    except pymysql.MySQLError as e:
        return f"MySQL 查询失败，错误类型：{type(e).__name__}"


# ==============================
# 7. 初始化 DeepSeek
# ==============================

api_key = os.getenv("DEEPSEEK_API_KEY")

if not api_key:
    raise ValueError("未找到 DEEPSEEK_API_KEY")

llm = ChatOpenAI(
    model="deepseek-chat",
    api_key=api_key,
    base_url="https://api.deepseek.com/v1",
    temperature=0
)


# ==============================
# 8. 创建 Agent
# ==============================

agent = create_agent(
    model=llm,
    tools=[query_order],
    system_prompt="""
    你是一个订单查询助手。

    用户询问订单信息时，必须调用 query_order 工具。
    根据工具返回的真实数据回答，不允许编造订单信息。
    普通闲聊不需要调用工具。
    """
)


# ==============================
# 9. 运行 Agent
# ==============================

if __name__ == "__main__":

    try:
        print("Redis 连接状态：", redis_client.ping())
    except redis.RedisError as e:
        raise ConnectionError(
            f"Redis 连接失败：{type(e).__name__}"
        )

    question = input("请输入你的问题：")

    result = agent.invoke({
        "messages": [
            {"role": "user", "content": question}
        ]
    })

    print("\n========== Agent 执行过程 ==========")

    for message in result["messages"]:

        print(f"\n消息类型：{message.type}")

        if hasattr(message, "tool_calls") and message.tool_calls:
            print("工具调用：", message.tool_calls)

        if message.type == "tool":
            print("工具名称：", message.name)
            print("工具返回：", message.content)

    print("\n========== Agent 最终回答 ==========")
    print(result["messages"][-1].content)
