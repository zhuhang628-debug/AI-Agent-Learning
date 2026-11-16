
import os
import logging
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)

from openai import (
    APITimeoutError,
    APIConnectionError,
    RateLimitError,
    InternalServerError
)


# ==============================
# 1. 初始化环境
# ==============================

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR.parent / ".env")

api_key = os.getenv("DEEPSEEK_API_KEY")

if not api_key:
    raise ValueError("没有读取到 DEEPSEEK_API_KEY")


# ==============================
# 2. 配置日志
# ==============================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


# ==============================
# 3. 初始化模型
# ==============================

llm = ChatOpenAI(
    model="deepseek-chat",
    api_key=api_key,
    base_url="https://api.deepseek.com/v1",
    temperature=0,
    timeout=10,
    max_retries=0
)


# ==============================
# 4. 配置自动重试
# ==============================

@retry(
    stop=stop_after_attempt(3),

    wait=wait_exponential(
        multiplier=1,
        min=1,
        max=4
    ),

    retry=retry_if_exception_type((
        APITimeoutError,
        APIConnectionError,
        RateLimitError,
        InternalServerError
    )),

    before_sleep=before_sleep_log(
        logger,
        logging.WARNING
    ),

    reraise=True
)
def call_llm(question: str):

    logger.info("开始调用 DeepSeek API")

    response = llm.invoke(question)

    return response.content


# ==============================
# 6. 模拟异常，测试 Retry
# ==============================

from openai import APIConnectionError

test_count = 0


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=4),
    retry=retry_if_exception_type(APIConnectionError),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True
)
def test_retry():

    global test_count
    test_count += 1

    logger.info(f"模拟调用，第 {test_count} 次")

    if test_count < 3:
        raise APIConnectionError(
            request=None
        )

    return "第三次调用成功！"



# ==============================
# 5. 主程序
# ==============================

def main():
    # 在 main() 中临时加入：
    print("\n========== Retry 模拟测试 ==========")
    print(test_retry())

    question = "请用简单的语言解释什么是 AI Agent。"

    try:

        result = call_llm(question)

        print("\n========== 模型回答 ==========")
        print(result)

    except Exception as e:

        logger.exception("模型调用最终失败")

        print("\n模型调用失败：", str(e))


if __name__ == "__main__":
    main()
