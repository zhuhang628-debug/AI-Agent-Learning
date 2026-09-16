from day7_Langgraph_memory.long_term_memory import save_memory, get_memory

save_memory(
    "zhuhang",
    "language",
    "Java"
)

save_memory(
    "zhuhang",
    "goal",
    "AI Agent 实习"
)

memory=get_memory("zhuhang",)

print("用户长期记忆:")
print(memory)