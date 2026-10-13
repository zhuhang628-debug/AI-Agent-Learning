
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from state import MemoryAgentState
from nodes import (
    manage_memory_node,
    load_memory_node,
    chat_node,
)


builder = StateGraph(MemoryAgentState)

builder.add_node("manage_memory", manage_memory_node)
builder.add_node("load_memory", load_memory_node)
builder.add_node("chat", chat_node)

builder.add_edge(START, "manage_memory")
builder.add_edge("manage_memory", "load_memory")
builder.add_edge("load_memory", "chat")
builder.add_edge("chat", END)

checkpointer = MemorySaver()

app = builder.compile(
    checkpointer=checkpointer
)
