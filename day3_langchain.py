import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

llm=ChatOpenAI(
    model="deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1"
)

response=llm.invoke(
    "什么是AI Agent?"
)

print(response.content)