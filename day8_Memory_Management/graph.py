from langgraph.graph import StateGraph,START,END
from state import MemoryState
from nodes import memory_node

#1.创建工作流构建器
graph=StateGraph(MemoryState)
#2.注册节点
graph.add_node("memory",memory_node)
#3.链接工作流
graph.add_edge(START,"memory")
graph.add_edge("memory",END)
#4.编译工作流
app=graph.compile()