
import os
from pathlib import Path

import httpx
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
# 2. API 基础配置
# =========================

BASE_URL = "https://jsonplaceholder.typicode.com"

TIMEOUT = 10.0


# =========================
# 3. 定义 GET 工具参数
# =========================

class GetPostInput(BaseModel):

    post_id: int = Field(
        gt=0,
        description="文章ID，必须是正整数"
    )


# =========================
# 4. 定义 POST 工具参数
# =========================

class CreatePostInput(BaseModel):

    title: str = Field(
        min_length=1,
        description="文章标题"
    )

    body: str = Field(
        min_length=1,
        description="文章正文"
    )

    user_id: int = Field(
        gt=0,
        description="用户ID，必须是正整数"
    )


# =========================
# 5. 定义工具一：GET 查询文章
# =========================

@tool(args_schema=GetPostInput)
def get_post(post_id: int) -> str:
    """根据文章ID查询文章内容。当用户询问某篇文章的标题、正文或文章详情时使用。"""

    url = f"{BASE_URL}/posts/{post_id}"

    try:

        response = httpx.get(
            url,
            timeout=TIMEOUT
        )

        response.raise_for_status()

        data = response.json()

        return (
            f"文章查询成功：\n"
            f"文章ID：{data['id']}\n"
            f"用户ID：{data['userId']}\n"
            f"标题：{data['title']}\n"
            f"正文：{data['body']}"
        )

    except httpx.TimeoutException:
        return "文章查询失败：请求超时。"

    except httpx.HTTPStatusError as e:
        return f"文章查询失败：HTTP状态码 {e.response.status_code}。"

    except httpx.RequestError as e:
        return f"文章查询失败：网络请求异常，{str(e)}"

    except (ValueError, KeyError) as e:
        return f"文章数据解析失败：{str(e)}"


# =========================
# 6. 定义工具二：POST 创建文章
# =========================

@tool(args_schema=CreatePostInput)
def create_post(
    title: str,
    body: str,
    user_id: int
) -> str:
    """向测试文章API提交一篇新文章。当用户要求创建、发布或提交文章时使用。"""

    url = f"{BASE_URL}/posts"

    payload = {
        "title": title,
        "body": body,
        "userId": user_id
    }

    try:

        response = httpx.post(
            url,
            json=payload,
            timeout=TIMEOUT
        )

        response.raise_for_status()

        data = response.json()

        return (
            f"文章提交成功：\n"
            f"文章ID：{data['id']}\n"
            f"用户ID：{data['userId']}\n"
            f"标题：{data['title']}\n"
            f"正文：{data['body']}\n"
            f"HTTP状态码：{response.status_code}\n"
            f"说明：这是测试API返回的模拟创建结果。"
        )

    except httpx.TimeoutException:
        return "文章创建失败：请求超时。"

    except httpx.HTTPStatusError as e:
        return f"文章创建失败：HTTP状态码 {e.response.status_code}。"

    except httpx.RequestError as e:
        return f"文章创建失败：网络请求异常，{str(e)}"

    except (ValueError, KeyError) as e:
        return f"文章数据解析失败：{str(e)}"


# =========================
# 7. 初始化 LLM
# =========================

llm = ChatOpenAI(
    model="deepseek-chat",
    api_key=api_key,
    base_url="https://api.deepseek.com/v1",
    temperature=0
)


# =========================
# 8. 创建 Agent
# =========================

tools = [
    get_post,
    create_post
]

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt="""
你是一个 API 业务助手。

规则：
1. 用户询问已有文章内容时，调用 get_post。
2. 用户要求创建或提交文章时，调用 create_post。
3. 必须根据用户提供的信息生成工具参数。
4. 必须依据 API 返回结果回答。
5. 如果 API 调用失败，应如实说明。
6. 不得编造 API 返回的数据。
7. 普通闲聊不需要调用工具。
"""
)


# =========================
# 9. 交互测试
# =========================

if __name__ == "__main__":

    while True:

        question = input(
            "\n请输入问题（输入 q 退出）："
        ).strip()

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

            print(f"Agent 执行失败：{str(e)}")
