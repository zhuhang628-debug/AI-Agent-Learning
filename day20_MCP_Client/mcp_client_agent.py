
import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv

from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient


# =====================================
# 1. 加载环境变量
# =====================================

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR.parent / ".env")

api_key = os.getenv("DEEPSEEK_API_KEY")

if not api_key:
    raise ValueError("未找到 DEEPSEEK_API_KEY")


# =====================================
# 2. 初始化 DeepSeek
# =====================================

llm = ChatOpenAI(
    model="deepseek-chat",
    api_key=api_key,
    base_url="https://api.deepseek.com/v1",
    temperature=0
)


# =====================================
# 3. 配置 MCP Server
# =====================================

MCP_SERVER_SCRIPT = (
    BASE_DIR.parent
    / "day19_MCP_Server"
    / "order_mcp_server.py"
)

PYTHON_EXE = (
    BASE_DIR.parent
    / "venv"
    / "Scripts"
    / "python.exe"
)

mcp_client = MultiServerMCPClient(
    {
        "order_mcp_server": {
            "transport": "stdio",
            "command": str(PYTHON_EXE),
            "args": [str(MCP_SERVER_SCRIPT)]
        }
    }
)


# =====================================
# 4. 异步主程序
# =====================================

async def main():

    # 动态发现 MCP Server 提供的工具
    tools = await mcp_client.get_tools()

    print("\n========== MCP 工具发现结果 ==========")

    for tool in tools:
        print(f"工具名称：{tool.name}")
        print(f"工具描述：{tool.description}")

    # 将 MCP 工具交给 LangChain Agent
    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt="""
        你是一个企业订单助手。

        用户询问订单信息时，调用 query_order 工具。
        用户要求计算订单金额时，调用 calculate_order 工具。
        必须根据工具返回的结果回答，不允许编造数据。
        普通闲聊不需要调用工具。
        """
    )

    # 持续接收用户问题
    while True:

        question = input("\n请输入问题（输入 q 退出）：").strip()

        if question.lower() == "q":
            break

        if not question:
            continue

        result = await agent.ainvoke(
            {
                "messages": [
                    {"role": "user", "content": question}
                ]
            }
        )

        print("\n========== Agent 执行过程 ==========")

        for message in result["messages"]:

            print(f"\n消息类型：{message.type}")

            if getattr(message, "tool_calls", None):
                print("工具调用：", message.tool_calls)

            if message.type == "tool":
                print("工具名称：", message.name)
                print("工具返回：", message.content)

        print("\n========== Agent 最终回答 ==========")
        print(result["messages"][-1].content)


# =====================================
# 5. 启动程序
# =====================================

if __name__ == "__main__":
    asyncio.run(main())
