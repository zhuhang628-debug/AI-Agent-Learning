# Day22：Multi-Agent 多智能体系统

## 一、学习目标

理解 Multi-Agent 多智能体架构，掌握 Supervisor、Order Agent、Analysis Agent 的分工协作，使用 LangChain `create_agent()` 创建多个独立 Agent，并通过 `@tool` 将专业 Agent 封装成工具，实现主管 Agent 动态分配任务。

## 二、核心概念

### 1. Multi-Agent

Multi-Agent 是由多个具有独立职责的 Agent 协同完成复杂任务的系统架构。

每个 Agent 可以拥有自己的：
- 大语言模型
- System Prompt
- Tools
- 执行逻辑

### 2. 三种常见架构

| 架构 | 核心思想 |
|---|---|
| Supervisor | 主管 Agent 分配任务并汇总结果 |
| Handoff | Agent 之间交接任务和控制权 |
| Parallel | 多个 Agent 并行执行独立任务 |

### 3. Agent as a Tool

将一个完整的 Agent 封装成 LangChain Tool，使另一个 Agent 可以通过工具调用委托任务。

这种方式可以实现专业 Agent 之间的分工协作。

## 三、项目架构

```text
day22_Multi_Agent/
└── multi_agent.py
```

系统结构：

```text
用户
  ↓
Supervisor Agent
  ├── order_specialist
  │       ↓
  │   Order Agent
  │       ↓
  │   MCP Tools
  │       ↓
  │   Redis / MySQL
  │
  └── analysis_specialist
          ↓
      Analysis Agent
          ↓
      数据分析结果
  ↓
Supervisor 汇总
  ↓
最终回答
```

## 四、核心代码

### 1. 创建专业 Agent

订单查询 Agent：

```python
order_agent = create_agent(
    model=llm,
    tools=mcp_tools,
    system_prompt="你是一名专业的订单查询 Agent..."
)
```

数据分析 Agent：

```python
analysis_agent = create_agent(
    model=llm,
    tools=[],
    system_prompt="你是一名专业的数据分析 Agent..."
)
```

两个 Agent 拥有独立职责和工具配置。

### 2. 将 Agent 封装成 Tool

```python
@tool
async def order_specialist(task: str) -> str:
    """委托订单专家查询订单信息。"""

    result = await order_agent.ainvoke({
        "messages": [
            {"role": "user", "content": task}
        ]
    })

    return extract_answer(result)
```

分析 Agent 同样通过 `@tool` 封装，将订单数据作为参数传入。

### 3. 创建 Supervisor

```python
supervisor = create_agent(
    model=llm,
    tools=[
        order_specialist,
        analysis_specialist
    ],
    system_prompt="负责协调订单查询和数据分析任务..."
)
```

Supervisor 根据用户需求决定调用哪个专业 Agent。

### 4. 执行 Supervisor

```python
result = await supervisor.ainvoke({
    "messages": [
        {"role": "user", "content": question}
    ]
})
```

使用异步接口执行整个多智能体协作流程。

## 五、执行流程

1. 用户提出业务需求。
2. Supervisor 理解任务。
3. 根据任务选择专业 Agent。
4. Order Agent 通过 MCP 查询真实订单。
5. Analysis Agent 接收订单数据并完成分析。
6. Supervisor 汇总专业 Agent 返回结果。
7. 输出最终回答。

## 六、测试结果

### 测试一：完整订单分析

输入：

```text
帮我分析一下 A1001 订单，检查订单金额和状态是否存在异常。
```

调用顺序：

```text
order_specialist
analysis_specialist
```

结果：
- 订单编号：A1001
- 订单状态：已发货
- 订单金额：199.00 元
- 数据来源：MySQL
- 未发现异常订单

### 测试二：只查询订单

输入：

```text
查询一下 A1001 订单的状态和金额。
```

调用：

```text
order_specialist
```

结果：
- 订单状态：已发货
- 订单金额：199.00 元
- 数据来源：Redis 缓存

未调用 Analysis Agent。

### 测试三：普通聊天

输入：

```text
你好，请介绍一下自己。
```

Supervisor 直接回答，没有调用专业 Agent。

## 七、技术优势

1. **职责分离：** 不同 Agent 负责不同领域的任务。
2. **模块化：** 可以独立维护专业 Agent 的提示词和工具。
3. **动态路由：** Supervisor 根据用户意图决定调用哪些专业 Agent。
4. **能力复用：** 可以将 Agent 封装成 Tool，供其他 Agent 调用。
5. **可扩展性：** 可以增加退款 Agent、报告 Agent 等专业角色。

## 八、当前实现的局限

1. 任务路由依赖模型决策和提示词，缺少严格的流程约束。
2. Agent 之间主要通过自然语言文本传递数据。
3. 缺少结构化数据校验和统一错误处理。
4. 当前采用 Supervisor 串行调用，尚未实现真正的并行协作。
5. 多 Agent 会增加模型调用次数、延迟和 Token 成本。

## 九、学习总结

本次学习掌握了 Multi-Agent 的基本架构，使用 LangChain `create_agent()` 创建 Order Agent、Analysis Agent 和 Supervisor Agent，并通过 `@tool` 将专业 Agent 封装为可调用工具，实现了主管 Agent 根据用户需求动态分配任务。系统结合 Day20 的 MCP 订单查询能力，完成了从真实订单查询到数据分析的完整业务流程。

## 十、面试表达

我基于 LangChain 1.x 实现了一个 Supervisor 多智能体订单分析系统。系统由主管 Agent、订单查询 Agent 和数据分析 Agent 组成，其中订单 Agent 通过 MCP 连接 Redis 和 MySQL 获取真实业务数据，分析 Agent 负责订单统计和异常判断。我将两个专业 Agent 封装为 LangChain Tool，由 Supervisor 根据用户意图动态选择和调用，实现了多智能体的任务路由、职责分离与结果汇总。