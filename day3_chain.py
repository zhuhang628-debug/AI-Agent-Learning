import os

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

load_dotenv()

llm=ChatOpenAI(
    model="deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1",
)

prompt=ChatPromptTemplate.from_template(
    """
你是一名AI Agent开发导师。

请回答：
{question}
"""
)

chain=prompt | llm

response=chain.invoke(
    {
        "question": input("请输入你的问题：")
    }
)
print(response.content)