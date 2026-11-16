import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")
# ==============================
# 1. 导入依赖
# ==============================

import os  # 读取系统环境变量，例如 API Key。
import sys  # 访问标准错误输出，用于设置日志编码。
import asyncio  # 提供异步运行和超时控制。
import logging  # 记录 Agent 运行日志。
import time  # 计算每次任务的执行耗时。
from pathlib import Path  # 处理项目文件路径。

from dotenv import load_dotenv  # 从 .env 文件读取配置。
from openai import (  # 导入 OpenAI SDK 定义的 API 异常类型。
    APIConnectionError,  # API 网络连接异常。
    APITimeoutError,  # API 请求超时异常。
    RateLimitError,  # API 请求频率限制异常。
    InternalServerError  # API 服务端内部错误。
)

from tenacity import (  # 导入自动重试相关组件。
    AsyncRetrying,  # 异步重试控制器。
    stop_after_attempt,  # 设置最大尝试次数。
    wait_exponential,  # 设置指数退避等待时间。
    retry_if_exception_type,  # 根据异常类型决定是否重试。
    before_sleep_log  # 每次重试前记录日志。
)

from langchain_openai import ChatOpenAI  # 创建兼容 OpenAI 接口的聊天模型。
from langchain.agents import create_agent  # LangChain 1.x 创建 Agent 的接口。
from langchain_mcp_adapters.client import MultiServerMCPClient  # 连接 MCP Server。


# ==============================
# 2. 项目路径和环境变量
# ==============================

BASE_DIR = Path(__file__).resolve().parent  # 获取当前 reliability_agent.py 所在目录。
PROJECT_DIR = BASE_DIR.parent  # 获取整个 AI-Agent-Learning 项目根目录。

load_dotenv(PROJECT_DIR / ".env")  # 加载项目根目录中的 .env 配置文件。

API_KEY = os.getenv("DEEPSEEK_API_KEY")  # 从环境变量读取 DeepSeek API Key。

if not API_KEY:  # 检查 API Key 是否成功读取。
    raise ValueError("未读取到 DEEPSEEK_API_KEY，请检查 .env 文件。")  # 缺少密钥时停止程序。

PYTHON_EXE = PROJECT_DIR / "venv" / "Scripts" / "python.exe"  # 指定项目虚拟环境的 Python。
MCP_SERVER_SCRIPT = PROJECT_DIR / "day19_MCP_Server" / "order_mcp_server.py"  # 指定订单 MCP Server 文件。

if not PYTHON_EXE.exists():  # 检查虚拟环境 Python 是否存在。
    raise FileNotFoundError(f"Python 环境不存在：{PYTHON_EXE}")  # 路径错误时给出提示。

if not MCP_SERVER_SCRIPT.exists():  # 检查 MCP Server 文件是否存在。
    raise FileNotFoundError(f"MCP Server 不存在：{MCP_SERVER_SCRIPT}")  # 文件缺失时停止程序。


# ==============================
# 3. 日志配置
# ==============================

LOG_DIR = BASE_DIR / "logs"  # 设置日志文件夹路径。
LOG_DIR.mkdir(exist_ok=True)  # 如果 logs 文件夹不存在，就自动创建。

LOG_FILE = LOG_DIR / "agent.log"  # 设置日志文件完整路径。

if hasattr(sys.stderr, "reconfigure"):  # 判断当前 Python 是否支持重新配置终端编码。
    sys.stderr.reconfigure(encoding="utf-8")  # 使用 UTF-8 输出错误日志，减少中文乱码。

logger = logging.getLogger("ReliabilityAgent")  # 创建当前 Agent 专用日志记录器。
logger.setLevel(logging.INFO)  # 设置日志级别，记录 INFO 及以上级别的信息。
logger.handlers.clear()  # 清除旧处理器，防止重复运行时重复输出日志。

formatter = logging.Formatter(  # 定义日志格式。
    "%(asctime)s - %(levelname)s - %(message)s"  # 包含时间、日志级别和具体内容。
)

file_handler = logging.FileHandler(  # 创建文件日志处理器。
    LOG_FILE,  # 指定日志文件。
    encoding="utf-8"  # 文件使用 UTF-8 编码。
)
file_handler.setFormatter(formatter)  # 将统一日志格式应用到文件处理器。

console_handler = logging.StreamHandler(sys.stderr)  # 创建控制台日志处理器，输出到标准错误流。
console_handler.setFormatter(formatter)  # 将统一日志格式应用到控制台处理器。

logger.addHandler(file_handler)  # 将文件处理器添加到日志记录器。
logger.addHandler(console_handler)  # 将控制台处理器添加到日志记录器。
logger.propagate = False  # 阻止日志向根记录器传播，避免重复输出。


# ==============================
# 4. 初始化 DeepSeek 模型
# ==============================

llm = ChatOpenAI(  # 创建 LangChain 聊天模型。
    model="deepseek-chat",  # 指定 DeepSeek 对话模型。
    api_key=API_KEY,  # 使用前面读取的 API Key。
    base_url="https://api.deepseek.com/v1",  # 指定 DeepSeek API 地址。
    temperature=0,  # 降低回答随机性。
    timeout=15,  # 单次模型 API 请求最多等待15秒。
    max_retries=0  # 关闭模型客户端内部重试，避免与 Tenacity 重试叠加。
)


# ==============================
# 5. 配置 MCP Client
# ==============================

mcp_client = MultiServerMCPClient({  # 创建 MCP 客户端，可以连接多个 MCP Server。
    "order_mcp_server": {  # 为订单 MCP Server 设置名称。
        "transport": "stdio",  # 使用标准输入输出进行进程间通信。
        "command": str(PYTHON_EXE),  # 使用项目虚拟环境中的 Python 启动 Server。
        "args": [str(MCP_SERVER_SCRIPT)]  # 将 MCP Server 脚本路径作为启动参数。
    }
})


# ==============================
# 6. 创建 Agent
# ==============================

def create_reliability_agent(tools):  # 定义创建可靠性 Agent 的函数。

    agent = create_agent(  # 使用 LangChain 1.x 创建 Agent。
        model=llm,  # 将 DeepSeek 模型交给 Agent。
        tools=tools,  # 将 MCP Client 获取到的工具交给 Agent。
        system_prompt="""  # 设置 Agent 的系统提示词。

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
"""  # 系统提示词结束。
    )

    return agent  # 返回创建好的 Agent 实例。


# ==============================
# 7. 提取 Agent 最终回答
# ==============================

def extract_answer(result):  # 定义回答提取函数，避免直接打印整个消息历史。

    messages = result.get("messages", [])  # 从 Agent 执行结果中获取消息列表。

    if not messages:  # 检查是否存在消息。
        return "Agent 没有返回消息。"  # 没有消息时返回提示。

    content = messages[-1].content  # 获取最后一条消息的正文内容。

    if isinstance(content, str):  # 判断正文是否为普通字符串。
        return content  # 如果是字符串，直接返回。

    if isinstance(content, list):  # 判断正文是否为多模态内容块列表。
        parts = []  # 创建列表，用于保存文本内容。

        for item in content:  # 遍历每一个内容块。
            if isinstance(item, dict) and item.get("type") == "text":  # 判断是否为文本内容块。
                parts.append(item.get("text", ""))  # 提取文本并加入列表。
            else:  # 如果不是普通文本块。
                parts.append(str(item))  # 转成字符串，避免内容丢失。

        return "\n".join(parts)  # 将多个内容块合并为一段文本。

    return str(content)  # 其他类型统一转换成字符串。


# ==============================
# 8. Retry + Timeout 核心执行函数
# ==============================

async def invoke_agent_with_reliability(agent, question):  # 定义带重试和超时控制的 Agent 执行函数。

    retry_controller = AsyncRetrying(  # 创建异步重试控制器。
        stop=stop_after_attempt(3),  # 最多尝试3次。
        wait=wait_exponential(  # 使用指数退避等待策略。
            multiplier=1,  # 设置等待时间基础倍数。
            min=1,  # 最短等待1秒。
            max=4  # 最长等待4秒。
        ),
        retry=retry_if_exception_type((  # 只对指定异常执行重试。
            APIConnectionError,  # 网络连接异常时重试。
            APITimeoutError,  # 模型 API 超时时重试。
            RateLimitError,  # API 限流时重试。
            InternalServerError  # 模型服务端错误时重试。
        )),
        before_sleep=before_sleep_log(logger, logging.WARNING),  # 重试前写入警告日志。
        reraise=True  # 重试次数耗尽后重新抛出最后一次异常。
    )

    async for attempt in retry_controller:  # 按照重试策略逐次执行。
        with attempt:  # 进入当前重试尝试的异常捕获上下文。

            result = await asyncio.wait_for(  # 给整个 Agent 任务增加超时限制。
                agent.ainvoke({  # 异步调用 Agent。
                    "messages": [  # 构造 Agent 所需的消息列表。
                        {"role": "user", "content": question}  # 将用户问题传给 Agent。
                    ]
                }),
                timeout=60  # 单次 Agent 任务最多等待60秒。
            )

            return result  # 成功执行后立即返回结果，不再继续重试。


# ==============================
# 9. 主程序
# ==============================

async def main():  # 定义异步主函数。

    print("=" * 50, flush=True)  # 输出程序标题分隔线。
    print("       Agent Reliability 综合项目", flush=True)  # 输出项目名称。
    print("=" * 50, flush=True)  # 输出程序标题分隔线。

    logger.info("Agent 程序启动")  # 记录程序启动日志。

    # ---------- 连接 MCP Server ----------

    print("\n[1/3] 正在连接 MCP Server...", flush=True)  # 提示正在连接 MCP Server。
    logger.info("开始加载 MCP 工具")  # 记录工具加载开始。

    try:  # 开始捕获 MCP 连接阶段的异常。

        tools = await asyncio.wait_for(  # 为 MCP 工具发现增加超时控制。
            mcp_client.get_tools(),  # 自动启动 MCP Server 并获取工具列表。
            timeout=15  # 最多等待15秒获取工具。
        )

        print("\nMCP 工具加载成功！", flush=True)  # 输出工具加载成功提示。
        logger.info("成功加载 %s 个 MCP 工具", len(tools))  # 记录工具数量。

        for tool in tools:  # 遍历已经加载的 MCP 工具。
            print(f"- {tool.name}: {tool.description}", flush=True)  # 输出工具名称和说明。

    except asyncio.TimeoutError:  # 捕获 MCP 连接超时。
        logger.exception("MCP 工具加载超时")  # 记录异常日志和堆栈。
        print("\nMCP 连接超时，请检查 Server 是否正常启动。")  # 提示用户检查 MCP。
        return  # 结束主程序。

    except Exception as e:  # 捕获其他 MCP 连接异常。
        logger.exception("MCP 工具加载失败")  # 记录异常日志和堆栈。
        print(f"\nMCP 连接失败：{type(e).__name__}: {e}")  # 输出异常类型和原因。
        return  # 结束主程序。

    # ---------- 创建 Agent ----------

    print("\n[2/3] 正在创建 Agent...", flush=True)  # 提示开始创建 Agent。
    agent = create_reliability_agent(tools)  # 将模型和 MCP 工具组合成 Agent。
    logger.info("Agent 创建成功")  # 记录 Agent 创建成功日志。
    print("Agent 创建成功！", flush=True)  # 输出创建成功提示。

    # ---------- 进入交互循环 ----------

    print("\n[3/3] Agent 已就绪，可以开始提问。", flush=True)  # 提示 Agent 已经准备就绪。
    print("输入 exit 或 quit 退出程序。", flush=True)  # 告知用户退出方式。

    while True:  # 持续接收用户输入。

        try:  # 捕获用户输入阶段的异常。

            question = input("\n请输入问题：").strip()  # 获取用户输入并去掉首尾空格。

            if question.lower() in ["exit", "quit", "退出"]:  # 判断用户是否要求退出。
                logger.info("用户主动退出程序")  # 记录退出日志。
                print("Agent 已退出。")  # 输出退出提示。
                break  # 结束循环。

            if not question:  # 判断用户是否输入了空内容。
                continue  # 空输入时重新等待提问。

            print("\nAgent 正在处理...", flush=True)  # 提示 Agent 开始处理任务。

            start_time = time.perf_counter()  # 记录本次任务开始时间。

            try:  # 捕获 Agent 执行阶段的异常。

                logger.info("收到用户问题：%s", question)  # 记录用户提出的问题。

                result = await invoke_agent_with_reliability(  # 调用包含 Retry 和 Timeout 的执行函数。
                    agent,  # 传入当前 Agent。
                    question  # 传入用户问题。
                )

                answer = extract_answer(result)  # 从 Agent 执行结果中提取最终回答。

                elapsed = time.perf_counter() - start_time  # 计算本次任务实际耗时。

                logger.info("任务执行成功，耗时 %.2f 秒", elapsed)  # 记录成功状态和耗时。

                print("\nAgent 回答：")  # 输出回答标题。
                print(answer)  # 输出 Agent 最终回答。
                print(f"\n本次任务耗时：{elapsed:.2f} 秒")  # 输出任务执行时间。

            except asyncio.TimeoutError:  # 捕获 Agent 整体执行超时。

                elapsed = time.perf_counter() - start_time  # 计算超时任务实际耗时。

                logger.error("Agent 执行超时，耗时 %.2f 秒", elapsed)  # 记录超时日志。

                print("\n任务执行超时，请缩短问题或稍后重试。")  # 向用户返回友好提示。

            except (  # 捕获模型 API 相关异常。
                APIConnectionError,  # 网络连接错误。
                APITimeoutError,  # API 请求超时。
                RateLimitError,  # API 请求限流。
                InternalServerError  # API 服务端错误。
            ) as e:  # 将异常对象保存到变量 e。

                logger.exception("模型 API 请求失败，重试已耗尽")  # 记录最终失败原因和堆栈。

                print(f"\n模型 API 请求失败：{type(e).__name__}: {e}")  # 向用户显示 API 错误。

            except Exception as e:  # 捕获其他未预料的执行异常。

                logger.exception("Agent 执行出现异常")  # 记录完整异常信息。

                print(f"\nAgent 执行失败：{type(e).__name__}: {e}")  # 输出错误类型和原因。

        except KeyboardInterrupt:  # 捕获用户按下 Ctrl+C 的情况。

            logger.info("用户通过 Ctrl+C 中断程序")  # 记录手动中断日志。

            print("\n程序已手动停止。")  # 输出程序停止提示。

            break  # 退出交互循环。


# ==============================
# 10. 程序入口
# ==============================

if __name__ == "__main__":  # 判断当前文件是否作为主程序运行。

    try:  # 捕获整个异步程序的异常。

        asyncio.run(main())  # 创建事件循环并运行异步主函数。

    except KeyboardInterrupt:  # 捕获程序启动或退出阶段的 Ctrl+C。

        print("\n程序已退出。")  # 输出最终退出提示。
