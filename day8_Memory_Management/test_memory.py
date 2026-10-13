from memory_manager import (
save_memory,
get_memory,
delete_memory
)

user_id="zhuhang"
print("第一次保存")
save_memory(
    user_id,
    "language",
    "Java"
)
print (get_memory(user_id))
print("\n更新记忆")
save_memory(
    user_id,
    "language",
    "Python"
)
print(get_memory(user_id))
print("\n保存第二条记忆")
save_memory(
    user_id,
    "goal",
    "AI Agent 实习"
)
print(get_memory(user_id))
print("\n删除 language")

delete_memory(
    user_id,
    "language"
)

print(get_memory(user_id))