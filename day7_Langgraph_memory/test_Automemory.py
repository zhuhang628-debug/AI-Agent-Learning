from graph import app                                      # 导入编译好的 LangGraph
from langchain_core.messages import HumanMessage           # 导入用户消息类型


# 创建本次会话的配置
config = {
    "configurable": {
        "thread_id": "zhuhang_auto_memory_002"              # 当前对话的唯一 ID
    }
}


# 用户发送一句包含个人信息的话
result = app.invoke(
    {
        "user_id": "zhuhang",                              # 用户的长期记忆 ID
        "messages": [
            HumanMessage(
                content="我的编程语言是什么？我的求职目标是什么？"
            )
        ]
    },
    config=config
)


# 输出 AI 最后一条消息
print("===== AI 回答 =====")


# result["messages"]：获取所有消息
# [-1]：获取最后一条消息
# .content：获取最后一条消息的文本内容
print(result["messages"][-1].content)