# Day7：LangGraph Memory

## 一、学习目标
学习 LangGraph Memory，实现短期记忆、长期记忆以及跨会话记忆。
- State 与 messages
- add_messages
- thread_id 会话隔离
- SQLite 持久化短期记忆
- user_id 长期记忆
- LLM 自动提取长期记忆
- JSON + Pydantic 结构化记忆
- 跨 thread_id 读取长期记忆

## 二、核心概念

### 1. State
```python
class MemoryState(TypedDict):
    messages: Annotated[list, add_messages]
    user_id: str
```
- `messages`：保存当前对话消息
- `user_id`：标识用户

### 2. thread_id
`thread_id` 用于区分不同会话。
```python
config = {
    "configurable": {
        "thread_id": "zhuhang"
    }
}
```
不同 `thread_id` 的短期记忆相互隔离。

### 3. messages[-1]
```python
last_message = messages[-1]
user_text = last_message.content
```
`messages[-1]` 获取最后一条消息，`.content` 获取消息中的实际文本。

## 三、短期记忆
使用 LangGraph Checkpointer + SQLite 保存当前会话状态。
```python
conn = sqlite3.connect(
    "memory.db",
    check_same_thread=False
)
memory = SqliteSaver(conn)
app = graph.compile(checkpointer=memory)
```
短期记忆：
```text
thread_id → memory.db → 当前会话 messages
```

## 四、长期记忆
使用 `long_term_memory.py` 将用户长期信息保存到 SQLite。
```text
user_id → long_term_memory.db
```
例如：
```text
zhuhang | language | Java
zhuhang | goal | 找 AI Agent 实习
```

## 五、LLM 自动提取长期记忆
Graph：
```text
START
  ↓
extract_memory
  ↓
chat
  ↓
END
```
用户输入：
```text
我平时主要写 Java，现在想找 AI Agent 实习。
```
LLM 自动提取：
```text
language = Java
goal = 找 AI Agent 实习
```
然后调用 `save_memory()` 保存到 `long_term_memory.db`。

## 六、JSON + Pydantic
最开始尝试：
```python
llm.with_structured_output(UserMemory)
```
但 DeepSeek API 返回：
```text
400 BadRequestError
This response_format type is unavailable now
```
因此改为：
```text
LLM → JSON → json.loads() → Pydantic → SQLite
```
`memory_schema.py`：
```python
from pydantic import BaseModel

class UserMemory(BaseModel):
    language: str | None = None
    goal: str | None = None
    interest: str | None = None
```

## 七、短期记忆 vs 长期记忆
```text
短期记忆
thread_id
   ↓
memory.db
   ↓
当前会话上下文

长期记忆
user_id
   ↓
long_term_memory.db
   ↓
用户长期信息
```
核心理解：
> 短期记忆解决“这次对话发生了什么”，长期记忆解决“这个用户有哪些值得长期保存的信息”。

## 八、项目结构
```text
day7_Langgraph_memory
├── llm.py
├── state.py
├── nodes.py
├── graph.py
├── long_term_memory.py
├── memory_schema.py
├── test_Automemory.py
├── memory.db
└── long_term_memory.db
```

## 九、遇到的问题

### 1. extract_memory() 缺少 state
错误：
```text
extract_memory() missing 1 required positional argument: 'state'
```
错误：
```python
graph.add_edge(extract_memory(), "chat")
```
正确：
```python
graph.add_edge("extract_memory", "chat")
```
`add_edge()` 连接的是节点名称，不是执行函数。

### 2. return 字典写错
错误：
```python
return {"messages", [response]}
```
正确：
```python
return {"messages": [response]}
```

### 3. Structured Output 不支持
DeepSeek 当前请求方式不支持对应 `response_format`，改用 JSON + `json.loads()` + Pydantic。

## 十、最终测试
第一次：
```text
用户：
我平时主要写 Java，现在想找 AI Agent 实习。
```
自动保存：
```text
language = Java
goal = 找 AI Agent 实习
```
换新的 `thread_id` 后：
```text
用户：
我的编程语言是什么？我的求职目标是什么？
```
仍然可以读取：
```text
Java
找 AI Agent 实习
```
说明长期记忆已经实现跨会话读取。

## 十一、Day7 总结
```text
✅ State
✅ messages / add_messages
✅ thread_id
✅ SQLite 短期记忆
✅ user_id
✅ SQLite 长期记忆
✅ LLM 自动提取记忆
✅ JSON + Pydantic
✅ 跨会话长期记忆
```
Day7 完成。

## 十二、Day8
下一步继续完善 Memory：
- 记忆筛选
- 记忆更新
- 记忆覆盖
- 避免重复记忆
- 记忆生命周期管理