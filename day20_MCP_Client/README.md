# Day20 MCP Client：LangChain Agent 接入 MCP Server

## 一、学习目标

- 使用 MCP Client 连接独立 MCP Server。
- 掌握 `MultiServerMCPClient` 的基本用法。
- 动态发现 MCP Server 提供的工具。
- 将 MCP Tool 转换为 LangChain Tool。
- 实现 DeepSeek Agent 自动选择和调用 MCP 工具。

## 二、核心知识点

| 技术 | 作用 |
|---|---|
| MultiServerMCPClient | 管理 MCP Server 连接 |
| get_tools() | 动态发现 MCP 工具 |
| LangChain Agent | 理解用户需求并选择工具 |
| ainvoke() | 异步调用 Agent |
| asyncio | 管理 Python 异步执行 |

## 三、核心代码

### 1. MCP Client 配置

```python
mcp_client = MultiServerMCPClient({
    "order_mcp_server": {
        "transport": "stdio",
        "command": str(PYTHON_EXE),
        "args": [str(MCP_SERVER_SCRIPT)]
    }
})
```

通过 STDIO 启动 Day19 的 MCP Server，建立本地进程通信。

### 2. 动态发现工具

```python
tools = await mcp_client.get_tools()
```

Client 自动获取 Server 提供的工具信息，并转换成 LangChain Tool 对象，无需在 Agent 中重复定义业务工具。

### 3. 创建 Agent

```python
agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt="根据用户需求选择工具，依据工具结果回答。"
)
```

### 4. 异步调用

```python
result = await agent.ainvoke({
    "messages": [
        {"role": "user", "content": question}
    ]
})
```

使用 `ainvoke()` 异步执行 Agent，通过 `asyncio.run(main())` 启动异步程序。

## 四、执行流程

1. 初始化 DeepSeek 模型。
2. 配置 MCP Server 的 Python 解释器和脚本路径。
3. 创建 MultiServerMCPClient。
4. 调用 get_tools() 动态发现 MCP 工具。
5. 将工具列表交给 LangChain Agent。
6. Agent 根据用户需求选择工具。
7. MCP Client 将工具调用请求发送给 MCP Server。
8. Server 执行业务逻辑并返回结果。
9. Agent 汇总工具结果并生成最终回答。

## 五、为什么使用 MCP？

传统方式通常需要在不同 Agent 应用中分别定义和适配工具。

使用 MCP 后，可以将业务能力独立部署为 MCP Server，由不同兼容 MCP 的 AI 应用通过 Client 接入。

主要优势：

- 标准化：统一工具发现和调用方式。
- 解耦：业务服务不必直接依赖某一个 Agent 框架。
- 复用：多个兼容 MCP 的应用可以接入同一个 Server。
- 扩展：新增工具可以由 Server 独立提供。

## 六、技术优势与应用价值

MCP Client 让 Agent 不需要了解工具的内部实现，只需要通过工具名称、描述和参数 Schema 使用外部能力。

结合 Redis 和 MySQL，可以实现业务工具与底层数据服务的分离：

- MCP：解决工具标准化接入和复用。
- Redis：缓存热点数据，减少数据库重复查询。
- MySQL：保存业务数据。
- LangChain Agent：负责理解需求和选择工具。

## 七、测试结果

| 测试项目 | 实际结果 |
|---|---|
| MCP 工具发现 | 成功发现 query_order、calculate_order |
| 订单查询 | A1001，已发货，199元 |
| 金额计算 | 160.00元 |
| 普通闲聊 | 未调用工具 |
| 多工具调用 | 一次请求成功调用两个工具 |
| Redis 缓存 | 成功命中缓存 |

## 八、学习总结

本次实现了 LangChain Agent 与独立 MCP Server 的集成。通过 MultiServerMCPClient 动态发现 MCP 工具，并将其交给 Agent 使用，实现了订单查询、金额计算和多工具协作。理解了 MCP 在业务工具标准化、跨应用复用和架构解耦方面的价值。

## 九、面试表达

MCP Client 负责连接 MCP Server，并动态获取服务端提供的 Tools、Resources 等能力。本项目使用 langchain-mcp-adapters 将 MCP Tools 转换为 LangChain 可用的工具，再交给 Agent 自动选择和调用。这样可以将业务工具独立部署，降低 Agent 应用与具体业务实现之间的耦合，提高工具的复用性和扩展性。