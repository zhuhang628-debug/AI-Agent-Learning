# Day21：Agent Skills

## 一、学习目标

理解 Agent Skills 的基本原理，实现 Skill 文件的创建、加载和 Agent 按需调用，并将 Skills 与 MCP 工具结合，完成真实订单分析。

## 二、核心概念

### 1. Agent Skills

Skill 是一种可复用的任务知识与操作规范封装方式，通常以 `SKILL.md` 文件作为核心。

主要包含：
- 适用场景
- 任务执行步骤
- 业务规则
- 输出要求
- 注意事项

Skill 本身不直接执行 Python 代码，而是向 Agent 提供完成特定任务所需的知识和规范。

### 2. Skill、Tool 和 MCP 的区别

| 技术 | 作用 | 示例 |
|---|---|---|
| Skill | 提供任务知识和执行规范 | 如何分析订单 |
| Tool | 提供可调用的实际能力 | 查询订单 |
| MCP | 标准化连接外部工具的协议 | 连接订单 MCP Server |

三者可以组合使用：Skill 告诉 Agent 怎么做，Tool 提供实际执行能力，MCP 负责标准化连接。

## 三、项目结构

```text
day21_Agent_Skills/
├── skills/
│   └── order-analysis/
│       └── SKILL.md
├── skill_loader.py
└── skill_agent.py
```

## 四、核心代码

### 1. Skill 加载器

```python
from pathlib import Path
from langchain.tools import tool

BASE_DIR = Path(__file__).resolve().parent
SKILLS_DIR = BASE_DIR / "skills"

@tool
def load_skill(skill_name: str) -> str:
    """根据 Skill 名称加载对应的 SKILL.md 文件。"""

    if not skill_name or Path(skill_name).name != skill_name:
        return "错误：Skill 名称不合法"

    skill_path = SKILLS_DIR / skill_name / "SKILL.md"

    if not skill_path.is_file():
        return f"错误：没有找到名为 {skill_name} 的 Skill"

    return skill_path.read_text(encoding="utf-8")
```

技术作用：
- 使用 pathlib 管理文件路径。
- 使用 `read_text()` 读取 Markdown 文件。
- 使用 `@tool` 将 Python 函数封装为 LangChain Tool。
- 通过工具参数让 Agent 指定需要加载的 Skill。

### 2. Skill 与 MCP 工具组合

```python
mcp_client = MultiServerMCPClient({
    "order_mcp_server": {
        "transport": "stdio",
        "command": str(PYTHON_EXE),
        "args": [str(MCP_SERVER_SCRIPT)]
    }
})

mcp_tools = await mcp_client.get_tools()

tools = [load_skill] + mcp_tools

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt="..."
)
```

技术作用：
- `MultiServerMCPClient` 连接 MCP Server。
- `get_tools()` 动态获取 MCP Server 提供的工具。
- 将 Skill 加载工具和 MCP 工具统一注册到 Agent。
- 模型根据任务决定调用哪些工具。

### 3. Agent 异步执行

```python
result = await agent.ainvoke({
    "messages": [
        {"role": "user", "content": question}
    ]
})
```

使用异步调用执行 Agent，等待模型和工具调用完成。

## 五、执行流程

1. 用户提出订单分析需求。
2. Agent 理解用户意图。
3. Agent 调用 `load_skill` 加载订单分析规范。
4. Agent 调用 MCP 工具 `query_order` 查询真实订单。
5. 获取数据库返回的订单数据。
6. 模型结合 Skill 规范与真实数据完成分析。
7. 输出最终结果。

## 六、测试结果

### 测试一：Skill 加载

成功读取 `order-analysis/SKILL.md`。

### 测试二：Skill 按需调用

订单分析任务成功触发 `load_skill`；普通聊天无需加载 Skill。

### 测试三：Skill + MCP

用户输入：

```text
帮我分析一下 A1001 订单，检查订单金额和状态是否存在异常。
```

工具调用记录：

```text
load_skill
query_order
```

MCP 查询结果：

- 订单编号：A1001
- 订单状态：已发货
- 订单金额：199.00 元
- 用户 ID：1
- 数据来源：MySQL

最终分析：
- 订单总数：1
- 订单总金额：199.00 元
- 订单金额大于 0
- 订单编号和状态均不缺失
- 未发现 Skill 定义范围内的异常

## 七、技术优势

1. **模块化：** 将不同业务任务的知识和规则独立封装。
2. **可复用：** 同一个 Skill 可以被不同 Agent 任务加载。
3. **按需加载：** 避免将所有业务规范长期放在 System Prompt 中。
4. **职责分离：** Skill 管理任务知识，Tool 执行实际操作，MCP 负责外部能力连接。
5. **易扩展：** 可以增加订单分析、退款处理、客户服务等不同 Skill。

## 八、当前实现的局限

当前实现属于简化版 Skills 加载机制：
- 需要手动编写 Skill 名称。
- 尚未实现 Skill 自动发现和元数据筛选。
- 尚未实现 references、scripts、assets 等资源的完整加载。
- Skill 的使用效果依赖模型是否正确选择和遵循。

## 九、学习总结

本次学习掌握了 Agent Skills 的基本思想，使用 Markdown 文件封装订单分析规范，通过 pathlib 实现 Skill 加载，并利用 LangChain `@tool` 将加载能力交给 Agent。进一步结合 MCP 订单查询工具，实现了任务知识与真实业务数据的协同使用，完成了一个具备按需加载 Skill 和调用外部业务能力的订单分析 Agent。

## 十、面试表达

我学习并实践了 Agent Skills 的基本实现机制，将业务知识和操作规范封装为独立的 `SKILL.md` 文件，通过 Python 实现 Skill 加载器，并使用 LangChain Tool 将加载能力暴露给 Agent。同时结合 MCP 连接订单查询服务，使 Agent 能够根据用户任务加载对应 Skill、调用真实业务工具，并按照预设业务规范完成订单分析，实现了任务知识与外部工具能力的模块化组合。