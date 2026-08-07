from langgraph.graph import (StateGraph,END)

from nodes import (
    weather_node,
    attraction_node,
    answer_node,
    analyze_node,
    travel_node
)
from state import TravelState

from router import route_question
from router_llm import llm_router

graph=StateGraph(
    TravelState
)

#添加节点
graph.add_node(
    "analyze",
    analyze_node
)
graph.add_node(
    "weather",
    weather_node
)
graph.add_node(
    "attraction",
    attraction_node
)
graph.add_node(
    "answer",
    answer_node
)
graph.add_node(
    "router",
    llm_router
)
graph.add_node(
    "travel",
    travel_node
)

#设置入口
graph.set_entry_point(
    "router"
)

#条件边
graph.add_conditional_edges(
    "router",
    route_question,
    {

        "weather":"weather",
        "attraction":"attraction",
        "travel":"travel",
        "answer":"answer"
    }
)

#后续流程,连接节点
graph.add_edge(
    "weather",
    "answer"
)
graph.add_edge(
    "attraction",
    "answer"
)
graph.add_edge(
    "travel",
    "answer"
)
graph.add_edge(
    "answer",
    END
)
app=graph.compile()