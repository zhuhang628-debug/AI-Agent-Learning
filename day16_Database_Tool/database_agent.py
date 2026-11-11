
import os
from pathlib import Path

import pymysql
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
# 2. 定义数据库查询参数
# ==============================

class OrderQueryInput(BaseModel):
    order_no: str = Field(
        description="需要查询的订单编号，例如 A1001"
    )


# ==============================
# 3. 封装数据库查询 Tool
# ==============================

@tool(args_schema=OrderQueryInput)
def query_order(order_no: str) -> str:
    """根据订单编号查询订单状态、金额和用户ID。只能查询订单，不允许修改数据。"""

    connection = None

    try:
        # 建立数据库连接
        connection = pymysql.connect(**MYSQL_CONFIG)

        # 创建游标并执行 SQL
        with connection.cursor() as cursor:
            sql = """
                SELECT order_no, status, amount, user_id
                FROM orders
                WHERE order_no = %s
            """

            # 参数化查询，避免 SQL 注入
            cursor.execute(sql, (order_no,))

            # 获取一条查询结果
            order = cursor.fetchone()

            if order is None:
                return f"没有找到订单编号为 {order_no} 的订单。"

            return (
                f"订单编号：{order['order_no']}\n"
                f"订单状态：{order['status']}\n"
                f"订单金额：{order['amount']:.2f} 元\n"
                f"用户ID：{order['user_id']}"
            )

    except pymysql.MySQLError as e:
        return f"数据库查询失败，请检查数据库连接或查询配置。错误类型：{type(e).__name__}"

    finally:
        # 无论查询成功还是失败，都关闭数据库连接
        if connection is not None:
            connection.close()


# ==============================
# 4. 初始化 DeepSeek 模型
# ==============================

api_key = os.getenv("DEEPSEEK_API_KEY")

if not api_key:
    raise ValueError("未找到 DEEPSEEK_API_KEY，请检查项目根目录下的 .env 文件")

llm = ChatOpenAI(
    model="deepseek-chat",
    api_key=api_key,
    base_url="https://api.deepseek.com/v1",
    temperature=0
)


# ==============================
# 5. 创建 Agent
# ==============================

tools = [query_order]

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt="""
    你是一个订单查询助手。

    当用户询问具体订单信息时，必须调用 query_order 工具查询数据库。
    根据工具返回的真实数据回答用户。
    不允许编造订单信息。
    如果订单不存在，明确告诉用户没有找到对应订单。
    普通闲聊不需要调用数据库工具。
    """
)


# ==============================
# 6. 运行 Agent
# ==============================

if __name__ == "__main__":

    question = input("请输入你的问题：")

    result = agent.invoke({
        "messages": [
            {"role": "user", "content": question}
        ]
    })

    print("\n========== Agent 回答 ==========")
    # print(result["messages"][-1].content)
    print("\n========== Agent 执行过程 ==========")

    for message in result["messages"]:

        print(f"\n消息类型：{message.type}")

        # 查看模型发起的工具调用
        if hasattr(message, "tool_calls") and message.tool_calls:
            print("工具调用：")
            for tool_call in message.tool_calls:
                print(tool_call)

        # 查看工具执行结果
        if message.type == "tool":
            print("工具名称：", message.name)
            print("工具返回：", message.content)

    print("\n========== Agent 最终回答 ==========")
    print(result["messages"][-1].content)