
import json
from llm import llm


ALLOWED_MEMORY_KEYS = {
    "goal",
    "primary_programming_language",
    "interest",
    "project",
    "learning_style"
}


def judge_memory_action(user_input, current_memory):
    """
    根据用户输入和已有记忆，判断应该执行什么记忆操作。
    """

    prompt = f"""
你是 AI Agent 的长期记忆管理模块。

请根据用户输入和当前已有记忆，判断应该执行什么操作。

允许的操作：
1. save：保存新记忆，或者更新已有记忆。
2. delete：用户明确要求忘记某条已有记忆。
3. ignore：一次性问题、普通闲聊或不值得长期保存的信息。

允许的记忆键名：
- goal：长期目标
- primary_programming_language：主要编程语言
- interest：长期兴趣
- project：持续进行的项目
- learning_style：用户偏好的学习方式、回答风格和代码讲解习惯

规则：
1. 只能使用上面列出的记忆键名，不得自行创造键名。
2. 如果用户明确更新了某条记忆，使用 save，
   并为这类信息选择相同的标准键名。
3. 只有用户明确要求删除记忆时，才使用 delete。
4. 如果没有值得保存的信息，也没有明确的删除请求，使用 ignore。
5. 不得把推测当作用户事实。
6. 必须只返回合法 JSON，不要输出 Markdown 代码块。

返回格式：
{{
    "action": "save",
    "key": "goal",
    "value": "准备 AI Agent 实习",
    "reason": "这是用户的长期目标"
}}

当前已有记忆：
{json.dumps(current_memory, ensure_ascii=False)}

用户输入：
{user_input}
"""

    response = llm.invoke(prompt)
    content = response.content.strip()

    result = json.loads(content)

    # 校验模型返回的基本结构
    if not isinstance(result, dict):
        raise ValueError("模型返回结果必须是 JSON 对象")

    action = result.get("action")
    key = result.get("key")
    value = result.get("value")

    if action not in {"save", "delete", "ignore"}:
        raise ValueError(f"不支持的记忆操作：{action}")

    if action in {"save", "delete"}:
        if key not in ALLOWED_MEMORY_KEYS:
            raise ValueError(f"不允许的记忆键名：{key}")

    if action == "save":
        if not isinstance(value, str) or not value.strip():
            raise ValueError("待保存的记忆内容不能为空")

    return result
