# Day6 LangGraph Workflow Agent

# 今日目标

学习 LangGraph 工作流框架，实现一个基于 LLM Router 的多任务 Agent。

完成内容：

- LangGraph State 状态管理
- Node 节点设计
- Edge 流程控制
- Conditional Edge 条件路由
- LLM 智能路由
- 多任务 Workflow Agent

最终实现：

用户输入

↓

LLM 判断用户需求

↓

选择对应业务节点

↓

调用 LLM 生成答案


# 项目结构

day6_langgraph_agent

├── graph.py              # LangGraph工作流定义
├── state.py              # State状态定义
├── nodes.py              # 业务节点
├── router.py             # 条件路由
├── router_llm.py         # LLM意图识别
├── tools.py              # 工具函数
├── llm.py                # 模型初始化
└── test_graph.py         # 测试文件


# 1. LangGraph简介

LangGraph 是基于 LangChain 的工作流框架。

相比传统 Agent：

传统 Agent：

用户输入

↓

LLM 自主决定

↓

调用工具


LangGraph：

用户输入

↓

Workflow流程控制

↓

Node节点执行

↓

LLM生成答案


LangGraph 优势：

- 流程更加可控
- 支持复杂任务拆分
- 支持多节点协作
- 适合企业级 Agent 开发


# 2. State状态管理

State 用于保存整个 Graph 运行过程中的数据。

例如：

```python
class TravelState(TypedDict):
    user_input:str
    city:str
    intent:str
    weather:str
    attractions:list
    answer:str
```

每个节点都会读取和修改 State。

流程：

用户输入

↓

State保存信息

↓

Node修改状态

↓

下一个Node继续使用


# 3. Node节点

Node 是 Graph 中的执行单元。

每个 Node 本质上是一个函数：

```python
def weather_node(state):

    state["weather"] = "杭州今天晴天"

    return state
```

Node 接收：

State

↓

处理任务

↓

返回新的State


本项目主要节点：


## router节点

作用：

使用 LLM 判断用户需求。


例如：

用户：

明天去杭州需要带外套吗


LLM判断：

weather


然后进入天气查询节点。


## weather_node

作用：

处理天气相关任务。

输入：

用户问题


输出：

```python
state["weather"]
```


## attraction_node

作用：

查询旅游景点信息。

输出：

```python
state["attractions"]
```


## travel_node

作用：

为旅游规划准备数据。


输出：

天气：

杭州未来三天天气晴朗，20-28度


景点：

```python
[
"西湖",
"灵隐寺",
"西溪湿地"
]
```


## answer_node

作用：

调用 DeepSeek 生成最终回答。

根据不同任务生成：

- 天气建议
- 景点介绍
- 旅游方案


# 4. Edge流程控制

Edge 用于连接不同 Node。


例如：

```python
graph.add_edge(
    "weather",
    "answer"
)
```


表示：

weather节点执行完成后进入answer节点。


本项目流程：


天气任务：

weather_node

↓

answer_node


景点任务：

attraction_node

↓

answer_node


旅游任务：

travel_node

↓

answer_node


# 5. Conditional Edge条件路由

Conditional Edge 根据返回结果选择不同路径。


代码：

```python
graph.add_conditional_edges(
    "router",
    route_question,
    {
        "weather":"weather",
        "attraction":"attraction",
        "travel":"travel"
    }
)
```


作用：

根据 LLM 判断结果进入不同节点。


例如：

用户：

杭州天气怎么样


LLM判断：

weather


流程：

router

↓

weather_node

↓

answer_node



用户：

杭州有哪些景点


LLM判断：

attraction


流程：

router

↓

attraction_node

↓

answer_node



用户：

帮我规划杭州三日游


LLM判断：

travel


流程：

router

↓

travel_node

↓

answer_node


# 6. LLM智能路由

本项目使用 DeepSeek 作为意图识别模型。


流程：

用户输入

↓

LLM分析

↓

生成intent


例如：

```python
intent="travel"
```


LangGraph 根据 intent 自动选择对应节点。


相比传统判断：

```python
if "天气" in message:
```

LLM 可以理解自然语言。


例如：

以下问题都会判断为 weather：

- 杭州今天冷吗
- 需要带外套吗
- 明天会不会下雨


# 7. 最终Workflow结构


用户输入

↓

LLM Router

↓

判断用户意图


↓

----------------

weather_node

attraction_node

travel_node

----------------


↓

answer_node

↓

END


# 8. 测试结果


## 测试1：天气任务

输入：

明天去杭州玩，要带外套吗


输出：

llm判断意图 weather

执行天气查询节点

执行答案生成节点



## 测试2：景点任务

输入：

杭州有哪些景点


输出：

llm判断意图 attraction

执行景点查询节点

执行答案生成节点



## 测试3：旅游规划任务

输入：

帮我规划杭州三日游


输出：

llm判断意图 travel

执行旅游规划节点

执行答案生成节点


# 9. 今日总结

Day6 完成了从普通 Agent 到 Workflow Agent 的升级。


掌握：

- LangGraph基础结构
- State状态管理
- Node节点设计
- Edge流程控制
- Conditional Routing
- LLM Router
- 多任务Workflow设计


最终实现：

用户输入

↓

LLM理解需求

↓

自动选择任务流程

↓

业务节点执行

↓

LLM生成回答


# 下一步

Day7：

LangGraph Memory


学习：

- Checkpoint
- 持久化Memory
- 多轮对话
- 用户偏好记忆