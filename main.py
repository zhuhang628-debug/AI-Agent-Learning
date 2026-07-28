import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from openai import OpenAI

from chat_history import ChatHistory

chat_history = ChatHistory()
load_dotenv()
app = FastAPI()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1"
)
@app.get("/")
def home():
    return {"message":"AI Agent Server Running"}

@app.get("/chat_stream")
def chat_stream(message: str):
    chat_history.add_message(
        "user",
        message
    )
    response=client.chat.completions.create(
        model="deepseek-chat",
        messages=chat_history.get_history(),
        stream=True
    )
    def generate():
        answer=""
        for chunk in response:
            content=chunk.choices[0].delta.content
            if content:
                answer+=content
                yield f"data:{content}\n\n"

        chat_history.add_message(
            "assistant",
            answer
        )
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
    )
