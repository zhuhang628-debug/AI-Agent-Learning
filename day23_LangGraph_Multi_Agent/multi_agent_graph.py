
import os
import re
import asyncio
from pathlib import Path
from typing import TypedDict

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.graph import StateGraph, START, END


# ==========================================
# 1. 环境配置
# ==========================================

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent

load_dotenv(PROJECT_ROOT / ".env")

PYTHON_EXE = PROJECT_ROOT / "venv" / "Scripts" / "python.exe"

MCP_SERVER_SCRIPT = (
    PROJECT_ROOT
    / "day19_MCP_Server"
    / "order_mcp_server.py"
)


# ==========================================
# 2. 初始化 DeepSeek
# ==========================================

api_key = os.getenv("DEEPSEEK_API_KEY")

if not api_key:
    raise ValueError("没有读取到 DEEPSEEK_API_KEY")

llm = ChatOpenAI(
    model="deepseek-chat",
    api_key=api_key,
    base_url="https://api.deepseek.com/v1",
    temperature=0
)


# ==========================================
# 3. 初始化 MCP Client
# ==========================================

mcp_client = MultiServerMCPClient({
    "order_mcp_server": {
        "transport": "stdio",
        "command": str(PYTHON_EXE),
        "args": [str(MCP_SERVER_SCRIPT)]
    }
})


# ==========================================
# 4. 定义共享 State
# ==========================================

class AgentState(TypedDict):
    task: str
    order_data: str
    analysis_result: str
    status: str


# ==========================================
# 5. MCP 工具
# ==========================================

query_order_tool = None


# ==========================================
# 6. 提取工具结果
# ==========================================

def extract_tool_result(result) -> str:

    if isinstance(result, str):
        return result

    if isinstance(result, list):
        contents = []

        for item in result:
            if isinstance(item, dict):
                if item.get("type") == "text":
                    contents.append(item.get("text", ""))
                else:
                    contents.append(str(item))
            else:
                contents.append(str(item))

        return "\n".join(contents)

    return str(result)


# ==========================================
# 7. Order Agent
# ==========================================

async def order_agent(state: AgentState):

    print("\n========== Order Agent ==========")

    task = state["task"]

    match = re.search(r"\b[A-Za-z]\d+\b", task)

    if not match:
        print("没有识别到订单编号")

        return {
            "order_data": "没有识别到有效的订单编号",
            "status": "failed"
        }

    order_no = match.group(0)

    print(f"识别到订单编号：{order_no}")

    try:
        print("正在调用 MCP query_order...")

        result = await query_order_tool.ainvoke({
            "order_no": order_no
        })

        order_data = extract_tool_result(result)

        print("订单查询结果：")
        print(order_data)

        # 检查查询结果是否包含有效订单
        if (
            "没有找到订单" in order_data
            or "不存在" in order_data
            or "查询失败" in order_data
            or not order_data.strip()
        ):
            return {
                "order_data": order_data,
                "status": "failed"
            }

        return {
            "order_data": order_data,
            "status": "success"
        }

    except Exception as e:

        print("订单查询发生异常：", str(e))

        return {
            "order_data": f"订单查询异常：{str(e)}",
            "status": "failed"
        }


# ==========================================
# 8. 条件路由函数
# ==========================================

def route_order(state: AgentState):

    print("\n========== Conditional Router ==========")

    if state["status"] == "success":
        print("订单查询成功，进入 Analysis Agent")
        return "success"

    print("订单查询失败，进入 Error Agent")
    return "failed"


# ==========================================
# 9. Analysis Agent
# ==========================================

async def analysis_agent(state: AgentState):

    print("\n========== Analysis Agent ==========")

    order_data = state["order_data"]

    response = await llm.ainvoke(
        f"""
        你是订单数据分析专家。

        请分析以下真实订单数据：

        {order_data}

        请输出：
        1. 订单基本信息
        2. 订单金额
        3. 订单状态
        4. 数据完整性
        5. 是否存在异常
        6. 分析总结

        不允许编造数据。
        """
    )

    return {
        "analysis_result": response.content
    }


# ==========================================
# 10. Error Agent
# ==========================================

async def error_agent(state: AgentState):

    print("\n========== Error Agent ==========")

    error_message = state["order_data"]

    response = await llm.ainvoke(
        f"""
        你是订单查询异常处理助手。

        以下是订单查询失败信息：

        {error_message}

        请向用户说明：
        1. 本次查询未成功
        2. 可能的原因
        3. 建议用户下一步如何处理

        不要编造订单信息。
        """
    )

    return {
        "analysis_result": response.content
    }


# ==========================================
# 11. 构建 LangGraph
# ==========================================

builder = StateGraph(AgentState)

builder.add_node("order_agent", order_agent)
builder.add_node("analysis_agent", analysis_agent)
builder.add_node("error_agent", error_agent)

builder.add_edge(START, "order_agent")

# 根据订单查询结果进行动态路由
builder.add_conditional_edges(
    "order_agent",
    route_order,
    {
        "success": "analysis_agent",
        "failed": "error_agent"
    }
)

builder.add_edge("analysis_agent", END)
builder.add_edge("error_agent", END)

graph = builder.compile()


# ==========================================
# 12. 执行工作流
# ==========================================


async def main():

    global query_order_tool

    print("正在连接 MCP Server...")

    tools = await mcp_client.get_tools()

    print("\n发现的 MCP 工具：")

    for tool in tools:
        print("-", tool.name)

    query_order_tool = next(
        (tool for tool in tools if tool.name == "query_order"),
        None
    )

    if query_order_tool is None:
        raise RuntimeError("没有找到 query_order 工具")

    print("\nMCP 初始化成功！")

    # 循环接收用户输入
    while True:

        question = input(
            "\n请输入你的问题（输入 exit 退出）："
        ).strip()

        if question.lower() in ["exit", "quit", "退出"]:
            print("程序已退出")
            break

        if not question:
            print("问题不能为空，请重新输入")
            continue

        # 执行 LangGraph 工作流
        result = await graph.ainvoke({
            "task": question,
            "order_data": "",
            "analysis_result": "",
            "status": ""
        })

        print("\n========== 最终结果 ==========")
        print(result["analysis_result"])


if __name__ == "__main__":
    asyncio.run(main())

