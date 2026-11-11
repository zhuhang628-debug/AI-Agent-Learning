# Day16：Database Tool —— 让 Agent 连接 MySQL 数据库

## 一、学习目标

本节学习如何将 MySQL 数据库接入 LangChain Agent，使 Agent 能够根据用户的自然语言问题，调用自定义数据库工具，查询真实业务数据。

Day14 使用 Python 字典模拟订单数据，Day16 将订单数据迁移到 MySQL，实现从模拟数据查询到真实数据库查询的升级。

本节主要完成：

1. 理解 Python 与 MySQL 的连接方式。
2. 掌握 PyMySQL 的基本使用。
3. 使用 SQL 参数化查询数据库。
4. 使用 Pydantic 定义数据库 Tool 的输入参数。
5. 使用 LangChain `@tool` 封装数据库查询函数。
6. 使用 LangChain 1.x 的 `create_agent()` 创建数据库查询 Agent。
7. 理解 Agent 从接收用户问题到执行 SQL、返回查询结果的完整过程。

## 二、核心技术

- Python 3.10.11
- MySQL
- Navicat
- PyMySQL
- LangChain 1.x
- Pydantic
- DeepSeek API
- python-dotenv

## 三、项目结构

```text
AI-Agent-Learning/
│
├── .env
│
└── day16_Database_Tool/
    └── database_agent.py
```

数据库名称：`shop_db`

数据表名称：`orders`

## 四、数据库设计

### 1. 创建数据库

```sql
CREATE DATABASE IF NOT EXISTS shop_db
DEFAULT CHARACTER SET utf8mb4;

USE shop_db;
```

### 2. 创建订单表

```sql
CREATE TABLE IF NOT EXISTS orders (
    id INT PRIMARY KEY AUTO_INCREMENT,
    order_no VARCHAR(30) NOT NULL UNIQUE,
    status VARCHAR(30) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    user_id INT NOT NULL
);
```

字段说明：

| 字段 | 类型 | 说明 |
|---|---|---|
| id | INT | 自增主键 |
| order_no | VARCHAR(30) | 订单编号，唯一 |
| status | VARCHAR(30) | 订单状态 |
| amount | DECIMAL(10,2) | 订单金额 |
| user_id | INT | 用户编号 |

### 3. 插入测试数据

```sql
INSERT INTO orders (order_no, status, amount, user_id)
VALUES
('A1001', '已发货', 199.00, 1),
('A1002', '待付款', 299.00, 1),
('A1003', '已完成', 599.00, 2);
```

测试数据：

| 订单编号 | 订单状态 | 金额 | 用户ID |
|---|---|---:|---:|
| A1001 | 已发货 | 199.00 | 1 |
| A1002 | 待付款 | 299.00 | 1 |
| A1003 | 已完成 | 599.00 | 2 |

## 五、核心知识点

### 1. PyMySQL

PyMySQL 是 Python 操作 MySQL 数据库的第三方库。

安装：

```bash
pip install pymysql
```

建立数据库连接：

```python
connection = pymysql.connect(
    host="localhost",
    port=3306,
    user="root",
    password="数据库密码",
    database="shop_db"
)
```

主要参数：

- host：数据库服务器地址。
- port：数据库端口，MySQL 默认 3306。
- user：数据库用户名。
- password：数据库密码。
- database：需要连接的数据库。
- charset：字符编码。

### 2. 数据库连接与游标

数据库连接对象负责建立 Python 与 MySQL 之间的通信。

游标 Cursor 负责执行 SQL 语句以及获取查询结果。

```python
connection = pymysql.connect(**MYSQL_CONFIG)

with connection.cursor() as cursor:
    cursor.execute("SELECT * FROM orders")
    result = cursor.fetchall()
```

`pymysql.connect()`：建立数据库连接。

`connection.cursor()`：创建游标。

`cursor.execute()`：执行 SQL 语句。

`cursor.fetchone()`：获取一条查询结果。

`cursor.fetchall()`：获取全部查询结果。

`cursor.fetchmany(5)`：获取指定数量的查询结果。

使用 `with` 管理游标，可以在代码块结束时自动关闭游标。

数据库连接本身仍然需要关闭。

### 3. DictCursor

默认情况下，数据库查询结果通常以元组形式返回。

例如：

```python
("A1001", "已发货", 199.00, 1)
```

使用：

```python
cursorclass=pymysql.cursors.DictCursor
```

查询结果将以字典形式返回：

```python
{
    "order_no": "A1001",
    "status": "已发货",
    "amount": 199.00,
    "user_id": 1
}
```

这样可以通过字段名称直接获取数据：

```python
order["order_no"]
order["status"]
order["amount"]
```

相比元组下标访问，字典方式更加直观。

### 4. SQL 参数化查询

本节最重要的安全知识点之一。

参数化查询：

```python
sql = """
    SELECT order_no, status, amount, user_id
    FROM orders
    WHERE order_no = %s
"""

cursor.execute(sql, (order_no,))
```

`%s` 是 PyMySQL 的参数占位符。

第二个参数 `(order_no,)` 是一个只有一个元素的元组，末尾逗号不能省略。

错误写法：

```python
sql = f"SELECT * FROM orders WHERE order_no = '{order_no}'"
```

直接使用 f-string 拼接用户输入可能产生 SQL 注入风险。

参数化查询将 SQL 结构与用户输入分开处理，避免将输入直接作为 SQL 代码执行。

### 5. 数据库异常处理

```python
except pymysql.MySQLError as e:
    return f"数据库查询失败，错误类型：{type(e).__name__}"
```

`pymysql.MySQLError` 用于捕获 PyMySQL 相关数据库异常。

### 6. finally 资源释放

```python
finally:
    if connection is not None:
        connection.close()
```

`finally` 中的代码无论查询成功还是失败都会执行。

因此可以保证数据库连接得到关闭，避免连接资源长期占用。

### 7. 环境变量管理

在项目根目录 `.env` 中配置：

```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=你的MySQL密码
MYSQL_DATABASE=shop_db
```

Python 读取环境变量：

```python
load_dotenv(BASE_DIR.parent / ".env")

MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_USER = os.getenv("MYSQL_USER")
```

数据库密码不应该直接写入 Python 源代码，也不应该上传到 GitHub。

## 六、实战项目：Database Agent

### 1. 完整代码

文件：`database_agent.py`

```python
import os
from pathlib import Path

import pymysql
from dotenv import load_dotenv
from pydantic import BaseModel, Field

from langchain.agents import create_agent
from langchain.tools import tool
from langchain_openai import ChatOpenAI


# 1. 加载环境变量

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR.parent / ".env")

MYSQL_CONFIG = {
    "host": os.getenv("MYSQL_HOST"),
    "port": int(os.getenv("MYSQL_PORT", "3306")),
    "user": os.getenv("MYSQL_USER"),
    "password": os.getenv("MYSQL_PASSWORD"),
    "database": os.getenv("MYSQL_DATABASE"),
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor
}


# 2. 定义数据库查询参数

class OrderQueryInput(BaseModel):
    order_no: str = Field(
        description="需要查询的订单编号，例如 A1001"
    )


# 3. 封装数据库查询 Tool

@tool(args_schema=OrderQueryInput)
def query_order(order_no: str) -> str:
    """根据订单编号查询订单状态、金额和用户ID。只能查询订单，不允许修改数据。"""

    connection = None

    try:
        connection = pymysql.connect(**MYSQL_CONFIG)

        with connection.cursor() as cursor:

            sql = """
                SELECT order_no, status, amount, user_id
                FROM orders
                WHERE order_no = %s
            """

            cursor.execute(sql, (order_no,))

            order = cursor.fetchone()

            if order is None:
                return f"没有找到订单编号为 {order_no} 的订单。"

            return (
                f"订单编号：{order['order_no']}\\n"
                f"订单状态：{order['status']}\\n"
                f"订单金额：{order['amount']:.2f} 元\\n"
                f"用户ID：{order['user_id']}"
            )

    except pymysql.MySQLError as e:
        return (
            f"数据库查询失败，请检查数据库连接或查询配置。"
            f"错误类型：{type(e).__name__}"
        )

    finally:
        if connection is not None:
            connection.close()


# 4. 初始化 DeepSeek 模型

api_key = os.getenv("DEEPSEEK_API_KEY")

if not api_key:
    raise ValueError(
        "未找到 DEEPSEEK_API_KEY，请检查项目根目录下的 .env 文件"
    )

llm = ChatOpenAI(
    model="deepseek-chat",
    api_key=api_key,
    base_url="https://api.deepseek.com/v1",
    temperature=0
)


# 5. 创建 Agent

tools = [query_order]

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt="""
    你是一个订单查询助手。

    当用户询问具体订单信息时，必须调用 query_order 工具查询数据库。
    根据工具返回的真实数据回答用户。
    不允许编造订单信息。
    如果订单不存在，明确告诉用户没有找到对应订单。
    普通闲聊不需要调用数据库工具。
    """
)


# 6. 运行 Agent

if __name__ == "__main__":

    question = input("请输入你的问题：")

    result = agent.invoke({
        "messages": [
            {"role": "user", "content": question}
        ]
    })

    print("\n========== Agent 执行过程 ==========")

    for message in result["messages"]:

        print(f"\n消息类型：{message.type}")

        if hasattr(message, "tool_calls") and message.tool_calls:
            print("工具调用：")

            for tool_call in message.tool_calls:
                print(tool_call)

        if message.type == "tool":
            print("工具名称：", message.name)
            print("工具返回：", message.content)

    print("\n========== Agent 最终回答 ==========")
    print(result["messages"][-1].content)
```

### 2. 代码执行流程

1. 加载项目根目录中的 `.env`。
2. 读取 MySQL 连接配置。
3. 定义 Pydantic 参数模型 `OrderQueryInput`。
4. 使用 `@tool` 将 `query_order()` 封装为数据库工具。
5. PyMySQL 建立数据库连接。
6. 执行参数化 SQL 查询。
7. 获取数据库返回结果。
8. 将查询结果返回给 LangChain。
9. 使用 DeepSeek 模型创建 Agent。
10. Agent 根据用户问题决定是否调用数据库工具。
11. 模型根据 ToolMessage 生成最终回答。

## 七、Agent Tool Calling 消息分析

本节通过打印 `result["messages"]` 观察 Agent 的执行过程。

### 1. 用户消息

```text
消息类型：human
```

表示用户输入的问题。

### 2. AI 工具调用消息

```python
{
    'name': 'query_order',
    'args': {
        'order_no': 'A1001'
    },
    'type': 'tool_call'
}
```

表示模型判断需要查询订单，并生成工具名称及参数。

### 3. Tool 工具返回消息

```text
消息类型：tool
工具名称：query_order

订单编号：A1001
订单状态：已发货
订单金额：199.00 元
用户ID：1
```

表示 Python 工具函数已经执行，并返回 MySQL 中的真实查询结果。

### 4. AI 最终回答

模型接收 ToolMessage 后，将结构化查询结果整理成自然语言回复。

完整过程：

HumanMessage → AIMessage（Tool Call）→ ToolMessage → AIMessage（Final Answer）。

## 八、实际测试结果

### 测试1：查询 A1001

输入：

```text
帮我查询订单 A1001
```

实际结果：

```text
订单编号：A1001
订单状态：已发货
订单金额：199.00 元
用户ID：1
```

结果：通过。

### 测试2：查询 A1002

输入：

```text
A1002 的订单状态是什么？
```

实际结果：

```text
订单状态：待付款
订单金额：299.00 元
用户ID：1
```

结果：通过。

### 测试3：查询不存在的订单

输入：

```text
查询订单 A9999
```

实际结果：

```text
没有找到订单编号为 A9999 的订单。
```

结果：通过。

### 测试4：验证真实 Tool Calling

查询 A1001 时，执行日志显示：

```text
消息类型：human

消息类型：ai
工具调用：
{
    'name': 'query_order',
    'args': {'order_no': 'A1001'},
    'type': 'tool_call'
}

消息类型：tool
工具名称：query_order
工具返回：
订单编号：A1001
订单状态：已发货
订单金额：199.00 元
用户ID：1

消息类型：ai
```

结果：通过。

证明 Agent 确实调用了 `query_order`，并由 Python 连接 MySQL 执行查询，而不是模型直接编造答案。

### 测试5：普通闲聊

输入：

```text
你好，介绍一下你自己
```

执行日志：

```text
消息类型：human
消息类型：ai
```

没有出现 Tool Call 和 ToolMessage。

结果：通过。

说明 Agent 能够根据用户意图决定是否使用数据库工具。

## 九、工程注意事项

### 1. 数据库连接管理

本节采用每次 Tool 调用时建立连接、查询完成后关闭连接的方式。

优点是实现简单，适合当前学习项目。

生产环境可以进一步使用连接池，提高并发访问时的连接管理效率。

### 2. SQL 注入防护

所有外部输入都应使用参数化查询，不要通过 f-string 拼接 SQL。

### 3. 数据库权限

当前 Tool 只提供 SELECT 查询能力。

真实业务系统中应使用权限受限的数据库账号，避免 Agent 直接使用拥有全部权限的 root 账号。

### 4. 敏感信息保护

数据库用户名、密码以及 API Key 应放在 `.env` 中，并通过 `.gitignore` 排除。

### 5. 金额数据处理

数据库使用 DECIMAL 保存金额，避免使用浮点数直接进行精确金额运算。

## 十、Day16 学习成果

本节完成了从 Python 字典模拟订单查询到 MySQL 真实数据库查询的升级。

掌握了：

- PyMySQL 数据库连接。
- SQL 查询与参数化查询。
- DictCursor 查询结果处理。
- 数据库异常处理与连接释放。
- Pydantic Tool 参数定义。
- LangChain `@tool` 封装。
- LangChain 1.x `create_agent()`。
- Agent 自主判断是否调用数据库工具。
- HumanMessage、AIMessage、ToolMessage 执行过程分析。

最终实现了一个能够通过自然语言查询 MySQL 订单数据的 Agent。

## 十一、下一阶段

建议 Day17 学习 **Redis Tool 与缓存机制**，理解为什么真实 AI 应用除了 MySQL 以外，还需要 Redis。

重点内容：

1. Redis 的基本数据结构。
2. Python 连接 Redis。
3. 使用 Redis 实现缓存。
4. 将缓存查询封装成 LangChain Tool。
5. 理解 MySQL 与 Redis 的职责区别。
6. 结合 Agent 实现缓存优先、数据库兜底的查询流程。