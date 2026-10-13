
# Day9–Day10：多用户、多会话长期记忆 Agent

## 一、项目简介

本项目基于 Python、LangGraph、DeepSeek API 和 SQLite，构建一个支持多用户、多会话的 AI 学习助手。

项目的核心目标是让 Agent 不仅能够回答当前问题，还能够：

- 在同一个会话中保留短期对话历史。
- 将用户的长期偏好保存到 SQLite 数据库。
- 在不同会话中读取同一用户的长期记忆。
- 从用户输入中识别需要新增、更新或删除的长期记忆。
- 根据用户的长期偏好生成个性化回答。
- 通过 `user_id` 区分用户，通过 `thread_id` 区分会话。

本阶段是在 Day7 LangGraph Memory 和 Day8 Memory Management 的基础上进行整合。

## 二、技术栈

| 技术 | 用途 |
|---|---|
| Python | 项目主要开发语言 |
| LangGraph | 编排记忆管理、加载记忆和回答生成节点 |
| MemorySaver | 在当前 Python 进程中保存会话状态 |
| DeepSeek API | 提取记忆意图并生成回答 |
| langchain-openai | 使用兼容 OpenAI API 格式的客户端调用 DeepSeek |
| SQLite | 持久化用户长期记忆 |
| python-dotenv | 从 `.env` 文件加载 API 密钥 |
| Pydantic / JSON | 辅助解析和验证模型输出 |

## 三、项目架构

整体工作流如下：

```text
用户输入
   |
   v
manage_memory_node
   | 判断是否需要保存、删除或忽略长期记忆
   v
load_memory_node
   | 从 SQLite 读取当前 user_id 的长期记忆
   v
chat_node
   | 组合系统提示词、当前会话历史和当前问题
   | 调用 DeepSeek 生成回答
   v
返回回答和更新后的 State
```

### 两种记忆的区别

| 维度 | 短期记忆 | 长期记忆 |
|---|---|---|
| 保存内容 | 同一会话中的用户消息和 AI 回复 | 用户偏好、目标、项目等信息 |
| 标识方式 | `thread_id` | `user_id` |
| 存储方式 | LangGraph `MemorySaver` | SQLite |
| 不同会话是否共享 | 默认不共享 | 同一用户可以共享 |
| 程序重启后是否保留 | 不保留 | 保留在 SQLite 文件中 |

注意：`MemorySaver` 是内存型 Checkpointer。当前实现没有将短期对话历史持久化到磁盘，因此程序退出后，短期历史会丢失。

## 四、项目文件说明

| 文件 | 作用 |
|---|---|
| `main.py` | 项目运行入口，测试同一会话连续对话和新会话隔离 |
| `graph.py` | 创建 StateGraph，注册节点、连接执行边并配置 Checkpointer |
| `state.py` | 定义图运行时的状态字段 |
| `nodes.py` | 实现记忆管理、长期记忆加载和对话生成节点 |
| `memory_manager.py` | 封装 SQLite 长期记忆的初始化、保存、读取和删除 |
| `memory_filter.py` | 调用 LLM 判断记忆操作，并校验模型输出 |
| `memory_service.py` | 根据记忆判断结果执行保存、删除或忽略操作 |
| `llm.py` | 初始化 DeepSeek 模型客户端 |
| `test_thread.py` | 验证不同 thread 的短期状态是否隔离 |
| `test_long_term_memory.py` | 验证不同用户的长期记忆是否隔离 |
| `test_cross_thread_memory.py` | 验证同一用户的长期记忆能否跨会话读取 |
| `test_memory_service.py` | 验证长期记忆的识别和更新 |
| `test_personalized_chat.py` | 验证长期偏好是否影响模型回答 |
| `test_memory_isolation.py` | 验证删除一个用户的记忆不会影响另一个用户 |
| `check_memory_keys.py` | 检查指定用户的长期记忆字段 |
| `migrate_memory_key.py` | 将旧字段迁移为统一的字段名称 |
| `long_term_memory.db` | SQLite 长期记忆数据库，运行时自动创建 |

## 五、核心概念与代码原理

### 1. user_id 和 thread_id

两者承担不同的职责：

- `user_id` 用于标识用户，长期记忆根据用户 ID 读取。
- `thread_id` 用于标识会话，短期历史由 Checkpointer 按会话 ID 恢复。

同一个用户可以有多个会话。这些会话各自保留短期历史，但可以读取同一份长期记忆。

例如：

```python
user_id = "user_001"

thread_a = "thread_A"
thread_b = "thread_B"
```

`thread_A` 和 `thread_B` 的短期历史互相隔离，但都可以读取 `user_001` 的长期记忆。

在真实服务中，`user_id` 应由后端认证系统可信地确定，不能直接信任客户端任意提交的值。

### 2. State：图中节点共享的数据

`state.py` 使用 `TypedDict` 声明状态结构，主要字段包括：

- `user_id`：当前用户标识。
- `user_input`：本轮用户输入。
- `memory_action`：长期记忆管理结果。
- `long_term_memory`：从 SQLite 读取的长期记忆。
- `messages`：当前会话的短期消息历史。
- `answer`：本轮模型回答。

State 描述工作流中需要传递的数据。节点接收 State、执行逻辑，并返回需要更新的字段。

### 3. add_messages：累积对话消息

`messages` 使用 LangGraph 的 `add_messages` 作为消息合并规则。

对话节点只返回本轮新增的用户消息和 AI 消息，由 LangGraph 合并到已有历史中。

例如：

```text
第一轮：HumanMessage + AIMessage       共 2 条
第二轮：原来的 2 条 + 新增 2 条        共 4 条
```

这样，同一会话的下一轮就能够参考之前的对话上下文。

### 4. Checkpointer：恢复会话状态

`graph.py` 使用 `MemorySaver`，并将它传给：

```python
app = builder.compile(checkpointer=checkpointer)
```

调用 `app.invoke()` 时，通过以下配置指定会话：

```python
config = {
    "configurable": {
        "thread_id": thread_id
    }
}
```

相同的 `thread_id` 可以恢复同一会话的状态；新的 `thread_id` 会建立独立的短期历史。

当前使用的是内存型 Checkpointer，适合学习和本地验证。如果希望程序重启后仍能恢复短期会话，需要改用持久化 Checkpointer，例如 SQLite Checkpointer，并按其依赖和初始化要求配置。

### 5. SQLite：持久化长期记忆

长期记忆表 `user_memory` 的核心字段如下：

| 字段 | 含义 |
|---|---|
| `user_id` | 用户标识 |
| `memory_key` | 记忆类别 |
| `memory_value` | 记忆内容 |

主键为 `(user_id, memory_key)`，同一个用户的同一类记忆只保留一条记录。

主要操作：

- 保存：使用 `INSERT OR REPLACE` 保存或更新记忆。
- 读取：根据 `user_id` 查询该用户的记忆。
- 删除：同时使用 `user_id` 和 `memory_key` 限定删除范围。

数据库路径基于 Python 文件所在目录生成，避免依赖启动命令时的工作目录。

不要将本地数据库文件当作代码提交的必要内容。

### 6. LLM 记忆判断与规则校验

`memory_filter.py` 让模型判断当前输入应该执行哪种操作：

- `save`：保存或更新记忆。
- `delete`：删除指定记忆。
- `ignore`：无需修改长期记忆。

项目允许的记忆字段包括：

- `goal`
- `primary_programming_language`
- `interest`
- `project`
- `learning_style`

模型输出经过 JSON 解析，并检查操作类型、允许的字段以及记忆值。

这些校验能够减少格式错误和非法字段，但并不代表模型输出完全可靠。当前实现仍需要进一步完善异常处理、无效 JSON 重试、删除确认和敏感信息过滤等逻辑。

## 六、环境配置

### 1. 激活虚拟环境

在 Windows 命令提示符中进入项目目录：

```bat
cd /d C:\Users\zh136\AI-Agent-Learning
venv\Scripts\activate
```

### 2. 配置环境变量

在项目根目录的 `.env` 文件中配置：

```dotenv
DEEPSEEK_API_KEY=你的DeepSeek_API密钥
```

`llm.py` 使用 `python-dotenv` 读取该变量，并通过兼容 OpenAI API 格式的客户端调用 DeepSeek。

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

不要把真实 API 密钥写入代码或提交到 Git 仓库。

### 3. 安装依赖

如果当前虚拟环境已经安装了项目依赖，通常不需要重复安装。

本项目涉及的主要 Python 包包括：

```text
langgraph
langchain-core
langchain-openai
python-dotenv
typing-extensions
```

建议在当前已验证的虚拟环境中运行，不要为了清除无关的依赖告警而随意升级全部包。

## 七、运行项目

确认 `.env` 中已配置有效的 `DEEPSEEK_API_KEY`，然后运行：

```bat
cd /d C:\Users\zh136\AI-Agent-Learning\day9_Multi_User_Memory
..\venv\Scripts\python.exe main.py
```

如果虚拟环境路径不同，请将命令中的路径改为实际路径。

`main.py` 依次测试：

1. 在 `thread_memory_test` 中询问 LangGraph 的 State。
2. 在同一个 `thread_memory_test` 中继续询问 State 和 Node 的区别。
3. 在新的 `thread_new_test` 中询问另一个会话里说过什么。

程序会输出用户输入、记忆操作、当前长期记忆、当前会话消息数和 AI 回答。

## 八、已验证的测试结果

以下结果来自开发过程中实际运行过的测试。

| 测试 | 结果 |
|---|---|
| `test_thread.py`：不同 thread 的短期状态隔离 | 已通过 |
| `test_long_term_memory.py`：不同用户的长期记忆隔离 | 已通过 |
| `test_cross_thread_memory.py`：同一用户跨会话读取长期记忆 | 已通过 |
| `test_memory_service.py`：提取并更新学习偏好 | 已通过 |
| `test_personalized_chat.py`：根据偏好生成回答 | 已通过 |
| `test_memory_isolation.py`：删除一个用户的记忆不影响另一个用户 | 已通过 |
| `migrate_memory_key.py`：迁移旧记忆字段 | 已通过 |
| `main.py`：同一会话连续对话 | 已通过 |
| `main.py`：新会话读取同一用户的长期记忆 | 已通过 |

`main.py` 的关键观察结果：

- 第一轮消息数为 `2`。
- 同一会话第二轮消息数为 `4`。
- 新会话消息数为 `2`。
- 新会话能够读取同一用户的长期记忆，但不能直接读取另一个 thread 的短期聊天历史。

这些测试属于本地手动验证，不等于完整的自动化测试套件，也不代表项目已达到生产部署标准。

## 九、已知限制与后续改进

1. **短期记忆尚未持久化**：当前使用 `MemorySaver`，Python 进程退出后短期历史会丢失。后续可以研究持久化 Checkpointer。
2. **LLM 输出可能异常**：JSON 解析失败、模型输出缺少字段或 API 调用失败时，还需要完善错误处理和重试策略。
3. **记忆管理需要安全边界**：删除操作可以考虑二次确认；还应增加敏感信息过滤、输入验证和可信用户身份校验。
4. **当前是学习项目**：尚未完整实现用户认证、并发控制、权限管理、日志、监控和生产部署。
5. **测试需要自动化**：后续可以使用 `pytest` 将多用户隔离、会话隔离、记忆更新和删除行为整理成可重复运行的测试。
6. **长期记忆检索策略可以继续改进**：当前以键值形式存储用户记忆，后续可以探索记忆冲突处理、过期策略和更复杂的记忆检索机制。

## 十、Day9–Day10 学习总结

通过本阶段项目，完成了以下学习目标：

- 理解 `user_id` 和 `thread_id` 的区别。
- 使用 LangGraph `MemorySaver` 管理同一会话的短期状态。
- 使用 `add_messages` 累积消息历史。
- 使用 SQLite 保存用户长期记忆。
- 将 LLM 记忆判断、数据库操作和回答生成整合为 LangGraph 工作流。
- 验证同一用户跨会话共享长期记忆、不同会话隔离短期历史。
- 根据长期偏好生成个性化回答。

本项目建立了一个可继续扩展的记忆 Agent 基础。后续可以在此基础上继续学习企业级 RAG、工具调用、Agent 工程化和 Java AI 应用开发。
