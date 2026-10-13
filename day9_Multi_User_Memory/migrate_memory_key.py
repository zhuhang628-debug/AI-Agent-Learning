
from memory_manager import get_memory, save_memory, delete_memory

user_id = "user_001"

# 1. 读取当前用户的记忆
memories = get_memory(user_id)
print("迁移前：", memories)

# 2. 检查旧字段是否存在
if "primary_language" in memories:
    old_value = memories["primary_language"]

    # 3. 如果新字段不存在，就先保存旧值
    if "primary_programming_language" not in memories:
        save_memory(
            user_id,
            "primary_programming_language",
            old_value
        )

    # 4. 确认新字段已经保存，再删除旧字段
    updated_memories = get_memory(user_id)

    if "primary_programming_language" in updated_memories:
        delete_memory(user_id, "primary_language")

print("迁移后：", get_memory(user_id))
