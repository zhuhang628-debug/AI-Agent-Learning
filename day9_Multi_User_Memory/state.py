
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages


class MemoryAgentState(TypedDict):
    user_id: str
    user_input: str

    # 长期记忆管理结果
    memory_action: dict

    # 当前用户的长期记忆
    long_term_memory: dict

    # 当前会话的短期对话历史
    messages: Annotated[list, add_messages]

    # 当前轮次的回答
    answer: str
