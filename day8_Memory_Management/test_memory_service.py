from memory_service import manage_memory

user_id = "day8_lifecycle_test"

test_inputs = [
    "我正在准备 AI Agent 实习",
    "我主要使用 Java 开发",
    "我现在主要使用 Python 开发",
    "请忘记我的主要编程语言偏好",
    "帮我计算一下 1 + 1"
]

for user_input in test_inputs:
    print("\n用户输入：", user_input)

    result = manage_memory(user_id, user_input)

    print("操作类型：", result["action"])
    print("操作说明：", result["message"])
    print("当前记忆：", result["current_memory"])
