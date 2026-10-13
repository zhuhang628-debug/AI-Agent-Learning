from typing import TypedDict

from memory_manager import*
from langgraph.checkpoint.memory import MemorySaver
from langgraph.constants import START,END
from langgraph.graph import StateGraph

from day9_Multi_User_Memory.memory_manager import get_memory


#1.定义工作流状态
class MemoryState(TypedDict):
    user_id: str
    messages:list[str]
    long_term_memory: dict

#2.定义读取长期记忆的节点
def read_memory_node(state:MemoryState):
    user_id=state["user_id"]
    #根据user_id读取长期记忆
    memories=get_memory(user_id)
    return {
        "long_term_memory":memories
    }

#3.创建工作流
builder=StateGraph(MemoryState)

builder.add_node("read_memory",read_memory_node)
builder.add_edge(START,"read_memory")
builder.add_edge("read_memory",END)

memroy=MemorySaver()
app=builder.compile(checkpointer=memroy)

# 4. 准备测试数据
user_id = "user_001"

delete_memory(user_id, "primary_language")
save_memory(user_id, "primary_language", "Python")

config_a = {
    "configurable": {
        "thread_id": "thread_A"
    }
}

config_b = {
    "configurable": {
        "thread_id": "thread_B"
    }
}


# 5. 在会话 A 中读取长期记忆
result_a = app.invoke(
    {
        "user_id": user_id,
        "messages": ["会话 A"],
        "long_term_memory": {}
    },
    config=config_a
)

print("会话 A 读取到的长期记忆：", result_a["long_term_memory"])


# 6. 在会话 B 中读取同一用户的长期记忆
result_b = app.invoke(
    {
        "user_id": user_id,
        "messages": ["会话 B"],
        "long_term_memory": {}
    },
    config=config_b
)

print("会话 B 读取到的长期记忆：", result_b["long_term_memory"])


# 7. 验证两个会话读取到相同的长期记忆
assert result_a["long_term_memory"]["primary_language"] == "Python"
assert result_b["long_term_memory"]["primary_language"] == "Python"

print("测试通过：同一用户的长期记忆可以跨会话共享。")

