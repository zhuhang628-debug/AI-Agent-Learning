
import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent


# =========================
# 1. 加载环境变量
# =========================

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR.parent / ".env")

api_key = os.getenv("DEEPSEEK_API_KEY")

if not api_key:
    raise ValueError("没有找到 DEEPSEEK_API_KEY，请检查 .env 文件")


# =========================
# 2. 定义工具参数 Schema
# =========================

class OrderInput(BaseModel):
    price: float = Field(
        gt=0,
        description="商品单价，必须大于0"
    )

    quantity: int = Field(
        gt=0,
        description="购买数量，必须是正整数"
    )

    discount: float = Field(
        ge=0,
        le=1,
        description="折扣比例，0表示不打折，0.2表示打八折"
    )


# =========================
# 3. 定义工具一：订单金额计算
# =========================

@tool(args_schema=OrderInput)
def calculate_order(
    price: float,
    quantity: int,
    discount: float
) -> str:
    """计算商品订单的折后总价。适用于用户询问商品总价、订单金额或折扣计算。"""

    try:
        total = price * quantity * (1 - discount)

        return (
            f"订单计算成功："
            f"单价={price}，"
            f"数量={quantity}，"
            f"折扣={discount * 100:.0f}%，"
            f"折后总价={total:.2f}元"
        )

    except Exception as e:
        return f"订单计算失败：{str(e)}"


# =========================
# 4. 定义工具二：订单查询
# =========================

@tool
def lookup_order(order_id: str) -> str:
    """根据订单编号查询订单状态和订单金额。适用于用户询问订单进度、订单状态或订单详情。"""

    # 模拟订单数据库
    orders = {
        "A1001": {
            "status": "已发货",
            "amount": 199.00
        },
        "A1002": {
            "status": "待付款",
            "amount": 299.00
        },
        "A1003": {
            "status": "已完成",
            "amount": 599.00
        }
    }

    try:
        order = orders.get(order_id)

        if order is None:
            return f"没有找到订单编号为 {order_id} 的订单。"

        return (
            f"订单编号：{order_id}，"
            f"订单状态：{order['status']}，"
            f"订单金额：{order['amount']:.2f}元"
        )

    except Exception as e:
        return f"订单查询失败：{str(e)}"


# =========================
# 5. 初始化 LLM
# =========================

llm = ChatOpenAI(
    model="deepseek-chat",
    api_key=api_key,
    base_url="https://api.deepseek.com/v1",
    temperature=0
)


# =========================
# 6. 创建 Agent
# =========================

tools = [
    calculate_order,
    lookup_order
]

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt="""
你是一个业务订单助手。

规则：
1. 用户询问订单金额计算时，调用 calculate_order。
2. 用户询问具体订单状态时，调用 lookup_order。
3. 如果用户同时提出多个需求，可以根据需要调用多个工具。
4. 必须依据工具返回结果回答，不得编造订单信息。
5. 如果工具返回没有找到订单，应如实告知用户。
6. 普通闲聊不需要调用工具。
"""
)


# =========================
# 7. 交互测试
# =========================

if __name__ == "__main__":

    while True:

        question = input("\n请输入问题（输入 q 退出）：").strip()

        if question.lower() == "q":
            break

        if not question:
            continue

        try:
            result = agent.invoke({
                "messages": [
                    {
                        "role": "user",
                        "content": question
                    }
                ]
            })

            print("\n========== 执行过程 ==========")

            for message in result["messages"]:

                print(f"\n消息类型：{message.type}")

                if getattr(message, "tool_calls", None):
                    print("工具调用：", message.tool_calls)

                if message.type == "tool":
                    print("工具名称：", message.name)
                    print("工具结果：", message.content)

            print("\n========== 最终回答 ==========")
            print(result["messages"][-1].content)

        except Exception as e:
            print(f"Agent 执行失败：{e}")
