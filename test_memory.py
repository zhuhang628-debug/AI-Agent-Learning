from agent_memory import AgentMemory


memory = AgentMemory()


memory.add_user_message(
    "我叫朱航"
)


memory.add_ai_message(
    "你好朱航"
)


print(memory.get_messages())