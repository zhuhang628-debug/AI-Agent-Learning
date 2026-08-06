from fastapi import FastAPI
from fastapi.responses import StreamingResponse

from agent import executor
from memory import TravelMemory

app=FastAPI()
memory=TravelMemory()

@app.get("/")
def home():
    return {
        "message":
            "Travel Agent Running"
    }
@app.get("/travel")
async def travel_plan(message: str):
    memory.add_user_message(message)
    async def generate():
        answer = ""
        async for event in executor.astream_events(
            {
                "input": message,
                "chat_history": memory.get_messages()
            },
            version="v1"
        ):
            kind = event["event"]
            if kind == "on_chat_model_stream":
                token = event["data"]["chunk"].content
                if token:
                    answer += token
                    yield token
        memory.add_ai_message(answer)
    return StreamingResponse(
        generate(),
        media_type="text/plain"
    )








# while True:
#     user_input=input(
#         "用户："
#     )
#     memory.add_user_message(
#         user_input
#     )
#     response=executor.invoke(
#         {
#             "input":user_input,
#             "chat_history":memory.get_messages()
#         }
#     )
#     answer=response["output"]
#     print(
#         "AI:",
#         answer
#     )
#     memory.add_ai_message(
#         answer
#     )