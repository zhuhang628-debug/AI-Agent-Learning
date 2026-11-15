# Day23：LangGraph Multi-Agent 多智能体编排

## 一、学习目标

使用 LangGraph StateGraph 构建多智能体工作流，将 MCP 工具接入 Agent 节点，实现多个 Agent 之间的状态传递、顺序执行和条件路由。

## 二、核心知识

### 1. StateGraph

StateGraph 是 LangGraph 的图编排方式，通过 State、Node 和 Edge 组织工作流。

- State：保存节点之间共享的数据。
- Node：执行具体任务的函数或 Agent。
- Edge：定义节点之间的执行关系。
- Conditional Edge：根据状态或业务条件动态决定下一步执行节点。

### 2. 多 Agent 协作

本项目设计了三个节点：

- Order Agent：识别订单编号，通过 MCP 查询真实订单。
- Analysis Agent：分析订单金额、状态、数据完整性及异常。
- Error Agent：处理订单查询失败的情况，并向用户提供处理建议。

### 3. MCP 集成

使用 MultiServerMCPClient 连接 Day19 实现的 MCP Server，动态获取工具，并调用 query_order 查询订单。

业务查询链路：

LangGraph → Order Agent → MCP Client → MCP Server → Redis / MySQL。

### 4. 条件路由

使用 add_conditional_edges() 根据订单查询状态选择执行路径：

- success：进入 Analysis Agent。
- failed：进入 Error Agent。

核心代码：

```python
builder.add_conditional_edges(
    "order_agent",
    route_order,
    {
        "success": "analysis_agent",
        "failed": "error_agent"
    }
)
```

## 三、系统执行流程

用户输入问题后，Order Agent 提取订单编号并调用 MCP 工具。

查询成功时，将真实订单数据写入共享 State，再交给 Analysis Agent。

查询失败时，通过 Conditional Edge 路由到 Error Agent，输出异常说明和处理建议。

## 四、测试结果

### 测试一：正常订单 A1001

- MCP 工具调用成功。
- Redis 返回订单数据。
- 订单金额：199.00 元。
- 订单状态：已发货。
- 成功进入 Analysis Agent 并输出分析报告。

### 测试二：不存在的订单 A9999

- MCP 返回订单不存在。
- 路由状态为 failed。
- 成功进入 Error Agent。
- 输出查询失败原因及处理建议。

两组测试均成功。

## 五、技术优势

1. 通过 State 实现多个节点之间的数据共享。
2. 通过 Graph 明确管理 Agent 的执行流程。
3. 通过 Conditional Edge 实现动态业务路由。
4. MCP 将业务工具与 Agent 编排层解耦。
5. 将正常业务分析与异常处理分离，提高工作流的可维护性。

## 六、当前不足

- 订单查询结果仍以字符串形式传递，尚未使用结构化数据模型。
- 缺少系统级超时、重试和完整异常分类。
- 尚未加入持久化 Checkpoint 和工作流恢复。
- 当前采用固定节点流程，尚未实现更复杂的并行协作。

## 七、学习总结

本阶段掌握了 LangGraph 在多智能体系统中的实际应用，完成了 StateGraph、共享 State、Node、Edge 和 Conditional Edge 的组合使用，并将此前开发的 MCP Server 接入工作流，实现了真实订单查询、订单分析和异常处理。

## 八、面试表达

在项目中使用 LangGraph 构建多智能体工作流，将订单查询、数据分析和异常处理拆分为独立节点。通过共享 State 在节点间传递订单数据，通过 Conditional Edge 根据业务执行结果动态路由。同时集成 MCP Server，实现对 Redis 和 MySQL 订单数据的真实查询，提高了系统的模块化程度和流程可控性。