# Day25：FastAPI + Agent 后端服务
## 一、项目介绍
本阶段基于 Day24 完成的 Agent Reliability 综合项目，使用 FastAPI 将 LangChain Agent 封装为 HTTP 后端服务，实现从本地 Agent 程序到 Web API 服务的转换。
通过 FastAPI 接收外部请求，调用 LangChain Agent 处理用户问题，并通过 MCP Client 连接 Day19 开发的 MCP Server，实现订单查询、金额计算等业务工具调用。
项目同时保留普通大模型对话接口与 Agent 对话接口，用于区分直接调用 LLM 和通过 Agent 调度工具的不同处理方式。
### 核心功能
- FastAPI 服务：搭建 AI Agent HTTP 后端服务。
- Swagger API 文档：通过 `/docs` 自动生成接口文档，支持在线调试。
- Pydantic 数据校验：定义请求参数和响应数据结构。
- MCP 工具接入：通过 MultiServerMCPClient 连接 MCP Server，动态获取业务工具。
- Agent 初始化：服务启动时加载 MCP 工具并创建 LangChain Agent。
- Agent 实例管理：通过 `app.state.agent` 保存 Agent 实例，供接口重复使用。
- 异步调用：使用 `ainvoke()` 实现模型和 Agent 的异步调用。
- 生命周期管理：通过 `lifespan` 管理服务启动时的工具加载和 Agent 初始化。
- 接口封装：分别实现健康检查、普通模型对话和 Agent 对话接口。
## 二、技术栈
| 技术 | 应用场景 |
|---|---|
| Python 3.10 | 项目开发语言 |
| FastAPI | Web 后端服务与 API 接口 |
| Uvicorn | ASGI 服务运行服务器 |
| Pydantic | 请求参数和响应数据校验 |
| LangChain 1.x | Agent 构建与调用 |
| DeepSeek API | 大语言模型服务 |
| langchain-openai | DeepSeek 模型接口接入 |
| MCP Python SDK | MCP Server 工具服务 |
| langchain-mcp-adapters | MCP Client 与 LangChain 工具集成 |
| Redis | 订单数据缓存 |
| MySQL | 订单数据存储 |
| python-dotenv | 环境变量配置管理 |
| Swagger UI | API 接口文档与在线测试 |
## 三、项目结构
```text
AI-Agent-Learning/
│
├── day19_MCP_Server/
│   └── order_mcp_server.py       # 订单 MCP Server
│
├── day24_Agent_Reliability/
│   ├── logs/
│   ├── reliability_agent.py       # Agent 可靠性模块
│   └── ...                        # 重试、超时、日志、安全等模块
│
├── day25_FastAPI/
│   ├── main.py                    # FastAPI 服务入口
│   └── logs/                      # 运行日志目录（如启用）
│
├── .env                           # 环境变量配置
├── requirements.txt               # 项目依赖
└── README.md                      # 项目学习记录
```
## 四、核心知识点
### 1. FastAPI 后端服务
FastAPI 是 Python 的现代 Web 框架，用于快速构建 HTTP API 服务。
本项目使用 FastAPI 将 Agent 封装为接口，使其他程序能够通过 HTTP 请求调用 Agent，而不需要直接运行 Python Agent 代码。
基本流程：
```text
用户 / 前端应用
      ↓
HTTP 请求
      ↓
FastAPI 路由
      ↓
Python 业务逻辑
      ↓
Agent / LLM
      ↓
HTTP JSON 响应
```
### 2. Swagger 接口文档
FastAPI 自动生成 Swagger UI 接口文档。
启动服务后访问：
```text
http://127.0.0.1:8000/docs
```
可以查看接口说明、填写请求参数并执行测试。
常用操作：
- Try it out：进入接口测试模式。
- Execute：发送 HTTP 请求。
- Response body：查看接口返回的 JSON 数据。
Swagger 主要用于开发阶段的接口调试，不需要额外编写前端页面。
### 3. Pydantic 请求与响应模型
使用 Pydantic 定义统一的数据结构：
```python
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    answer: str
```
其中：
- ChatRequest：定义客户端发送的数据格式。
- ChatResponse：定义后端返回的数据格式。
通过 Pydantic 可以对请求数据进行基础类型校验，并使接口输入输出更加规范。
### 4. FastAPI 生命周期管理
使用 `lifespan` 管理服务启动阶段的初始化任务。
```text
FastAPI 启动
     ↓
连接 MCP Server
     ↓
获取 MCP Tools
     ↓
创建 LangChain Agent
     ↓
保存 Agent 实例
     ↓
服务开始接收请求
```
核心代码：
```python
tools = await mcp_client.get_tools()
agent = create_reliability_agent(tools)
app.state.agent = agent
```
通过这种方式，在服务启动时完成工具加载和 Agent 创建，避免每次用户请求都重复初始化 Agent。
### 5. MCP Client 与 Agent 集成
使用 `MultiServerMCPClient` 连接已有的订单 MCP Server。
```text
FastAPI
   ↓
MCP Client
   ↓
MCP Server
   ↓
query_order / calculate_order
   ↓
Redis / MySQL
```
MCP Client 负责连接 MCP Server 并获取可用工具，再将工具交给 LangChain Agent。
Agent 根据用户问题判断是否需要调用工具，并根据工具返回结果组织最终回答。
### 6. Agent 实例管理
通过：
```python
app.state.agent = agent
```
将初始化完成的 Agent 保存到 FastAPI 应用状态中。
接口处理请求时：
```python
agent = app.state.agent
```
即可获取已经创建好的 Agent。
这样可以实现 Agent 实例的复用，避免每次请求都重新创建。
### 7. 异步调用
项目使用 `async def` 定义异步接口，并使用 `await` 等待异步任务完成。
例如：
```python
result = await agent.ainvoke({
    "messages": [
        {"role": "user", "content": request.message}
    ]
})
```
其中：
- `ainvoke()`：异步调用 LangChain Agent。
- `await`：等待异步任务执行完成并获取结果。
- `result`：保存 Agent 执行结果。
异步调用有利于提高后端服务处理 I/O 密集型任务时的资源利用效率。
## 五、API 接口设计
本项目提供三个 HTTP 接口。
| 接口 | 请求方式 | 功能 |
|---|---|---|
| `/health` | GET | 检查服务运行状态 |
| `/chat` | POST | 直接调用 DeepSeek 模型进行普通对话 |
| `/agent/chat` | POST | 调用 LangChain Agent，支持 MCP 工具调度 |
### 1. 健康检查接口
请求：
```http
GET /health
```
返回：
```json
{
    "status": "ok"
}
```
用于检查 FastAPI 服务是否正常运行。
### 2. 普通模型对话接口
请求：
```http
POST /chat
```
请求参数：
```json
{
    "message": "什么是 AI Agent？"
}
```
处理流程：
```text
用户问题
   ↓
FastAPI /chat
   ↓
DeepSeek LLM
   ↓
返回模型回答
```
该接口直接调用 `llm.ainvoke()`，不经过 Agent 工具调度流程。
### 3. Agent 对话接口
请求：
```http
POST /agent/chat
```
请求参数：
```json
{
    "message": "查询订单 A1001"
}
```
处理流程：
```text
用户问题
   ↓
FastAPI /agent/chat
   ↓
获取 app.state.agent
   ↓
LangChain Agent
   ↓
判断是否需要调用工具
   ↓
MCP Client
   ↓
MCP Server
   ↓
Redis / MySQL
   ↓
返回工具执行结果
   ↓
Agent 组织自然语言回答
   ↓
FastAPI 返回 JSON
```
与普通模型接口相比，Agent 接口具备业务工具调用能力，可以根据用户需求自主选择是否调用 MCP 工具。
## 六、项目整体架构
```text
             用户 / Swagger / 前端应用
                       |
                       | HTTP POST
                       ↓
                 FastAPI 服务
                       |
             ┌─────────┴─────────┐
             |                   |
          /chat              /agent/chat
             |                   |
             ↓                   ↓
         DeepSeek LLM       LangChain Agent
                                 |
                           MCP Client
                                 |
                           MCP Server
                                 |
                    ┌────────────┴────────────┐
                    |                         |
                query_order             calculate_order
                    |                         |
                    ↓                         ↓
                  Redis / MySQL 数据服务
                                 |
                                 ↓
                         Agent 组织回答
                                 |
                                 ↓
                         FastAPI 返回 JSON
```
## 七、运行与测试
### 1. 启动 Redis
订单 MCP Server 依赖 Redis 缓存和 MySQL 数据库，需要确保相关服务正常运行。
检查 Redis 容器：
```powershell
docker ps
```
如果 Redis 容器未运行，需要先启动对应容器。
### 2. 启动 FastAPI 服务
进入项目目录：
```powershell
cd C:\Users\zh136\AI-Agent-Learning\day25_FastAPI
```
启动命令：
```powershell
..\venv\Scripts\python.exe -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```
参数说明：
- `main:app`：加载 main.py 中的 FastAPI 实例。
- `--reload`：代码修改后自动重启服务。
- `--host 127.0.0.1`：监听本机地址。
- `--port 8000`：使用 8000 端口。
### 3. 访问 Swagger
```text
http://127.0.0.1:8000/docs
```
通过 Swagger 测试三个接口。
## 八、实际测试结果
| 测试场景 | 测试内容 | 测试结果 |
|---|---|---|
| 健康检查 | `/health` 服务状态检查 | 已实现 |
| 普通模型对话 | `/chat` 调用 DeepSeek | 测试通过 |
| Agent 普通问答 | 不涉及业务工具的问题 | 测试通过 |
| 订单查询 | 查询订单 A1001 | 测试通过 |
| 订单权限校验 | 用户 1 查询订单 A1003 | 测试通过，正确拒绝越权查询 |
| 金额计算 | 100 元 × 2 件，打八折 | 测试通过，结果为 160 元 |
| MCP 工具加载 | 加载 query_order、calculate_order | 测试通过 |
### 测试结果示例
订单查询：
```json
{
    "answer": "订单 A1001 查询结果：订单状态：已发货，订单金额：199.00 元，用户ID：1"
}
```
金额计算：
```text
原价：100 元
数量：2 件
折扣：20%
最终金额：160 元
```
## 九、Day25 学习总结
Day25 完成了从本地 Agent 程序到 HTTP 后端服务的封装，掌握了 FastAPI 的基本使用、接口设计、Pydantic 数据校验、Swagger 调试、异步调用和生命周期管理。
同时，将已有的 MCP Server 接入 FastAPI 项目，在服务启动时动态获取 MCP 工具并创建 LangChain Agent，实现了通过 HTTP 接口调用 Agent 的完整流程。
通过本阶段学习，进一步理解了 AI Agent 应用的后端服务架构，明确了 FastAPI、LangChain Agent、MCP Client 和 MCP Server 在整个系统中的职责与协作关系。
## 十、面试表达
在项目中使用 FastAPI 搭建 AI Agent 后端服务，通过 Pydantic 定义统一的请求和响应数据结构，并利用 Swagger 完成 API 接口调试。通过 lifespan 在服务启动阶段加载 MCP 工具并初始化 LangChain Agent，使用 app.state 管理 Agent 实例，实现 Agent 的复用。对外提供普通模型对话和 Agent 对话接口，其中 Agent 接口通过 MCP Client 连接订单 MCP Server，实现订单查询、权限校验和金额计算等业务功能，打通了从 HTTP 请求到 Agent 工具调用再到业务数据访问的完整链路。