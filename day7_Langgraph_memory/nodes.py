import json                                             # 导入 JSON 模块
from llm import llm                                    # 导入 DeepSeek LLM
from state import MemoryState                          # 导入 LangGraph State
from long_term_memory import get_memory, save_memory   # 导入长期记忆函数
from memory_schema import UserMemory                    # 导入长期记忆结构

def extract_memory(state: MemoryState):
    # 获取当前用户的 user_id
    user_id = state["user_id"]
    # 获取当前所有消息
    messages = state["messages"]
    # 获取最后一条消息
    last_message = messages[-1]
    # 获取最后一条消息的文本
    user_text = last_message.content
    # 告诉 LLM 必须返回 JSON
    prompt = f"""
请分析下面用户说的话。
用户说：
{user_text}
请提取其中适合长期保存的用户信息。
只提取用户明确表达的信息。
可提取的信息：
language：用户主要使用的编程语言
goal：用户的学习、职业或其他长期目标
interest：用户长期感兴趣的技术方向
必须严格按照下面的 JSON 格式返回：
{{
    "language": null,
    "goal": null,
    "interest": null
}}
如果某个信息没有明确提到，就填写 null。
不要输出任何解释。
不要输出 Markdown。
只返回 JSON。
"""
    # 调用 LLM
    response = llm.invoke(prompt)
    # 获取 LLM 返回的文本
    content = response.content.strip()
    # 把 JSON 字符串转换成 Python 字典
    data = json.loads(content)
    # 把字典转换成 UserMemory 对象
    memory = UserMemory(**data)
    # 如果提取到了 language
    if memory.language:
        # 保存 language
        save_memory(
            user_id,
            "language",
            memory.language
        )
        # 打印保存结果
        print(
            f"保存长期记忆：language = {memory.language}"
        )
    # 如果提取到了 goal
    if memory.goal:
        # 保存 goal
        save_memory(
            user_id,
            "goal",
            memory.goal
        )
        # 打印保存结果
        print(
            f"保存长期记忆：goal = {memory.goal}"
        )
    # 如果提取到了 interest
    if memory.interest:
        # 保存 interest
        save_memory(
            user_id,
            "interest",
            memory.interest
        )
        # 打印保存结果
        print(
            f"保存长期记忆：interest = {memory.interest}"
        )

def chat_node(state: MemoryState):
    # 打印当前正在执行的节点
    print("执行 chat_node")
    # 获取当前用户 ID
    user_id = state["user_id"]
    # 获取用户长期记忆
    memory = get_memory(user_id)
    # 默认长期记忆为空
    memory_text = ""
    # 如果存在长期记忆
    if memory:
        # 把长期记忆字典转换成文本
        memory_text = "\n".join(
            f"{key}: {value}"
            for key, value in memory.items()
        )
    # 创建 System Prompt
    system_message = f"""
你正在帮助用户进行对话。
这是用户的长期记忆：
{memory_text}
请结合这些长期记忆回答用户的问题。
"""
    # 将 System Message 和聊天记录组合起来
    messages = [
        ("system", system_message),
        *state["messages"]
    ]
    # 调用 LLM
    response = llm.invoke(messages)
    # 返回 AI 消息
    return {
        "messages": [response]
    }