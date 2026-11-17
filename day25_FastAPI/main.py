
import os
import sys
import asyncio
import logging
import time

from pathlib import Path
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from openai import (
    APIConnectionError,
    APITimeoutError,
    RateLimitError,
    InternalServerError
)

from tenacity import (
    AsyncRetrying,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)

from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient


# =================================
# 1. 项目路径和环境变量
# =================================

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent

load_dotenv(PROJECT_DIR / ".env")

API_KEY = os.getenv("DEEPSEEK_API_KEY")

if not API_KEY:
    raise ValueError("未读取到 DEEPSEEK_API_KEY")

PYTHON_EXE = PROJECT_DIR / "venv" / "Scripts" / "python.exe"

MCP_SERVER_SCRIPT = (
    PROJECT_DIR / "day19_MCP_Server" / "order_mcp_server.py"
)

if not PYTHON_EXE.exists():
    raise FileNotFoundError(f"Python 环境不存在：{PYTHON_EXE}")

if not MCP_SERVER_SCRIPT.exists():
    raise FileNotFoundError(f"MCP Server 不存在：{MCP_SERVER_SCRIPT}")


# =================================
# 2. 日志配置
# =================================

LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

logger = logging.getLogger("FastAPI-Agent")
logger.setLevel(logging.INFO)
logger.handlers.clear()

formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s"
)

file_handler = logging.FileHandler(
    LOG_DIR / "agent.log",
    encoding="utf-8"
)

console_handler = logging.StreamHandler(sys.stderr)

file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)

logger.propagate = False


# =================================
# 3. 初始化 DeepSeek 模型
# =================================

llm = ChatOpenAI(
    model="deepseek-chat",
    api_key=API_KEY,
    base_url="https://api.deepseek.com/v1",
    temperature=0,
    timeout=15,
    max_retries=0
)


# =================================
# 4. MCP Client 配置
# =================================

mcp_client = MultiServerMCPClient({
    "order_mcp_server": {
        "transport": "stdio",
        "command": str(PYTHON_EXE),
        "args": [str(MCP_SERVER_SCRIPT)]
    }
})


# =================================
# 5. 创建 Agent
# =================================

def create_reliability_agent(tools):

    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt="""
你是一个可靠的订单管理 Agent。

你可以使用以下工具：
1. query_order：查询订单信息。
2. calculate_order：计算订单金额。

工作规则：
1. 查询订单时必须调用 query_order，不允许编造订单数据。
2. 只能根据工具返回结果回答订单问题。
3. 如果工具提示权限不足，必须明确告知用户无权访问。
4. 如果订单不存在，如实告知用户。
5. 计算订单金额时必须调用 calculate_order。
6. 普通知识问题可以直接回答，不需要调用订单工具。
7. 使用中文回答，表达简洁准确。
"""
    )

    return agent


# =================================
# 6. 提取 Agent 最终回答
# =================================

def extract_answer(result):

    messages = result.get("messages", [])

    if not messages:
        return "Agent 没有返回消息。"

    content = messages[-1].content

    if isinstance(content, str):
        return content

    if isinstance(content, list):

        parts = []

        for item in content:

            if isinstance(item, dict) and item.get("type") == "text":
                parts.append(item.get("text", ""))

            else:
                parts.append(str(item))

        return "\n".join(parts)

    return str(content)


# =================================
# 7. Agent Retry + Timeout
# =================================

async def invoke_agent_with_reliability(agent, question):

    retry_controller = AsyncRetrying(
        stop=stop_after_attempt(3),

        wait=wait_exponential(
            multiplier=1,
            min=1,
            max=4
        ),

        retry=retry_if_exception_type((
            APIConnectionError,
            APITimeoutError,
            RateLimitError,
            InternalServerError
        )),

        before_sleep=before_sleep_log(
            logger,
            logging.WARNING
        ),

        reraise=True
    )

    async for attempt in retry_controller:

        with attempt:

            result = await asyncio.wait_for(
                agent.ainvoke({
                    "messages": [
                        {
                            "role": "user",
                            "content": question
                        }
                    ]
                }),
                timeout=60
            )

            return result


# =================================
# 8. FastAPI 生命周期管理
# =================================

@asynccontextmanager
async def lifespan(app: FastAPI):

    logger.info("FastAPI 服务启动")

    try:

        logger.info("开始加载 MCP 工具")

        tools = await asyncio.wait_for(
            mcp_client.get_tools(),
            timeout=15
        )

        logger.info("成功加载 %s 个 MCP 工具", len(tools))

        for tool in tools:
            logger.info("加载工具：%s", tool.name)

        app.state.agent = create_reliability_agent(tools)

        logger.info("Agent 创建成功")

        yield

    except Exception:

        logger.exception("FastAPI 初始化失败")
        raise

    finally:

        app.state.agent = None

        logger.info("FastAPI 服务关闭")


# =================================
# 9. 创建 FastAPI 应用
# =================================

app = FastAPI(
    title="AI Agent API",
    description="FastAPI + DeepSeek + MCP 订单 Agent",
    version="2.0.0",
    lifespan=lifespan
)


# =================================
# 10. 请求和响应模型
# =================================

class ChatRequest(BaseModel):

    message: str = Field(
        min_length=1,
        max_length=2000,
        description="用户输入的问题"
    )


class ChatResponse(BaseModel):

    answer: str


# =================================
# 11. 健康检查接口
# =================================

@app.get("/health")
async def health_check():

    return {
        "status": "ok",
        "message": "AI Agent API 服务运行正常"
    }


# =================================
# 12. 普通 DeepSeek 对话接口
# =================================

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):

    try:

        logger.info("普通聊天请求：%s", request.message)

        response = await llm.ainvoke(request.message)

        return ChatResponse(
            answer=response.content
        )

    except Exception:

        logger.exception("普通聊天接口执行失败")

        raise HTTPException(
            status_code=500,
            detail="AI 服务暂时不可用"
        )


# =================================
# 13. 完整 Agent 对话接口
# =================================

@app.post("/agent/chat", response_model=ChatResponse)
async def agent_chat(
    request: ChatRequest
):

    agent = getattr(
        app.state,
        "agent",
        None
    )

    if agent is None:

        raise HTTPException(
            status_code=503,
            detail="Agent 尚未初始化"
        )

    start_time = time.perf_counter()

    try:

        logger.info(
            "收到 Agent 请求：%s",
            request.message
        )

        result = await invoke_agent_with_reliability(
            agent,
            request.message
        )

        answer = extract_answer(result)

        elapsed = time.perf_counter() - start_time

        logger.info(
            "Agent 执行成功，耗时 %.2f 秒",
            elapsed
        )

        return ChatResponse(
            answer=answer
        )

    except asyncio.TimeoutError:

        logger.error("Agent 执行超时")

        raise HTTPException(
            status_code=504,
            detail="Agent 执行超时，请稍后重试"
        )

    except (
        APIConnectionError,
        APITimeoutError,
        RateLimitError,
        InternalServerError
    ):

        logger.exception("模型 API 请求失败")

        raise HTTPException(
            status_code=503,
            detail="模型服务暂时不可用"
        )

    except Exception:

        logger.exception("Agent 执行失败")

        raise HTTPException(
            status_code=500,
            detail="Agent 执行失败，请检查服务日志"
        )
