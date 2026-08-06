from day5_travel_agent.agent import executor
from day5_travel_agent.memory import TravelMemory

memory=TravelMemory()

while True:
    user_input=input(
        "用户："
    )
    memory.add_user_message(
        user_input
    )
    response=executor.invoke(
        {
            "input":user_input,
            "chat_history":memory.get_messages()
        }
    )
    answer=response["output"]
    print(
        "AI:",
        answer
    )
    memory.add_ai_message(
        answer
    )