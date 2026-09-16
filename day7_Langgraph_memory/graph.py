import sqlite3

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import StateGraph,END,START
from state import MemoryState
from nodes import chat_node,extract_memory

conn=sqlite3.connect("memory.db",check_same_thread=False)

memory=SqliteSaver(conn)

graph=StateGraph(MemoryState)

graph.add_node(
    "extract_memory",
    extract_memory
)

graph.add_node("chat",chat_node)

graph.add_edge(START,"extract_memory")

graph.add_edge("extract_memory","chat")

graph.add_edge("chat",END)

app = graph.compile(checkpointer=memory)