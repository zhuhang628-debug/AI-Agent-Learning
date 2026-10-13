
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from llm import llm
from memory_service import manage_memory
from memory_manager import get_memory


def manage_memory_node(state):
    """判断当前输入是否需要更新长期记忆。"""
    result = manage_memory(
        state["user_id"],
        state["user_input"]
    )
    return {"memory_action": result}


def load_memory_node(state):
    """读取当前用户的长期记忆。"""
    memories = get_memory(state["user_id"])
    return {"long_term_memory": memories}


def chat_node(state):
    """结合短期对话历史和长期记忆生成回答。"""

    memories = state.get("long_term_memory", {})
    history = state.get("messages", [])
    user_input = state["user_input"]

    system_prompt = f"""
你是一个 AI 学习助手。

以下是当前用户的长期记忆：
{memories}

回答时请参考这些记忆，尤其注意用户的学习偏好。
不要把没有记录的信息当作用户事实。
如果当前记忆为空，就正常回答用户问题。
"""

    # 构建本轮模型需要读取的消息
    messages = [
        SystemMessage(content=system_prompt),
        *history,
        HumanMessage(content=user_input)
    ]

    # 调用模型生成回答
    response = llm.invoke(messages)

    # 将本轮问答追加到短期历史

    return {
        "messages": [
            HumanMessage(content=user_input),
            AIMessage(content=response.content)
        ],
        "answer": response.content
    }
