from langchain_core.tools import tool


@tool
def search_attraction(city:str):
    """
    查询城市热门旅游景点
    """
    attractions={
        "杭州":
            "西湖、灵隐寺、雷峰塔、河坊街",
        "上海":
        "外滩、东方明珠、迪士尼"
    }
    return attractions.get(
        city,
        "暂无景点信息"
    )
@tool
def search_weather(city:str):
    """
    查询城市天气
    """
    return f"{city}未来三天天气晴朗，温度20-28度"