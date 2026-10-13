# Day8：LangGraph Memory Management（长期记忆管理）
## 一、学习目标
Day7 实现了 LangGraph 短期记忆、长期记忆和跨会话记忆。Day8 在此基础上继续完善长期记忆管理，解决以下问题：
- 什么信息值得长期保存？
- 如何识别用户对已有信息的更新？
- 如何覆盖旧记忆，避免同一类别出现多条冲突记录？
- 如何根据用户要求删除指定记忆？
- 如何忽略一次性请求，避免无意义的信息进入长期记忆？
- 如何将 Memory Manager 接入 LangGraph 工作流？
本日最终实现一个独立的长期记忆管理工作流，支持记忆筛选、保存、更新覆盖、删除、忽略和结果返回。
## 二、项目结构
```text
day8_Memory_Management/
├── llm.py                  # 初始化 DeepSeek 模型
├── memory_manager.py       # SQLite 长期记忆管理
├── memory_filter.py        # LLM 记忆操作判断
├── memory_service.py       # 记忆管理业务流程
├── state.py                # 定义 LangGraph State
├── nodes.py                # 定义记忆管理节点
├── graph.py                # 构建并编译工作流
├── test_memory_service.py  # 测试记忆管理业务
├── test_graph.py           # 测试 LangGraph 集成
├── long_term_memory.db     # 本地长期记忆数据库（不提交 Git）
└── README.md               # 学习记录与运行说明
```
## 三、整体运行架构
```text
用户输入
   ↓
test_graph.py
   ↓
app.invoke(initial_state)
   ↓
LangGraph 工作流
   ↓
memory_node(state)
   ↓
manage_memory(user_id, user_input)
   ├── get_memory()：读取当前记忆
   ├── judge_memory_action()：调用 LLM 判断
   ├── save_memory()：新增或覆盖
   ├── delete_memory()：删除指定记忆
   └── ignore：不修改数据库
   ↓
重新查询最新记忆
   ↓
返回 action、reason、message、current_memory
   ↓
LangGraph 返回最终 State
   ↓
test_graph.py 打印测试结果
```
核心分工：
- **LLM：** 理解用户输入，根据现有记忆判断应该执行什么操作。
- **Memory Manager：** 使用 SQLite 实现长期记忆的增删改查。
- **Memory Service：** 组织记忆读取、模型判断、数据库操作和结果返回。
- **LangGraph：** 负责状态传递和工作流执行。
## 四、SQLite 长期记忆管理
### 1. 数据库表设计
使用 SQLite 保存长期记忆，数据表为 `user_memory`：
```sql
CREATE TABLE IF NOT EXISTS user_memory (
    user_id TEXT NOT NULL,
    memory_key TEXT NOT NULL,
    memory_value TEXT NOT NULL,
    PRIMARY KEY (user_id, memory_key)
);
```
字段说明：
- `user_id`：用户标识，用于区分不同用户的记忆。
- `memory_key`：记忆类别，例如 `goal`、`primary_programming_language`。
- `memory_value`：该类别对应的记忆内容。
- `PRIMARY KEY (user_id, memory_key)`：联合主键，确保同一用户的同一类别只有一条记忆。
例如：
| user_id | memory_key | memory_value |
|---|---|---|
| user_001 | goal | 准备 AI Agent 实习 |
| user_001 | primary_programming_language | Java |
| user_002 | primary_programming_language | Python |
不同用户可以拥有相同的记忆类别，但彼此的数据相互独立。同一用户的同一记忆类别只能有一条记录，后续更新可以覆盖旧值。
### 2. 数据库连接与初始化
```python
import sqlite3

DB_PATH = "long_term_memory.db"

def get_connection():
    return sqlite3.connect(DB_PATH)
```
- `sqlite3`：Python 内置的 SQLite 数据库模块。
- `DB_PATH`：数据库文件名。当前使用相对路径，实际文件位置取决于程序的工作目录。
- `get_connection()`：封装数据库连接，供查询、保存和删除函数复用。
初始化时使用 `cursor.execute()` 执行建表 SQL，并通过 `CREATE TABLE IF NOT EXISTS` 避免重复创建已有数据表。`conn.commit()` 提交数据库操作，`conn.close()` 关闭连接。
在 `memory_manager.py` 文件末尾调用 `init_db()`，模块首次导入时即可完成数据库表初始化。
### 3. 保存与覆盖记忆
```python
cursor.execute(
    """
    INSERT OR REPLACE INTO user_memory
    (user_id, memory_key, memory_value)
    VALUES (?, ?, ?)
    """,
    (user_id, key, value)
)
```
- `INSERT OR REPLACE`：不存在对应主键时插入；存在相同主键时替换原记录。
- `?`：SQL 参数占位符。
- `(user_id, key, value)`：绑定实际参数，避免直接拼接用户输入构造 SQL。
例如：
```text
第一次保存：primary_programming_language = Java
第二次保存：primary_programming_language = Python
最终结果：primary_programming_language = Python
```
因为两次操作使用相同的 `user_id` 和 `memory_key`，所以旧值会被新值覆盖，而不是保留两条互相冲突的记录。
### 4. 查询长期记忆
```python
cursor.execute(
    """
    SELECT memory_key, memory_value
    FROM user_memory
    WHERE user_id = ?
    """,
    (user_id,)
)
rows = cursor.fetchall()
```
- `SELECT`：查询指定字段。
- `WHERE user_id = ?`：只查询指定用户的记忆。
- `(user_id,)`：单元素元组，用于绑定 SQL 参数。
- `fetchall()`：获取所有符合条件的记录。
将查询结果转换为字典：
```python
return {
    key: value
    for key, value in rows
}
```
该字典推导式把数据库中的每条记录转换为 `memory_key: memory_value`。例如：
```python
{
    "goal": "准备 AI Agent 实习",
    "primary_programming_language": "Python"
}
```
如果用户没有任何记录，则返回空字典 `{}`。
### 5. 删除指定记忆
```python
cursor.execute(
    """
    DELETE FROM user_memory
    WHERE user_id = ?
    AND memory_key = ?
    """,
    (user_id, key)
)
```
删除时同时指定 `user_id` 和 `memory_key`，只删除指定用户的指定类别，不影响其他用户或同一用户的其他记忆。
## 五、LLM 记忆判断
### 1. 初始化 DeepSeek
在 `llm.py` 中通过 `ChatOpenAI` 创建模型客户端：
```python
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()

llm = ChatOpenAI(
    model="deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1"
)
```
- `load_dotenv()`：读取 `.env` 配置。
- `os.getenv("DEEPSEEK_API_KEY")`：从环境变量读取 API Key，避免将密钥硬编码在源码中。
- `model`：指定使用的模型。
- `base_url`：指定 DeepSeek API 地址。
创建 `llm` 对象只完成客户端初始化；实际请求发生在调用 `llm.invoke(prompt)` 时。
### 2. 记忆类别白名单
```python
ALLOWED_MEMORY_KEYS = {
    "goal",
    "primary_programming_language",
    "interest",
    "project"
}
```
使用固定的记忆类别，减少模型生成任意键名导致的重复分类问题。
- `goal`：长期目标。
- `primary_programming_language`：主要编程语言。
- `interest`：长期兴趣。
- `project`：项目信息。
模型负责理解自然语言并选择类别，Python 负责校验返回的键名是否在白名单中。
### 3. 记忆操作类型
`judge_memory_action(user_input, current_memory)` 将用户输入与当前记忆交给 LLM，要求模型返回 JSON 决策。
| action | 含义 |
|---|---|
| `save` | 新增记忆或更新已有记忆 |
| `delete` | 用户明确要求删除某条记忆 |
| `ignore` | 一次性请求、无须保存的信息或无需重复修改的内容 |
模型决策示例：
```json
{
  "action": "save",
  "key": "primary_programming_language",
  "value": "Python",
  "reason": "用户明确更新了主要编程语言"
}
```
### 4. JSON 解析与校验
模型返回的 JSON 最初是文本，需要先解析：
```python
content = response.content.strip()
decision = json.loads(content)
```
- `response.content`：读取模型返回的正文。
- `strip()`：去掉字符串开头和结尾的空白字符。
- `json.loads()`：把合法 JSON 字符串转换成 Python 字典。
解析后进行规则校验：
1. `action` 必须属于 `save`、`delete`、`ignore`。
2. 对 `save` 和 `delete`，`key` 必须属于 `ALLOWED_MEMORY_KEYS`。
3. 对 `save`，`value` 必须是非空字符串。
校验的目的，是避免模型直接生成不符合预期的操作类型或记忆键。JSON 格式错误、字段缺失等情况仍需要进一步完善异常处理。
## 六、Memory Service：完整业务流程
`memory_service.py` 是 Day8 的业务核心，负责连接 LLM 判断和 SQLite 操作。
```python
def manage_memory(user_id, user_input):
    current_memory = get_memory(user_id)
    decision = judge_memory_action(user_input, current_memory)
    action = decision["action"]
    key = decision.get("key")
    value = decision.get("value", "")

    if action == "save":
        save_memory(user_id, key, value)
        message = f"已保存或更新记忆：{key} = {value}"

    elif action == "delete":
        if key not in current_memory:
            message = f"当前没有找到这条记忆：{key}"
        else:
            delete_memory(user_id, key)
            message = f"已删除记忆：{key}"

    else:
        message = "本次输入不需要修改长期记忆"

    return {
        "action": action,
        "reason": decision.get("reason", ""),
        "message": message,
        "current_memory": get_memory(user_id)
    }
```
执行逻辑：
1. `get_memory(user_id)`：读取当前用户已有记忆。
2. `judge_memory_action(...)`：根据新输入和已有记忆获取模型决策。
3. 读取 `action`、`key`、`value`。
4. 如果是 `save`，调用 `save_memory()` 新增或覆盖记忆。
5. 如果是 `delete`，先确认该键存在，再调用 `delete_memory()`。
6. 如果是 `ignore`，不修改数据库，只生成提示信息。
7. 最后再次调用 `get_memory()`，获取操作完成后的最新状态。
返回值包含四个字段：
- `action`：操作类型。
- `reason`：模型判断理由。
- `message`：操作结果说明。
- `current_memory`：数据库中的最新记忆。
这里的关键设计是：模型只负责提出决策，真正的数据库操作由 Python 代码执行。
## 七、LangGraph 状态与节点
### 1. State：`state.py`
```python
from typing_extensions import TypedDict

class MemoryState(TypedDict):
    user_id: str
    user_input: str
    operation_result: dict
```
`TypedDict` 用于描述状态字典的结构：
- `user_id`：用户标识。
- `user_input`：本轮用户输入。
- `operation_result`：记忆管理业务的返回结果。
它主要用于类型提示和静态检查，不等于运行时自动校验所有字段。
### 2. Node：`nodes.py`
```python
from state import MemoryState
from memory_service import manage_memory

def memory_node(state: MemoryState):
    print("执行memory_node")
    user_id = state["user_id"]
    user_input = state["user_input"]

    result = manage_memory(
        user_id=user_id,
        user_input=user_input
    )

    return {"operation_result": result}
```
执行逻辑：
1. LangGraph 将当前 State 传入 `memory_node()`。
2. 从 State 中读取 `user_id` 和 `user_input`。
3. 调用 `manage_memory()` 执行记忆管理业务。
4. 将业务返回值放入 `operation_result`。
`return {"operation_result": result}` 是关键：它告诉 LangGraph 更新哪个状态字段。这里的 `result` 是业务结果，而外层字典是节点提交给 LangGraph 的状态更新。
### 3. Graph：`graph.py`
```python
from langgraph.graph import StateGraph, START, END
from state import MemoryState
from nodes import memory_node

graph = StateGraph(MemoryState)
graph.add_node("memory", memory_node)
graph.add_edge(START, "memory")
graph.add_edge("memory", END)
app = graph.compile()
```
- `StateGraph(MemoryState)`：创建使用 `MemoryState` 的工作流。
- `add_node("memory", memory_node)`：注册节点，将节点名称映射到 Python 函数。
- `add_edge(START, "memory")`：设置入口。
- `add_edge("memory", END)`：设置出口。
- `compile()`：编译工作流，得到可执行应用 `app`。
当前工作流结构为：
```text
START → memory_node → END
```
目前只有一个业务节点，尚未添加条件路由或多节点分支。
## 八、测试程序与运行逻辑
`test_graph.py` 导入编译好的应用：
```python
from graph import app

user_id = "day8_graph_test"

test_inputs = [
    "我正在准备 AI Agent 实习",
    "我主要使用 Java 开发",
    "我现在主要使用 Python 开发",
    "请忘记我的主要编程语言偏好",
    "帮我计算一下 1 + 1"
]
```
`user_id` 固定为 `day8_graph_test`，所以每次测试都使用同一个用户的数据库记录。已有记忆会影响模型的判断，因此重复运行时的输出不一定与第一次完全相同。
循环调用工作流：
```python
for user_input in test_inputs:
    result = app.invoke({
        "user_id": user_id,
        "user_input": user_input,
        "operation_result": {}
    })

    operation_result = result["operation_result"]
    print("操作类型：", operation_result["action"])
    print("操作说明：", operation_result["message"])
    print("当前记忆：", operation_result["current_memory"])
```
- `for`：逐条处理测试输入。
- `app.invoke(...)`：启动一次 LangGraph 工作流执行。
- 初始 State 包含用户 ID、用户输入和空的 `operation_result`。
- `result`：接收工作流最终返回的 State。
- `result["operation_result"]`：提取业务节点返回的结果。
- 最后打印操作类型、说明和当前记忆。
每次 `app.invoke()` 都会执行一次工作流，但因为使用相同的 `user_id`，不同轮次可以通过 SQLite 读取到之前保存的记忆。
## 九、测试场景与结果
| 测试输入 | 预期行为 | 实际验证重点 |
|---|---|---|
| 我正在准备 AI Agent 实习 | `ignore` 或避免重复保存 | 已有目标记忆可被识别 |
| 我主要使用 Java 开发 | `save` | 新增编程语言记忆 |
| 我现在主要使用 Python 开发 | `save` | 使用相同键覆盖 Java |
| 请忘记我的主要编程语言偏好 | `delete` | 删除指定键 |
| 帮我计算一下 1 + 1 | `ignore` | 不把一次性请求写入长期记忆 |
测试过程中，程序最终成功执行，退出代码为 `0`。模型的具体判断可能受到数据库已有记录和模型输出影响，表格描述的是本次测试的目标行为，而非所有情况下的固定结果。
## 十、开发过程中遇到的问题
### 1. SQLite 建表语句不完整
曾出现 `sqlite3.OperationalError: incomplete input`，原因是 `CREATE TABLE` SQL 语句缺少结束括号。修复后表结构可以正常初始化。
### 2. 查询参数缺失
`get_memory()` 的 SQL 使用了 `WHERE user_id = ?`，但执行时未传入 `(user_id,)`。补上参数绑定后，查询正常。
### 3. Pydantic 与 LangGraph 依赖冲突
最初出现：
```text
ImportError: cannot import name 'PydanticDeprecationWarning' from 'pydantic'
```
检查发现当前 LangGraph、LangChain 和 FastAPI 需要 Pydantic 2.x，而环境中安装的是 Pydantic 1.10.26。将 Pydantic 升级到 2.x 后，`from langgraph.graph import StateGraph, START, END` 成功导入。
`pip check` 仍报告 `typeddict 0.3.0` 与 Pydantic 2.x 的版本约束冲突。虽然当前 LangGraph 测试已通过，但这个残留依赖冲突仍应在后续环境整理时处理。
### 4. `compile()` 拼写错误
曾将 `graph.compile()` 写成 `graph.complie()`，导致 `AttributeError`。修正方法名后工作流可以编译。
### 5. LangGraph 返回值缺少 `operation_result`
测试时曾出现 `KeyError: 'operation_result'`。检查实际 State 后，统一了 `MemoryState` 的字段定义和节点的返回结构：
```python
return {"operation_result": result}
```
修复后，LangGraph 能够正常返回操作结果。
## 十一、运行方式
在项目虚拟环境中安装所需依赖，并配置 `.env` 中的 `DEEPSEEK_API_KEY`。然后在 Day8 目录运行：
```powershell
python test_memory_service.py
python test_graph.py
```
- `test_memory_service.py`：验证业务层记忆操作。
- `test_graph.py`：验证记忆管理服务与 LangGraph 的集成。
注意：本项目使用 SQLite 本地文件保存长期记忆。运行测试可能会改变数据库内容；因为测试用户 ID 固定，重复执行前应注意已有数据对测试结果的影响。
## 十二、Day8 总结
Day8 将 Day7 的长期记忆从“能够保存和读取”扩展为“能够判断、更新、覆盖、删除和忽略”。
核心架构：
```text
LLM：理解用户输入并给出操作决策
        ↓
Memory Service：组织业务逻辑
        ↓
Memory Manager：执行 SQLite 增删改查
        ↓
LangGraph：管理状态传递与工作流执行
```
本日掌握的关键概念：
- SQLite、SQL 参数绑定、联合主键
- `INSERT OR REPLACE` 的覆盖逻辑
- LLM JSON 输出、`json.loads()` 和白名单校验
- 业务层与数据库层的职责划分
- LangGraph State、Node、Edge、`compile()` 和 `invoke()`
- 节点通过返回字典更新工作流状态
当前完成的是独立的长期记忆管理工作流。后续 Day9 将继续学习多用户记忆隔离和会话管理，再将记忆管理能力逐步整合进完整聊天 Agent。