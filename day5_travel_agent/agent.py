import os

from dotenv import load_dotenv
from langchain_classic.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from day5_travel_agent.tools import search_weather, search_attraction

load_dotenv()

llm=ChatOpenAI(
    model="deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1",
)
tools=[
    search_weather,
    search_attraction
]
prompt=ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            你是一个专业的旅游规划助手。
            根据用户需求指定旅游方案。
            必要时调用工具获取信息。
            """
        ),
        (
            "placeholder",
            "{chat_history}"
        ),
        (
            "human",
            "{input}"
        ),
        (
            "placeholder",
            "{agent_scratchpad}"
        ),
    ]
)
agent=create_tool_calling_agent(
    llm,
    tools,
    prompt
)
executor=AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True
)
