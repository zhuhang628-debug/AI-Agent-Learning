
import os
import time
import asyncio
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


# ==============================
# 1. 初始化环境
# ==============================

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR.parent / ".env")

api_key = os.getenv("DEEPSEEK_API_KEY")

if not api_key:
    raise ValueError("没有读取到 DEEPSEEK_API_KEY")


# ==============================
# 2. 初始化模型
# ==============================

llm = ChatOpenAI(
    model="deepseek-chat",
    api_key=api_key,
    base_url="https://api.deepseek.com/v1",
    temperature=0,
    timeout=5,
    max_retries=0
)


# ==============================
# 3. 测试 LLM Timeout
# ==============================

def test_llm_timeout():

    print("\n========== LLM Timeout 测试 ==========")

    try:
        result = llm.invoke(
            "请用一句话解释什么是 AI Agent。"
        )

        print("模型回答：")
        print(result.content)

    except Exception as e:
        print("模型调用失败：", type(e).__name__, str(e))


# ==============================
# 4. 模拟耗时工具
# ==============================

async def slow_tool():

    print("工具开始执行，预计需要 10 秒...")

    await asyncio.sleep(10)

    return "工具执行成功"


# ==============================
# 5. 测试 Tool Timeout
# ==============================

async def test_tool_timeout():

    print("\n========== Tool Timeout 测试 ==========")

    try:

        result = await asyncio.wait_for(
            slow_tool(),
            timeout=3
        )

        print("工具结果：", result)

    except asyncio.TimeoutError:

        print("工具执行超时！超过 3 秒，停止等待。")


# ==============================
# 6. 主程序
# ==============================

async def main():

    # 测试模型 API 超时
    test_llm_timeout()

    # 测试工具执行超时
    await test_tool_timeout()


if __name__ == "__main__":
    asyncio.run(main())
