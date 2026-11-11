# Day15：API Tool——HTTP 请求与外部 API 接入

## 一、学习目标

本阶段在 Day14 多工具调用的基础上，进一步学习如何让 Agent 通过 HTTP 请求访问外部服务，实现从本地 Python 函数调用到外部 API 服务调用的升级。

主要学习内容：

1. 理解 HTTP 请求与响应机制。
2. 掌握 GET 和 POST 两种常见请求方式。
3. 理解 REST API 的基本概念。
4. 掌握 HTTPX 库的使用。
5. 掌握 JSON 数据格式及解析方式。
6. 学习 HTTP 状态码和异常处理。
7. 理解请求超时控制。
8. 将外部 HTTP API 封装为 LangChain Tool。
9. 实现 Agent 自主选择 API 工具并处理返回结果。

## 二、核心技术

- Python
- LangChain 1.x
- Pydantic
- HTTPX
- HTTP / REST API
- JSON
- DeepSeek API
- Tool Calling

## 三、API Tool 基本原理

### 1. 什么是 API？

API（Application Programming Interface），即应用程序编程接口。

可以理解为不同软件系统之间进行交互的接口。

例如：

- 天气 API：获取城市天气信息。
- 地图 API：获取地理位置和路线信息。
- 新闻 API：获取新闻内容。
- 订单 API：查询订单状态。
- 用户 API：获取用户信息。

通过 API，一个程序可以使用另一个系统提供的功能，而不需要了解其内部实现。

### 2. 什么是 HTTP？

HTTP（HyperText Transfer Protocol）是一种应用层通信协议，常用于客户端与服务器之间的数据传输。

例如，Python 程序访问天气 API：

```text
Python 客户端
      |
      | HTTP Request
      ↓
外部 API 服务器
      |
      | 处理请求
      ↓
服务器返回 HTTP Response
      |
      | JSON 数据
      ↓
Python 客户端解析数据
```

其中：

- Request：客户端向服务器发送的请求。
- Response：服务器返回给客户端的响应。
- URL：请求资源的地址。
- Method：请求方法，例如 GET、POST。
- Status Code：HTTP 状态码。
- Response Body：服务器返回的数据主体。

### 3. GET 和 POST 请求

GET 和 POST 是 HTTP 中最常见的两种请求方法。

| 对比 | GET | POST |
|---|---|---|
| 主要用途 | 获取资源 | 提交数据 |
| 参数传递 | 常见于 URL 查询参数或路径参数 | 常见于请求体 |
| 数据获取 | 查询文章、天气、订单 | 创建文章、提交表单 |
| 数据提交 | 通常不用于提交业务数据 | 常用于提交业务数据 |

GET 请求示例：

```python
response = httpx.get(
    "https://example.com/api/posts/1"
)
```

POST 请求示例：

```python
response = httpx.post(
    "https://example.com/api/posts",
    json={
        "title": "AI Agent",
        "body": "Learning API Tool"
    }
)
```

其中：

- `httpx.get()`：发送 GET 请求。
- `httpx.post()`：发送 POST 请求。
- `json=`：将 Python 字典作为 JSON 请求体发送。

### 4. 什么是 REST API？

REST（Representational State Transfer）是一种常见的 Web API 设计风格。

REST API 通常使用 URL 表示资源，并通过 HTTP 方法表达操作。

例如：

| HTTP 请求 | 含义 |
|---|---|
| GET /posts/1 | 查询 ID 为 1 的文章 |
| GET /posts | 查询文章列表 |
| POST /posts | 创建文章 |
| PUT /posts/1 | 更新文章 |
| PATCH /posts/1 | 部分更新文章 |
| DELETE /posts/1 | 删除文章 |

其中：

- `/posts` 表示文章资源。
- `/posts/1` 表示 ID 为 1 的具体文章。
- GET、POST、PUT、PATCH、DELETE 表示对资源执行的不同操作。

本阶段主要实践 GET 和 POST。

## 四、JSON 数据格式

### 1. 什么是 JSON？

JSON（JavaScript Object Notation）是一种轻量级的数据交换格式。

它广泛用于客户端与服务器之间的数据传输。

例如，API 返回：

```json
{
    "userId": 1,
    "id": 1,
    "title": "测试标题",
    "body": "这是一段文章内容"
}
```

JSON 数据由键值对组成。

| 字段 | 值 | 含义 |
|---|---|---|
| userId | 1 | 用户 ID |
| id | 1 | 文章 ID |
| title | 测试标题 | 文章标题 |
| body | 文章内容 | 文章正文 |

### 2. JSON 与 Python 字典的关系

Python 字典：

```python
data = {
    "userId": 1,
    "id": 1,
    "title": "测试标题",
    "body": "文章内容"
}
```

JSON 与 Python 字典结构相似，但两者并不完全相同。

使用 HTTPX：

```python
data = response.json()
```

可以将符合 JSON 格式的响应解析为 Python 字典或列表。

然后通过：

```python
data["title"]
data["body"]
```

获取对应字段。

### 3. JSON 数据序列化

POST 请求：

```python
payload = {
    "title": "AI Agent学习记录",
    "body": "今天学习了HTTP请求和API Tool",
    "userId": 1
}

response = httpx.post(
    url,
    json=payload
)
```

这里的 `json=payload` 会将 Python 数据转换为 JSON 格式发送给服务器，并设置相应的 Content-Type 请求头。

## 五、HTTPX：Python HTTP 请求库

### 1. 什么是 HTTPX？

HTTPX 是 Python 中用于发送 HTTP 请求的第三方库。

主要支持：

- GET 请求
- POST 请求
- PUT 请求
- PATCH 请求
- DELETE 请求
- 同步请求
- 异步请求
- 超时控制
- HTTP 状态码处理
- 连接管理

本阶段使用 HTTPX 完成同步 HTTP 请求。

安装：

```bash
pip install httpx
```

导入：

```python
import httpx
```

### 2. GET 请求

```python
import httpx

response = httpx.get(
    "https://jsonplaceholder.typicode.com/posts/1",
    timeout=10
)

response.raise_for_status()

data = response.json()

print(data)
```

代码解释：

| 代码 | 作用 |
|---|---|
| `import httpx` | 导入 HTTPX |
| `httpx.get()` | 发送 GET 请求 |
| URL | 指定请求地址 |
| `timeout=10` | 设置请求超时时间 |
| `response` | 保存 HTTP 响应对象 |
| `raise_for_status()` | 检查 HTTP 错误状态 |
| `response.json()` | 将 JSON 响应解析为 Python 数据 |

### 3. POST 请求

```python
import httpx

response = httpx.post(
    "https://jsonplaceholder.typicode.com/posts",
    json={
        "title": "AI Agent",
        "body": "Learning API Tool",
        "userId": 1
    },
    timeout=10
)

response.raise_for_status()

print(response.status_code)
print(response.json())
```

代码解释：

- `httpx.post()`：向指定 URL 发送 POST 请求。
- `json`：提交 JSON 格式的数据。
- `timeout`：控制请求超时时间。
- `response.status_code`：获取 HTTP 状态码。
- `response.json()`：解析服务器返回的数据。

### 4. HTTP 响应对象

HTTPX 请求成功后会返回 Response 对象。

常用属性和方法：

| 属性或方法 | 作用 |
|---|---|
| `response.status_code` | 获取状态码 |
| `response.text` | 获取响应文本 |
| `response.json()` | 解析 JSON |
| `response.headers` | 获取响应头 |
| `response.url` | 获取请求 URL |
| `response.raise_for_status()` | 检查 HTTP 状态码 |

需要区分：

- `response` 是 HTTP 响应对象。
- `response.json()` 是解析后的数据。
- `data` 通常是 Python 字典或列表。

## 六、HTTP 状态码与异常处理

### 1. 常见 HTTP 状态码

HTTP 状态码用于表示服务器处理请求的结果。

| 状态码 | 含义 | 常见场景 |
|---|---|---|
| 200 | OK | 请求成功 |
| 201 | Created | 资源创建成功 |
| 204 | No Content | 请求成功，但没有响应正文 |
| 400 | Bad Request | 请求参数错误 |
| 401 | Unauthorized | 未授权 |
| 403 | Forbidden | 禁止访问 |
| 404 | Not Found | 资源不存在 |
| 429 | Too Many Requests | 请求过于频繁 |
| 500 | Internal Server Error | 服务器内部错误 |
| 503 | Service Unavailable | 服务暂时不可用 |

### 2. raise_for_status()

```python
response.raise_for_status()
```

作用：

检查 HTTP 响应状态码。

当响应状态码表示客户端错误或服务器错误时，会抛出 HTTP 异常。

例如：

```text
200 OK
```

程序继续执行。

如果返回：

```text
404 Not Found
```

则抛出 `httpx.HTTPStatusError`。

这样可以避免程序把 HTTP 错误响应当作正常数据处理。

### 3. try / except 异常处理

Python 使用 try / except 捕获程序运行过程中出现的异常。

基本结构：

```python
try:
    # 尝试执行的代码

except Exception as e:
    # 发生异常时执行
```

其中：

- `try`：尝试执行代码。
- `except`：捕获异常。
- `Exception`：常见异常的基类。
- `as e`：将异常对象赋值给变量 e。
- `str(e)`：将异常信息转换为字符串。

### 4. HTTPX 常见异常

本阶段重点使用以下异常：

| 异常类型 | 含义 |
|---|---|
| `httpx.TimeoutException` | 请求超时 |
| `httpx.HTTPStatusError` | HTTP 状态码错误 |
| `httpx.RequestError` | 网络请求过程中出现错误 |
| `ValueError` | 数据解析或值处理错误 |
| `KeyError` | 字典中不存在指定字段 |

代码示例：

```python
try:

    response = httpx.get(
        url,
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

except httpx.TimeoutException:
    print("请求超时")

except httpx.HTTPStatusError as e:
    print("HTTP状态码错误：", e.response.status_code)

except httpx.RequestError as e:
    print("网络请求异常：", str(e))
```

本阶段将异常处理嵌入 API Tool，使工具在外部服务出现异常时能够返回明确的错误信息。

### 5. Timeout：请求超时控制

```python
TIMEOUT = 10.0
```

然后：

```python
response = httpx.get(
    url,
    timeout=TIMEOUT
)
```

超时控制的作用是避免程序一直等待没有响应的外部服务。

实际项目中，超时时间需要根据 API 的响应速度和业务需求设置。

需要注意：HTTPX 的 timeout 默认是网络阶段的超时控制，不应简单理解为整个业务流程固定在 10 秒内完成。

## 七、Python 相关语法补充

### 1. import：导入模块

```python
import httpx
import os

from pathlib import Path
from dotenv import load_dotenv
```

作用：

- `import`：导入整个模块。
- `from ... import ...`：从模块中导入指定对象。

本项目中：

| 模块 | 作用 |
|---|---|
| httpx | 发送 HTTP 请求 |
| os | 读取环境变量 |
| pathlib | 处理文件路径 |
| dotenv | 加载 .env 环境变量 |
| pydantic | 定义参数 Schema |
| langchain_core.tools | 定义 Agent 工具 |
| langchain.agents | 创建 Agent |

### 2. 常量与配置管理

```python
BASE_URL = "https://jsonplaceholder.typicode.com"

TIMEOUT = 10.0
```

使用大写字母命名表示程序中约定不随运行过程改变的配置值。

这样做可以避免在代码中多次重复写 API 地址和超时时间。

### 3. f-string：动态字符串

```python
post_id = 1

url = f"{BASE_URL}/posts/{post_id}"
```

输出：

```text
https://jsonplaceholder.typicode.com/posts/1
```

`f-string` 可以在字符串中直接插入变量或表达式。

### 4. Python 字典

```python
payload = {
    "title": title,
    "body": body,
    "userId": user_id
}
```

字典用于保存键值对数据。

这里将用户输入整理成 API 要求的 JSON 数据结构。

注意：Python 参数名使用 `user_id`，但外部 API 的 JSON 字段使用 `userId`，两者需要根据接口规范进行转换。

### 5. 元组与多异常捕获

```python
except (ValueError, KeyError) as e:
    return f"数据解析失败：{str(e)}"
```

这里使用元组同时捕获多个异常类型。

当 JSON 解析出现值错误，或访问字典字段时出现 KeyError，就会进入该异常处理分支。

### 6. 函数返回值

```python
def get_post(post_id: int) -> str:
    ...
```

- `def`：定义函数。
- `post_id: int`：参数类型注解。
- `-> str`：返回值类型注解。

这里表示函数接收文章 ID，并预期返回字符串。

### 7. 装饰器与参数 Schema

```python
@tool(args_schema=GetPostInput)
def get_post(post_id: int) -> str:
    ...
```

`@tool` 将普通 Python 函数封装为 LangChain Tool。

`args_schema` 用于指定工具的参数结构。

本阶段继续沿用 Day14 学习的 Pydantic Schema 和 Tool Calling 知识。

## 八、实战：构建 API Tool Agent

### 1. 项目结构

```text
day15_API_Tool/
└── api_tool_agent.py
```

### 2. 测试 API 服务

本阶段使用 JSONPlaceholder：

https://jsonplaceholder.typicode.com

这是一个用于测试 HTTP 请求的模拟 REST API 服务。

主要接口：

| 请求地址 | 方法 | 功能 |
|---|---|---|
| /posts/1 | GET | 获取 ID 为 1 的文章 |
| /posts | GET | 获取文章列表 |
| /posts | POST | 模拟创建文章 |

该服务不需要 API Key。

注意：POST 返回模拟创建结果，不会真正持久化保存文章。

### 3. 加载环境变量

```python
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR.parent / ".env")

api_key = os.getenv("DEEPSEEK_API_KEY")

if not api_key:
    raise ValueError("没有找到 DEEPSEEK_API_KEY")
```

作用：

1. 获取当前 Python 文件所在目录。
2. 定位项目根目录中的 `.env`。
3. 加载环境变量。
4. 读取 DeepSeek API Key。
5. 如果没有读取到 Key，则抛出异常。

### 4. API 基础配置

```python
BASE_URL = "https://jsonplaceholder.typicode.com"

TIMEOUT = 10.0
```

统一管理 API 地址和超时时间。

后续更换 API 服务时，只需要调整配置。

### 5. 定义 GET 工具参数 Schema

```python
class GetPostInput(BaseModel):

    post_id: int = Field(
        gt=0,
        description="文章ID，必须是正整数"
    )
```

使用 Pydantic 定义查询文章所需要的参数。

其中：

- `post_id`：文章 ID。
- `int`：整数类型。
- `gt=0`：必须大于 0。
- `description`：向模型说明参数的含义。

### 6. 定义 POST 工具参数 Schema

```python
class CreatePostInput(BaseModel):

    title: str = Field(
        min_length=1,
        description="文章标题"
    )

    body: str = Field(
        min_length=1,
        description="文章正文"
    )

    user_id: int = Field(
        gt=0,
        description="用户ID，必须是正整数"
    )
```

POST 请求需要提交三个参数：

| 参数 | 类型 | 约束 |
|---|---|---|
| title | str | 至少一个字符 |
| body | str | 至少一个字符 |
| user_id | int | 大于 0 |

使用 Schema 可以让模型了解工具需要哪些参数，以及参数的基本约束。

### 7. 工具一：GET 查询文章

```python
@tool(args_schema=GetPostInput)
def get_post(post_id: int) -> str:
    """根据文章ID查询文章内容。当用户询问某篇文章的标题、正文或文章详情时使用。"""

    url = f"{BASE_URL}/posts/{post_id}"

    try:

        response = httpx.get(
            url,
            timeout=TIMEOUT
        )

        response.raise_for_status()

        data = response.json()

        return (
            f"文章查询成功：\n"
            f"文章ID：{data['id']}\n"
            f"用户ID：{data['userId']}\n"
            f"标题：{data['title']}\n"
            f"正文：{data['body']}"
        )

    except httpx.TimeoutException:
        return "文章查询失败：请求超时。"

    except httpx.HTTPStatusError as e:
        return f"文章查询失败：HTTP状态码 {e.response.status_code}。"

    except httpx.RequestError as e:
        return f"文章查询失败：网络请求异常，{str(e)}"

    except (ValueError, KeyError) as e:
        return f"文章数据解析失败：{str(e)}"
```

执行流程：

```text
Agent 调用 get_post
        ↓
接收 post_id
        ↓
拼接 API 请求地址
        ↓
httpx.get() 发送 GET 请求
        ↓
检查 HTTP 状态码
        ↓
response.json() 解析 JSON
        ↓
提取文章字段
        ↓
整理为字符串
        ↓
返回 Agent
```

关键代码解释：

**第一步：构造 URL**

```python
url = f"{BASE_URL}/posts/{post_id}"
```

根据文章 ID 动态生成请求地址。

例如：

```text
https://jsonplaceholder.typicode.com/posts/1
```

**第二步：发送 GET 请求**

```python
response = httpx.get(
    url,
    timeout=TIMEOUT
)
```

向外部 API 发送请求。

**第三步：检查响应状态**

```python
response.raise_for_status()
```

如果服务器返回 404 等错误状态，会抛出 HTTPStatusError。

**第四步：解析 JSON**

```python
data = response.json()
```

将 API 返回的 JSON 转换为 Python 字典。

**第五步：提取字段**

```python
data["id"]
data["userId"]
data["title"]
data["body"]
```

获取文章信息并整理为字符串返回给 Agent。

### 8. 工具二：POST 创建文章

```python
@tool(args_schema=CreatePostInput)
def create_post(
    title: str,
    body: str,
    user_id: int
) -> str:
    """向测试文章API提交一篇新文章。当用户要求创建、发布或提交文章时使用。"""

    url = f"{BASE_URL}/posts"

    payload = {
        "title": title,
        "body": body,
        "userId": user_id
    }

    try:

        response = httpx.post(
            url,
            json=payload,
            timeout=TIMEOUT
        )

        response.raise_for_status()

        data = response.json()

        return (
            f"文章提交成功：\n"
            f"文章ID：{data['id']}\n"
            f"用户ID：{data['userId']}\n"
            f"标题：{data['title']}\n"
            f"正文：{data['body']}\n"
            f"HTTP状态码：{response.status_code}\n"
            f"说明：这是测试API返回的模拟创建结果。"
        )

    except httpx.TimeoutException:
        return "文章创建失败：请求超时。"

    except httpx.HTTPStatusError as e:
        return f"文章创建失败：HTTP状态码 {e.response.status_code}。"

    except httpx.RequestError as e:
        return f"文章创建失败：网络请求异常，{str(e)}"

    except (ValueError, KeyError) as e:
        return f"文章数据解析失败：{str(e)}"
```

执行流程：

```text
Agent 调用 create_post
        ↓
接收 title、body、user_id
        ↓
构造 payload 字典
        ↓
httpx.post() 发送 POST 请求
        ↓
将 payload 转换为 JSON 请求体
        ↓
服务器处理请求
        ↓
检查 HTTP 状态码
        ↓
解析 JSON 响应
        ↓
提取创建结果
        ↓
返回 Agent
```

关键代码：

```python
payload = {
    "title": title,
    "body": body,
    "userId": user_id
}
```

将模型提供的参数整理为 API 需要的数据格式。

```python
response = httpx.post(
    url,
    json=payload,
    timeout=TIMEOUT
)
```

将数据提交到外部 API。

这里的 `json=payload` 与 GET 请求不同，POST 通过请求体向服务器提交数据。

### 9. 初始化 LLM

```python
llm = ChatOpenAI(
    model="deepseek-chat",
    api_key=api_key,
    base_url="https://api.deepseek.com/v1",
    temperature=0
)
```

继续使用 DeepSeek 的 OpenAI 兼容接口。

主要参数：

- `model`：指定模型。
- `api_key`：API 密钥。
- `base_url`：API 服务地址。
- `temperature=0`：降低生成结果的随机性。

### 10. 创建 Agent

```python
tools = [
    get_post,
    create_post
]

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt="""
你是一个 API 业务助手。

规则：
1. 用户询问已有文章内容时，调用 get_post。
2. 用户要求创建或提交文章时，调用 create_post。
3. 必须根据用户提供的信息生成工具参数。
4. 必须依据 API 返回结果回答。
5. 如果 API 调用失败，应如实说明。
6. 不得编造 API 返回的数据。
7. 普通闲聊不需要调用工具。
"""
)
```

通过 `tools` 列表将两个 API Tool 注册给 Agent。

模型根据工具名称、描述和参数 Schema，判断应该调用哪个工具。

### 11. Agent 调用与执行轨迹

```python
result = agent.invoke({
    "messages": [
        {
            "role": "user",
            "content": question
        }
    ]
})
```

使用 LangChain 1.x 的 `create_agent` 创建的 Agent，通过 `invoke()` 接收用户问题。

观察工具调用：

```python
for message in result["messages"]:

    print(message.type)

    if getattr(message, "tool_calls", None):
        print(message.tool_calls)

    if message.type == "tool":
        print(message.name)
        print(message.content)
```

主要消息类型：

| 消息类型 | 含义 |
|---|---|
| human | 用户输入 |
| ai | 模型回复或发起工具调用 |
| tool | 工具执行结果 |

其中：

- `AIMessage.tool_calls`：观察模型选择的工具名称和参数。
- `ToolMessage.name`：查看实际执行的工具名称。
- `ToolMessage.content`：查看工具返回的内容。

最终回答：

```python
print(result["messages"][-1].content)
```

获取 Agent 最后一条消息的内容。

## 九、实际测试结果

本阶段共完成四组测试，均通过。

### 测试一：POST 创建文章

用户输入：

```text
帮我创建一篇文章，标题是AI Agent学习记录，
正文是今天学习了HTTP请求和API Tool，
用户ID为1。
```

Agent 选择：

```text
create_post
```

模型生成参数：

```python
{
    "title": "AI Agent学习记录",
    "body": "今天学习了HTTP请求和API Tool",
    "user_id": 1
}
```

API 返回：

```text
文章提交成功：
文章ID：101
用户ID：1
标题：AI Agent学习记录
正文：今天学习了HTTP请求和API Tool
HTTP状态码：201
```

测试结果：通过。

说明：

1. Agent 正确识别创建文章的需求。
2. 正确选择 POST 工具。
3. 正确提取标题、正文和用户 ID。
4. 成功提交 JSON 请求体。
5. 成功解析服务器返回的创建结果。

### 测试二：GET 查询文章

用户输入：

```text
帮我查询文章ID为1的内容。
```

Agent 选择：

```text
get_post
```

模型生成参数：

```python
{
    "post_id": 1
}
```

API 返回：

```text
文章查询成功：
文章ID：1
用户ID：1
标题：sunt aut facere repellat provident occaecati excepturi optio reprehenderit
正文：
quia et suscipit
suscipit recusandae consequuntur expedita et cum
reprehenderit molestiae ut ut quas totam
nostrum rerum est autem sunt rem eveniet architecto
```

测试结果：通过。

说明：

1. Agent 正确选择 GET 查询工具。
2. 正确提取文章 ID。
3. 成功访问外部 API。
4. 成功解析 JSON 数据。
5. 正确返回文章标题和正文。

### 测试三：查询不存在的文章

用户输入：

```text
查询文章ID为999999的内容。
```

Agent 选择：

```text
get_post
```

模型生成参数：

```python
{
    "post_id": 999999
}
```

API 返回：

```text
文章查询失败：HTTP状态码 404。
```

Agent 最终回答：

```text
查询失败：
文章 ID 999999 不存在（API 返回 HTTP 404）。
请确认文章 ID 是否正确。
```

测试结果：通过。

说明：

1. Agent 正确调用 GET 工具。
2. API 返回 404。
3. `response.raise_for_status()` 触发 HTTPStatusError。
4. 异常处理捕获错误并返回明确的信息。
5. Agent 根据工具返回结果向用户解释查询失败原因。

### 测试四：普通闲聊

用户输入：

```text
你好，介绍一下你自己。
```

实际结果：

```text
没有调用任何 API 工具。

Agent 直接回答：
你好！我是一个 API 业务助手……
```

测试结果：通过。

说明：

Agent 能够区分普通对话和需要访问外部 API 的业务需求，不会强制调用工具。

### 测试结果汇总

| 测试项目 | 工具 | 实际结果 | 状态 |
|---|---|---|---|
| 创建文章 | create_post | HTTP 201 | 通过 |
| 查询文章 | get_post | HTTP 200 | 通过 |
| 查询不存在的文章 | get_post | HTTP 404，异常捕获成功 | 通过 |
| 普通闲聊 | 不调用工具 | 直接回答 | 通过 |

## 十、实际开发中的工程注意事项

### 1. API Key 管理

真实业务 API 通常需要 API Key 或 Token。

不应该将密钥直接写在 Python 代码中。

应该通过 `.env` 管理：

```text
WEATHER_API_KEY=your_api_key
```

然后：

```python
api_key = os.getenv("WEATHER_API_KEY")
```

避免密钥泄露到 GitHub。

### 2. 超时控制

外部 API 可能响应缓慢甚至无法访问。

应该使用：

```python
httpx.get(
    url,
    timeout=10
)
```

避免程序无限等待。

### 3. 错误处理

不能只考虑 API 请求成功的情况。

还需要考虑：

- 网络连接失败。
- 请求超时。
- 参数错误。
- API Key 无效。
- 访问权限不足。
- 请求频率限制。
- 服务器内部错误。
- 返回数据格式变化。

### 4. API 重试

当出现临时网络故障或服务暂时不可用时，可以考虑重试机制。

但需要注意：

- GET 请求通常适合在特定临时错误下重试。
- POST 请求可能已经成功执行，只是响应丢失，盲目重试可能造成重复创建。
- 真实业务中应考虑幂等性和请求唯一标识。

本阶段尚未实现自动重试，后续可靠性模块再深入学习。

### 5. API 安全

实际项目中还需要考虑：

- API Key 和 Token 保护。
- 用户身份认证。
- 请求参数校验。
- 工具调用权限。
- 外部 URL 访问限制。
- 防止 SSRF 等安全问题。

Agent 不应该不受限制地访问任意外部 URL。

## 十一、Day15 学习成果

完成本阶段后，掌握了：

1. HTTP 请求与响应的基本原理。
2. GET 和 POST 的区别。
3. REST API 的基本设计方式。
4. JSON 数据格式及其与 Python 字典的关系。
5. HTTPX 的安装和使用。
6. GET 请求与 POST 请求。
7. HTTP Response 对象及常用属性。
8. `response.json()` 数据解析。
9. `response.raise_for_status()` 状态码检查。
10. HTTP 状态码的常见含义。
11. HTTPX 超时控制。
12. HTTPX 异常处理。
13. Pydantic 参数 Schema。
14. 将外部 API 封装成 LangChain Tool。
15. Agent 自主选择 GET、POST 工具。
16. 观察 AIMessage 和 ToolMessage 的执行轨迹。

## 十二、本阶段总结

Day15 完成了从本地 Python Tool 到外部 API Tool 的升级。

Day14 中，Agent 通过调用本地 Python 函数完成订单金额计算和模拟订单查询；Day15 中，Agent 开始通过 HTTP 请求访问外部 API，实现文章查询和文章创建。

通过 HTTPX 学习了 GET、POST 请求，掌握了 JSON 数据解析、HTTP 状态码检查、请求超时控制和异常处理。

最终实现了两个 API Tool：

- `get_post`：通过 GET 请求查询文章。
- `create_post`：通过 POST 请求提交文章。

测试验证了 API 成功请求、资源不存在时的 404 异常处理，以及普通闲聊不调用工具的能力。

需要注意，JSONPlaceholder 是模拟测试 API，POST 返回的创建结果不会永久保存，不能将其当作真实业务数据库。

本阶段的核心收获是理解了 Agent 与外部服务之间的交互方式，掌握了将 HTTP API 封装为 Agent Tool 的基本方法。

## 十三、下一阶段学习方向

Day16：Database Tool

学习内容：

1. MySQL 数据库基础。
2. Python 连接 MySQL。
3. SQL 查询与 CRUD。
4. 数据库连接与连接管理。
5. 将数据库查询封装为 LangChain Tool。
6. Agent 自主选择数据库工具。
7. 数据库异常处理。
8. SQL 安全与参数化查询。

学习目标：

将 Day14 使用的模拟订单字典替换为真实 MySQL 数据库，使 Agent 能够查询真实业务数据，实现从模拟数据到数据库访问的升级。

---

**当前学习进度：**

- Day11：RAG 基础——已完成。
- Day12：多格式文档加载与检索——已完成。
- Day13：RAG + Agent——已完成。
- Day14：Tool Calling 进阶——已完成。
- Day15：API Tool——已完成。

**下一模块：Day16——Database Tool。**