import os

from dotenv import load_dotenv
from langchain_core.messages.tool import tool_call
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

load_dotenv()
@tool
def search_weather(city: str):
    """
    查询城市天气
    """
    return f"{city}今天晴天，温度25度"

llm=ChatOpenAI(
    model="deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1"
)

tools=[
    search_weather
]

llm_with_tools=llm.bind_tools(tools)

#第一次请求
response=llm_with_tools.invoke(
    "上海今天的天气怎么样？"
)
#判断是否调用工具
if response.tool_calls:
    tool_call=response.tool_calls[0]
    #执行工具
    tool_result=search_weather.invoke(
        tool_call["args"]
    )
    final_response=llm.invoke(
        f"""
        用户问题：
        上海今天天气怎么样？
        
        工具返回：
        {tool_result}
        根据工具结果回答用户
        """
    )
    print(final_response.content)
else:
    print(response.content)