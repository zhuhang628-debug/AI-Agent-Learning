
from graph import app


def chat(user_id: str, thread_id: str, user_input: str):
    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    result = app.invoke(
        {
            "user_id": user_id,
            "user_input": user_input,
            "memory_action": {},
            "long_term_memory": {},
            "messages": [],
            "answer": ""
        },
        config=config
    )

    print("\n用户：", user_input)
    print("记忆操作：", result["memory_action"]["message"])
    print("当前长期记忆：", result["long_term_memory"])
    print("当前会话消息数：", len(result["messages"]))
    print("AI：", result["answer"])


if __name__ == "__main__":
    user_id = "user_001"

    # 同一用户、同一会话：测试短期对话记忆
    chat(
        user_id,
        "thread_memory_test",
        "我正在学习 LangGraph。请解释一下 State 是什么。"
    )

    chat(
        user_id,
        "thread_memory_test",
        "那它和刚才提到的 Node 有什么区别？"
    )

    # 同一用户、不同会话：测试短期历史隔离
    chat(
        user_id,
        "thread_new_test",
        "你知道我刚才在另一个会话里问了什么吗？"
    )
