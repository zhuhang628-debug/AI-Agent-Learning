import os
from dotenv import load_dotenv
from fastapi import FastAPI
from openai import OpenAI

load_dotenv()
app = FastAPI()

client=OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1"
)
@app.get("/")
def home():
    return {"message":"AI Agent Server Running"}

@app.get("/chat")
def chat(message: str):
    response=client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {
                "role":"user",
                "content":message
            }
        ]
    )
    return{
        "answer":response.choices[0].message.content
    }