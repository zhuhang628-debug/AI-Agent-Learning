from day8_Memory_Management.memory_manager import save_memory,get_memory
from memory_filter import judge_memory

user_id="zhuhang"

test_inputs=[
    "我正在准备 AI Agent 实习",
    "我主要使用 Python 开发",
    "帮我计算一下 1 + 1",
    "今天中午吃了面条"
]
for user_input in test_inputs:
    print("\n用户输入:",user_input)
    result=judge_memory(user_input)
    print("判断结果",result)

    if result["should_save"]:
        save_memory(
            user_id,
            result["key"],
            result["value"]
        )
        print("已保存长期记忆")
    else:
        print("跳过保存，不写入数据库")
print("\n当前用户长期记忆")
print(get_memory(user_id))