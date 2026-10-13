
from memory_manager import save_memory, get_memory, delete_memory


# 1. 准备两个不同的用户
user_a = "isolation_test_A"
user_b = "isolation_test_B"

# 2. 清理本次测试可能留下的数据
for user_id in (user_a, user_b):
    delete_memory(user_id, "learning_style")

# 3. 为两个用户分别保存不同的偏好
save_memory(
    user_a,
    "learning_style",
    "逐步解释代码，并说明执行逻辑"
)

save_memory(
    user_b,
    "learning_style",
    "优先给出简洁的代码示例"
)

# 4. 分别读取两个用户的长期记忆
memory_a = get_memory(user_a)
memory_b = get_memory(user_b)

print("用户 A 的偏好：", memory_a)
print("用户 B 的偏好：", memory_b)

# 5. 验证用户之间的记忆隔离
assert memory_a["learning_style"] == "逐步解释代码，并说明执行逻辑"
assert memory_b["learning_style"] == "优先给出简洁的代码示例"

# 6. 删除用户 A 的偏好
delete_memory(user_a, "learning_style")

memory_a_after_delete = get_memory(user_a)
memory_b_after_delete = get_memory(user_b)

print("\n删除用户 A 的偏好后：")
print("用户 A 的记忆：", memory_a_after_delete)
print("用户 B 的记忆：", memory_b_after_delete)

# 7. 验证删除只影响用户 A
assert "learning_style" not in memory_a_after_delete
assert memory_b_after_delete["learning_style"] == "优先给出简洁的代码示例"

print("\n测试通过：用户记忆相互隔离，删除操作也不会影响其他用户。")
