# Day24：Agent Reliability —— AI Agent 可靠性工程实践

## 一、项目介绍

本项目基于 LangChain 1.x、MCP 和 DeepSeek 构建了一个具备可靠性保障能力的 AI Agent 综合应用。

项目以订单查询和金额计算为业务场景，将 Agent 与 MCP 工具、MySQL 数据库和 Redis 缓存结合，实现了工具调用、参数校验、用户权限控制、异常处理、自动重试、超时控制和日志记录等功能。

项目重点不只是实现 Agent 的基本对话能力，而是解决 AI Agent 在实际业务运行中可能遇到的接口异常、请求超时、参数错误、权限越界和数据库访问等问题。

## 二、技术栈

| 技术 | 应用场景 |
|---|---|
| Python 3.10 | 项目开发语言 |
| LangChain 1.x | Agent 创建与工具调用 |
| DeepSeek API | 大语言模型 |
| MCP | Agent 与外部工具之间的通信 |
| FastMCP | MCP Server 开发 |
| MySQL | 订单业务数据存储 |
| Redis | 订单查询缓存 |
| Pydantic | 工具参数校验 |
| Tenacity | 异常重试与指数退避 |
| asyncio | 异步执行与超时控制 |
| Logging | 日志记录与异常追踪 |

## 三、项目架构

```text
用户输入
   |
   v
LangChain Agent
   |
   |---- DeepSeek API
   |
   v
MCP Client
   |
   v
MCP Server
   |
   |---- query_order
   |       |
   |       v
   |     Pydantic 参数校验
   |       |
   |       v
   |     用户权限验证
   |       |
   |       v
   |     Redis 缓存查询
   |       |
   |       |---- HIT：直接返回
   |       |
   |       |---- MISS：查询 MySQL
   |                    |
   |                    v
   |                 写入 Redis
   |
   |---- calculate_order
           |
           v
       参数校验与金额计算
```

## 四、核心功能

### 1. Structured Output

使用 Pydantic 定义结构化数据模型，并通过 `PydanticOutputParser` 解析模型输出，保证返回结果符合预期的数据结构。

### 2. Retry 自动重试

使用 Tenacity 实现异常重试机制。

- 最多重试 3 次。
- 使用指数退避策略。
- 针对网络连接异常、请求超时、限流和服务器内部错误等临时性异常进行重试。
- MySQL 查询也配置了针对数据库连接异常的重试机制。

### 3. Timeout 超时控制

使用 `asyncio.wait_for()` 对异步任务进行超时控制，避免 Agent 或工具调用长时间阻塞。

项目中分别对 MCP 工具加载和 Agent 任务执行设置了超时限制。

### 4. Exception Handling 异常处理

对模型请求、工具调用和业务执行过程中的异常进行分类处理，避免程序因单个请求失败而直接退出。

### 5. Logging 日志监控

使用 Python Logging 实现控制台与文件双重日志记录。

记录内容包括：

- Agent 启动及 MCP 工具加载状态。
- 用户输入和任务执行结果。
- 异常信息与重试记录。
- Redis、MySQL 查询耗时。
- 订单工具整体执行耗时。

日志保存于 `logs/agent.log`。

### 6. Tool Security 工具安全

通过 Pydantic 对工具参数进行校验，并在订单查询过程中验证用户权限。

例如，当前测试用户 ID 为 1，可以查询自己的订单 A1001，但不能查询属于用户 ID 2 的订单 A1003。

### 7. Redis 缓存优化

订单查询采用 Redis + MySQL 的缓存策略：

- 优先查询 Redis。
- 缓存命中时直接返回结果。
- 缓存未命中时查询 MySQL。
- 查询成功后将结果写入 Redis。
- 缓存设置 TTL 为 300 秒。

当 Redis 不可用时，系统可以降级使用 MySQL 查询。

## 五、测试结果

项目完成了以下功能验证：

| 测试项目 | 测试结果 |
|---|---|
| MCP Server 启动 | 通过 |
| MCP 工具自动加载 | 通过 |
| Agent 创建与对话 | 通过 |
| 订单查询 | 通过 |
| 订单金额计算 | 通过 |
| Redis 缓存读写 | 通过 |
| Redis 命中后跳过 MySQL | 通过 |
| 用户权限校验 | 通过 |
| Pydantic 参数校验 | 通过 |
| Retry 单项集成测试 | 通过 |
| Timeout 单项集成测试 | 通过 |
| 日志记录 | 通过 |

### Redis 缓存性能验证

以订单 A1001 为测试对象，分别记录首次查询和缓存命中后的 MCP 工具执行耗时。

| 测试次数 | Redis 状态 | MySQL 查询 | 工具耗时 |
|---|---|---|---:|
| 第一次 | MISS | 是 | 84.815 ms |
| 第二次 | HIT | 否 | 41.443 ms |
| 第三次 | HIT | 否 | 36.999 ms |

首次查询后，订单数据成功写入 Redis；后续查询均命中缓存，不再访问 MySQL。

第一次与第二次测试的工具耗时相差约 43.37 ms，降幅约 51.1%。

说明 Redis 缓存机制正常运行，并减少了重复数据库查询。

注：以上为实际运行日志中的单次测试样本，并非严格控制变量下的性能基准测试。Agent 整体耗时还受到模型 API 响应和网络波动影响。

## 六、项目目录

```text
day24_Agent_Reliability/
│
├── logs/
│   └── agent.log
│
├── day24_1_structured_output.py
├── day24_2_retry.py
├── day24_3_timeout.py
├── day24_4_exception.py
├── day24_5_logging.py
├── day24_6_security.py
├── day24_7_retry_integration.py
├── day24_8_timeout_integration.py
│
└── reliability_agent.py
```

MCP Server 复用项目 Day19 中的 `order_mcp_server.py`，避免重复维护业务工具代码。

## 七、项目运行

### 1. 环境配置

在项目根目录 `.env` 中配置：

```env
DEEPSEEK_API_KEY=你的API_KEY

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

ORDER_AGENT_USER_ID=1
```

MySQL 连接参数根据本地数据库配置填写。

### 2. 启动 Redis

确保 Redis 服务已经启动，并可以正常连接。

### 3. 运行综合 Agent

```powershell
python day24_Agent_Reliability/reliability_agent.py
```

根据提示输入问题，例如：

```text
查询A1001
查询A1003
查询不存在的订单A9999
100元的商品购买2件，打8折
什么是AI Agent？
```

## 八、项目总结

通过本项目，进一步理解了 AI Agent 从基础工具调用走向实际业务应用时需要考虑的可靠性问题。

掌握了 LangChain 1.x Agent 的创建方式，以及 MCP Client 与 MCP Server 的通信机制，并将 MySQL、Redis 等外部服务接入 Agent。

同时，通过 Retry、Timeout、Exception Handling、Logging 和 Tool Security 等机制，提高了系统面对异常请求和外部服务故障时的稳定性。

项目让我从单纯实现 Agent 功能，进一步转向考虑系统的稳定性、安全性、可维护性和实际业务落地。
### 面试介绍（约1分钟）

我做过一个基于 LangChain 和 MCP 的订单管理 Agent 综合项目，主要使用 Python、DeepSeek、MySQL 和 Redis。

项目通过 LangChain 构建 Agent，利用 MCP 协议连接订单服务，实现订单查询和金额计算。订单查询采用 Redis 缓存与 MySQL 结合的方式，并增加了 Pydantic 参数校验和用户权限验证。

在可靠性方面，我使用 Tenacity 实现 API 异常重试和指数退避，使用 asyncio.wait_for 实现异步任务超时控制，同时通过 Logging 记录执行日志和异常信息。

最后完成了订单查询、权限拦截、参数校验、金额计算以及 Retry、Timeout 等测试。

这个项目让我把前期学习的 Agent、工具调用、MCP、数据库、缓存和可靠性工程能力整合到了一个完整的业务场景中。