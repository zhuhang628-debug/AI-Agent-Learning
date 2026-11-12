# Day19 MCP Server：独立业务工具服务

## 一、学习目标

- 使用官方 MCP Python SDK 创建 MCP Server。
- 掌握 FastMCP 和 `@mcp.tool()`。
- 将 Python 函数注册为 MCP Tool。
- 使用 MCP Inspector 测试工具发现与调用。
- 将 Redis、MySQL 业务能力封装为 MCP 服务。

## 二、核心知识点

| 知识点 | 作用 |
|---|---|
| FastMCP | 创建 MCP Server |
| `@mcp.tool()` | 注册 MCP 工具 |
| `mcp.run()` | 启动 MCP Server |
| STDIO | 本地进程通信 |
| MCP Inspector | 可视化调试 MCP 服务 |
| Tool Discovery | 发现 Server 提供的工具 |
| Tool Calling | 调用 MCP 工具并获取结果 |

## 三、实现的工具

| 工具 | 功能 |
|---|---|
| query_order | 优先查询 Redis，未命中时查询 MySQL |
| calculate_order | 根据单价、数量和折扣计算订单金额 |

## 四、执行流程

1. 使用 FastMCP 创建 MCP Server。
2. 通过 `@mcp.tool()` 注册业务工具。
3. 使用 STDIO 启动 Server。
4. 使用 MCP Inspector 连接 Server。
5. 发现工具并查看参数 Schema。
6. 调用工具，获取执行结果。

## 五、测试结果

| 测试项目 | 结果 |
|---|---|
| MCP Server 连接 | 成功 |
| 工具发现 | 成功发现两个工具 |
| 订单查询 A1001 | 已发货，199.00 元 |
| 订单金额计算 | 160.00 元 |
| Redis + MySQL 查询 | 成功 |

## 六、学习总结

本次使用官方 MCP Python SDK 创建了独立 MCP Server，将订单查询和金额计算封装为 MCP Tool，并通过 MCP Inspector 完成工具发现和调用测试。理解了 MCP Server 与 LangChain Tool 的区别，掌握了通过标准化协议向外部 AI 应用提供业务能力的基本方法。