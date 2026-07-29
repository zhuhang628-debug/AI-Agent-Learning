import os

from dotenv import load_dotenv
from langchain_classic.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from agent_memory import AgentMemory

load_dotenv()

#创建工具
@tool
def search_weather(city:str):
    """
    查询城市天气
    """
    return f"{city}今天晴天，温度25度"

@tool
def calculator(expression:str):
    """
    数学计算,可以计算简单的数学表达式
    """
    try:
        result = eval(expression)
        return  f"计算结果是:{result}"
    except:
        return "无法计算"
#创建模型
llm= ChatOpenAI(
    model="deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1"
)

#工具列表
tools=[
    search_weather,
    calculator
]

#Agent提示词
prompt=ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "你是一个智能助手，可以使用工具帮助用户解决问题"
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
        )
    ]
)

#创建Agent
agent=create_tool_calling_agent(
    llm,
    tools,
    prompt
)

#创建执行器
executor=AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,

)

#创建memory对象
memory=AgentMemory()

# #调用Agent
# response=executor.invoke(
#     {
#         "input":"2乘3等于多少"
#     }
# )
#
#
#
# print(response["output"])

while True:
    user_input=input("用户：")
    memory.add_user_message(
        user_input
    )
    reponse=executor.invoke(
        {
            "input": user_input,
            "chat_history":memory.get_messages()
        }
    )
    answer=reponse["output"]

    print(
        "AI:",
        answer
    )

    memory.add_ai_message(
        answer
    )