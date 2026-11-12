
import os
import sys
import asyncio
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient

from skill_loader import load_skill


# ==============================
# 1. 路径配置
# ==============================

BASE_DIR = Path(__file__).resolve().parent

# 加载项目根目录下的 .env
load_dotenv(BASE_DIR.parent / ".env")

# MCP Server 文件路径
MCP_SERVER_SCRIPT = (
    BASE_DIR.parent
    / "day19_MCP_Server"
    / "order_mcp_server.py"
)

# 当前 Python 解释器
PYTHON_EXE = Path(sys.executable)


# ==============================
# 2. 初始化模型
# ==============================

api_key = os.getenv("DEEPSEEK_API_KEY")

if not api_key:
    raise ValueError("没有找到 DEEPSEEK_API_KEY")

llm = ChatOpenAI(
    model="deepseek-chat",
    api_key=api_key,
    base_url="https://api.deepseek.com/v1",
    temperature=0
)


# ==============================
# 3. 主程序
# ==============================

async def main():

    # 检查 MCP Server 文件
    if not MCP_SERVER_SCRIPT.is_file():
        raise FileNotFoundError(
            f"没有找到 MCP Server：{MCP_SERVER_SCRIPT}"
        )

    # 连接 MCP Server
    mcp_client = MultiServerMCPClient({
        "order_mcp_server": {
            "transport": "stdio",
            "command": str(PYTHON_EXE),
            "args": [str(MCP_SERVER_SCRIPT)]
        }
    })

    # 获取 MCP Server 提供的工具
    mcp_tools = await mcp_client.get_tools()

    print("=== MCP 工具列表 ===")
    for item in mcp_tools:
        print(item.name)

    # 组合 Skill 加载工具和 MCP 工具
    tools = [load_skill] + mcp_tools

    print("\n=== Agent 可用工具 ===")
    for item in tools:
        print(item.name)

    # 创建 Agent
    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt="""
你是一个具备 Skill 和 MCP 工具调用能力的订单分析 Agent。

工作规则：

1. 用户要求分析订单时，先调用 load_skill，
   加载 order-analysis Skill。

2. 阅读 Skill 中的分析步骤、异常判断规则
   和输出要求。

3. 如果用户提供了订单编号，
   使用 MCP 提供的 query_order 工具查询真实订单。

4. 根据实际查询结果进行分析，
   不允许编造订单数据。

5. 如果订单查询失败或数据不足，
   明确说明原因。

6. 按照 Skill 的输出要求组织分析结果。

7. 普通闲聊不需要加载 Skill，也不需要调用 MCP 工具。
"""
    )

    # 接收用户输入
    question = input("\n请输入你的问题：")

    # 执行 Agent
    result = await agent.ainvoke({
        "messages": [
            {"role": "user", "content": question}
        ]
    })

    # ==============================
    # 4. 输出工具调用记录
    # ==============================

    print("\n========== 工具调用记录 ==========")

    for message in result["messages"]:

        # 查看模型发起的工具调用
        if message.type == "ai" and message.tool_calls:
            for call in message.tool_calls:
                print(
                    f"调用工具：{call['name']}"
                )
                print(
                    f"调用参数：{call['args']}"
                )

        # 查看工具返回结果
        elif message.type == "tool":
            print(f"工具名称：{message.name}")
            print(f"返回结果：{message.content}")

    # ==============================
    # 5. 输出最终回答
    # ==============================

    print("\n========== Agent 最终回答 ==========")

    for message in reversed(result["messages"]):
        if message.type == "ai" and message.content:
            print(message.content)
            break


if __name__ == "__main__":
    asyncio.run(main())
