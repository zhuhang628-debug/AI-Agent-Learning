from langchain_core.tools import tool


@tool
def search_weather(city:str):
    """
    查询城市天气
    """
    return f"{city}今天晴天，温度25度"