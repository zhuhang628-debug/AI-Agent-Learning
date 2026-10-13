from memory_filter import judge_memory_action
from memory_manager import (
    save_memory,
    get_memory,
    delete_memory
)

def manage_memory(user_id,user_input):
    current_memory=get_memory(user_id)
    decision=judge_memory_action(
        user_input,
        current_memory
    )
    action=decision["action"]
    key=decision.get("key")
    value=decision.get("value","")

    if action=="save":
        save_memory(user_id,key,value)
        message=f"已保存或更新记忆：{key}={value}"
    elif action == "delete":

        if key not in current_memory:
            message = f"当前没有找到这条记忆：{key}"
        else:
            delete_memory(user_id, key)
            message = f"已删除记忆：{key}"

    else:
        message = "本次输入不需要修改长期记忆"

        # 4. 返回操作结果和最新记忆
    return {
        "action": action,
        "reason": decision.get("reason", ""),
        "message": message,
        "current_memory": get_memory(user_id)
    }