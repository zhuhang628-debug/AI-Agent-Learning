from state import TravelState
from llm import llm
from tools import search_weather



def weather_node(state:TravelState):
    print("执行天气查询节点")
    weather=search_weather.invoke(
        state["city"]
    )
    state["weather"]=weather
    return state

def attraction_node(state:TravelState):
    print("执行景点查询节点")
    state["attractions"]=[
        "西湖",
        "灵隐寺",
        "西溪湿地",
    ]
    return state

def answer_node(state :TravelState):
    print("执行答案生成节点")
    if state["intent"]=="weather":
        prompt=f"""
你是个天气助手，
用户问题：
{state["user_input"]}
天气信息：
{state["weather"]}
请直接回答天气相关问题
"""
    elif state["intent"] == "attraction":
        prompt = f"""
    你是旅游景点助手。
    用户问题：
    {state["user_input"]}
    景点信息：
    {state["attractions"]}
    请介绍相关景点。
    """
    else:
        prompt = f"""
    你是旅游规划助手。
    用户需求：
    {state["user_input"]}
    天气：
    {state["weather"]}
    景点：
    {state["attractions"]}
    请生成旅游方案。
    """
    response=llm.invoke(prompt)
    state["answer"]=response.content
    return state

def analyze_node(state:TravelState):
    print("执行需求分析节点")
    user_input=state["user_input"]
    if "天气" in user_input:
        state["intent"]="weather"
    elif "景点" in user_input:
        state["intent"]="attraction"
    else:
        state["intent"]="travel"
    return state

def travel_node(state:TravelState):
    print("执行旅游规划节点")
    state["weather"]="杭州未来三天天气晴朗，20-28度"
    state["attractions"]=[
        "西湖",
        "灵隐寺",
        "西溪湿地"
    ]
    return state


