
from memory_manager import get_memory
from llm import llm


def personalized_chat(user_id, user_input):
    # 1. 读取该用户的长期记忆
    memories = get_memory(user_id)

    # 2. 获取用户的学习偏好
    learning_style = memories.get(
        "learning_style",
        "使用清晰、简洁的方式回答"
    )

    # 3. 将用户偏好加入系统提示词
    system_prompt = f"""
你是一个 AI 学习助手。

请遵循以下用户偏好回答问题：
{learning_style}

请保证回答准确、清晰。
"""

    # 4. 组合系统提示词与当前问题
    prompt = f"""
{system_prompt}

用户当前的问题：
{user_input}
"""

    # 5. 调用大模型生成回答
    response = llm.invoke(prompt)

    return response.content


# 使用刚才测试中保存偏好的用户
user_id = "day9_preference_test"

answer = personalized_chat(
    user_id,
    "请解释 Python 装饰器，并给一个简单的代码例子。"
)

print("AI 的个性化回答：")
print(answer)
