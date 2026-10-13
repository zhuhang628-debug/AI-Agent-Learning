from typing import TypedDict, Annotated
import operator
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph,START,END

#1.定义图的状态
class ChatState(TypedDict):
    user_id: str
    messages:Annotated[list[str],operator.add]

#2.定义节点
def chat_node(state:ChatState):
    print(f"当前用户:{state['user_id']}")
    print(f"当前会话已有消息:{state['messages']}")
    return {}

#3.创建工作流
builder=StateGraph(ChatState)
builder.add_node("chat",chat_node)
builder.add_edge(START,"chat")
builder.add_edge("chat",END)

#4.配置检查点保存器
memory=MemorySaver()
app=builder.compile(checkpointer=memory)

#5.同一个用户的两个独立对话
user_id="user_001"
config_a={
    "configurable":{
        "thread_id":"thread_A1"
    }
}

config_b={
    "configurable":{
        "thread_id":"thread_A2"
    }
}

# 6. 会话 A：连续发送两条消息
result_a1 = app.invoke(
    {
        "user_id": user_id,
        "messages": ["我正在学习 Python"]
    },
    config=config_a
)
print("会话 A 第一次：", result_a1)


result_a2 = app.invoke(
    {
        "user_id": user_id,
        "messages": ["我正在学习 LangGraph"]
    },
    config=config_a
)
print("会话 A 第二次：", result_a2)


# 7. 会话 B：发送一条消息
result_b1 = app.invoke(
    {
        "user_id": user_id,
        "messages": ["我正在开发 Java 项目"]
    },
    config=config_b
)
print("会话 B 第一次：", result_b1)