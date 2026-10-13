
from memory_service import manage_memory
from memory_manager import delete_memory, get_memory


user_id = "day9_preference_test"

# 清理之前测试留下的用户偏好
delete_memory(user_id, "learning_style")

# 测试 1：保存用户偏好
result1 = manage_memory(
    user_id,
    "以后教我代码时，请逐步解释每一步，并说明执行逻辑。"
)
print("测试 1：保存偏好")
print(result1)

# 检查数据库中是否保存了 learning_style
memory1 = get_memory(user_id)
print("当前长期记忆：", memory1)

assert "learning_style" in memory1, "没有成功保存学习偏好"

# 测试 2：更新用户偏好
result2 = manage_memory(
    user_id,
    "以后讲代码时，除了逐步解释，也请说明关键语法的作用。"
)
print("\n测试 2：更新偏好")
print(result2)

memory2 = get_memory(user_id)
print("更新后的长期记忆：", memory2)

assert "learning_style" in memory2, "更新后学习偏好丢失"

print("\n基础测试通过：学习偏好已保存，并且可以继续更新。")
