
from memory_manager import get_memory

for user_id in ("user_001", "day9_preference_test"):
    print(f"\n用户：{user_id}")
    print(get_memory(user_id))
