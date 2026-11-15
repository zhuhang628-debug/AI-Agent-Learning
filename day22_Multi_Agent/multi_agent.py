
import os
import sys
import asyncio
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_mcp_adapters.client import MultiServerMCPClient


# ==========================================
# 1. 路径和环境配置
# ==========================================

BASE_DIR = Path(__file__).resolve().parent

# 加载项目根目录下的 .env
load_dotenv(BASE_DIR.parent / ".env")

# Day19 MCP Server 路径
MCP_SERVER_SCRIPT = (
    BASE_DIR.parent
    / "day19_MCP_Server"
    / "order_mcp_server.py"
)

# 当前 Python 解释器
PYTHON_EXE = Path(sys.executable)


# ==========================================
# 2. 初始化大模型
# ==========================================

api_key = os.getenv("DEEPSEEK_API_KEY")

if not api_key:
    raise ValueError("没有找到 DEEPSEEK_API_KEY，请检查 .env 文件")

llm = ChatOpenAI(
    model="deepseek-chat",
    api_key=api_key,
    base_url="https://api.deepseek.com/v1",
    temperature=0
)


# ==========================================
# 3. 提取 Agent 最终回答
# ==========================================

def extract_answer(result):
    """
    从 Agent 的消息列表中提取最后一条有效 AI 回答。
    """

    for message in reversed(result["messages"]):

        if message.type == "ai" and message.content:

            # 兼容字符串和多模态内容列表
            if isinstance(message.content, str):
                return message.content

            return str(message.content)

    return "Agent 没有返回有效结果"


# ==========================================
# 4. 主程序
# ==========================================

async def main():

    # 检查 MCP Server 文件
    if not MCP_SERVER_SCRIPT.is_file():
        raise FileNotFoundError(
            f"没有找到 MCP Server：{MCP_SERVER_SCRIPT}"
        )

    # --------------------------------------
    # 4.1 连接 MCP Server
    # --------------------------------------

    mcp_client = MultiServerMCPClient({
        "order_mcp_server": {
            "transport": "stdio",
            "command": str(PYTHON_EXE),
            "args": [str(MCP_SERVER_SCRIPT)]
        }
    })

    # 获取 MCP Server 提供的工具
    mcp_tools = await mcp_client.get_tools()

    print("========== MCP 工具列表 ==========")

    for item in mcp_tools:
        print(item.name)

    # --------------------------------------
    # 4.2 创建 Order Agent
    # --------------------------------------

    order_agent = create_agent(
        model=llm,
        tools=mcp_tools,
        system_prompt="""
你是一名专业的订单查询 Agent。

你的职责：

1. 根据用户提供的订单编号查询订单。
2. 使用 query_order 工具获取真实订单数据。
3. 整理订单编号、订单状态、订单金额和用户 ID。
4. 不允许编造订单信息。
5. 如果没有提供订单编号，要求用户补充。
6. 只负责订单查询，不负责复杂的数据分析。
"""
    )

    print("\nOrder Agent 创建成功")

    # --------------------------------------
    # 4.3 创建 Analysis Agent
    # --------------------------------------

    analysis_agent = create_agent(
        model=llm,
        tools=[],
        system_prompt="""
你是一名专业的数据分析 Agent。

你的职责是分析其他 Agent 提供的订单数据。

分析要求：

1. 检查订单编号、订单金额和订单状态是否完整。
2. 统计订单数量和订单总金额。
3. 按订单状态分类统计。
4. 检查异常订单。

异常判断规则：

- 订单金额小于或等于 0：异常。
- 订单编号缺失：异常。
- 订单状态缺失：异常。
- 不允许仅凭订单金额较高就认定异常。

输出要求：

1. 订单基础信息。
2. 订单统计结果。
3. 异常检查结果。
4. 最终分析结论。

注意：

- 只能根据输入的真实数据进行分析。
- 不允许编造订单数据。
- 如果数据不足，明确说明原因。
- 只负责数据分析，不负责查询数据库。
"""
    )

    print("Analysis Agent 创建成功")

    # --------------------------------------
    # 4.4 将 Order Agent 封装为 Tool
    # --------------------------------------

    @tool
    async def order_specialist(task: str) -> str:
        """
        委托订单专家查询真实订单信息。
        输入订单编号或订单查询需求。
        """

        result = await order_agent.ainvoke({
            "messages": [
                {"role": "user", "content": task}
            ]
        })

        return extract_answer(result)

    # --------------------------------------
    # 4.5 将 Analysis Agent 封装为 Tool
    # --------------------------------------

    @tool
    async def analysis_specialist(data: str) -> str:
        """
        委托数据分析专家分析订单数据。
        输入已经获取的真实订单数据。
        """

        result = await analysis_agent.ainvoke({
            "messages": [
                {
                    "role": "user",
                    "content": f"请根据以下真实订单数据进行分析：\n{data}"
                }
            ]
        })

        return extract_answer(result)

    print("专业 Agent 已封装为 Tool")

    # --------------------------------------
    # 4.6 创建 Supervisor Agent
    # --------------------------------------

    supervisor = create_agent(
        model=llm,
        tools=[
            order_specialist,
            analysis_specialist
        ],
        system_prompt="""
你是一名订单业务主管 Agent，负责协调专业 Agent 完成用户任务。

你可以调用两个专业工具：

1. order_specialist：
   负责查询真实订单数据。

2. analysis_specialist：
   负责分析已经获取的订单数据。

工作规则：

1. 如果用户只要求查询订单，
   调用 order_specialist 即可。

2. 如果用户要求分析订单，
   必须先调用 order_specialist 获取真实数据，
   再将查询结果交给 analysis_specialist 分析。

3. 如果订单查询失败或没有获得有效订单数据，
   不要继续进行数据分析，也不能编造数据。

4. 如果用户只是普通闲聊，
   不需要调用专业 Agent。

5. 最后负责整理专业 Agent 的执行结果，
   向用户输出完整回答。

注意：
你负责协调任务，不要编造订单数据。
"""
    )

    print("Supervisor Agent 创建成功")

    # ======================================
    # 5. 执行用户任务
    # ======================================

    print("\n========== Multi-Agent 系统已启动 ==========")

    question = input("\n请输入你的任务：")

    result = await supervisor.ainvoke({
        "messages": [
            {"role": "user", "content": question}
        ]
    })

    # ======================================
    # 6. 输出工具调用记录
    # ======================================

    print("\n========== Multi-Agent 工具调用记录 ==========")

    for message in result["messages"]:

        # 模型发起的工具调用
        if message.type == "ai" and message.tool_calls:

            for call in message.tool_calls:

                print(f"\n调用工具：{call['name']}")
                print(f"调用参数：{call['args']}")

        # 工具返回结果
        elif message.type == "tool":

            print(f"\n工具名称：{message.name}")
            print(f"工具返回：{message.content}")

    # ======================================
    # 7. 输出最终结果
    # ======================================

    print("\n========== Supervisor 最终回答 ==========")

    print(extract_answer(result))


# ==========================================
# 8. 程序入口
# ==========================================

if __name__ == "__main__":
    asyncio.run(main())
