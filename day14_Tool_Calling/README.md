# Day14：Tool Calling 进阶

## 一、学习目标

本阶段在已有 LangChain Agent 基础上，进一步学习 Tool Calling 的进阶用法，实现多个工具的定义、参数约束、工具选择和执行结果返回。

主要学习内容：

1. 理解 Tool Calling 的完整执行流程。
2. 掌握 Pydantic 参数 Schema。
3. 掌握多个工具的定义与注册。
4. 理解 Agent 如何自主选择工具。
5. 理解工具执行结果如何返回 LLM。
6. 学习 Python 装饰器、类、函数、异常处理等相关语法。

## 二、核心技术

- Python
- LangChain 1.x
- Pydantic
- LangChain Tool Calling
- `@tool`
- `create_agent`
- DeepSeek API

## 三、Tool Calling 工作原理

Tool Calling 是指模型根据用户的问题，判断是否需要调用外部工具，并生成对应的工具名称和参数。

需要注意：LLM 本身并不直接执行 Python 函数，而是生成工具调用请求，由 LangChain 负责执行对应的工具。

完整流程：

```text
用户输入问题
      ↓
LLM 接收工具定义
      ↓
模型判断是否需要调用工具
      ↓
生成 Tool Call
      ↓
LangChain 执行 Python 函数
      ↓
工具返回执行结果
      ↓
结果返回 LLM
      ↓
LLM 整理并生成最终回答
```

其中：

- LLM 负责决策：选择工具、生成参数。
- LangChain 负责执行：调用 Python 函数、获取结果。
- Tool 负责具体业务操作：计算、查询、检索等。

## 四、Python 基础语法与代码结构

### 1. class：定义类

```python
class Person:
    name = "张三"
    age = 20
```

`class` 是 Python 中定义类的关键字。

类可以理解为一个模板，用来描述对象具有哪些属性和行为。

Day14 中：

```python
class OrderInput(BaseModel):
    ...
```

定义了一个名为 `OrderInput` 的类，用于描述订单工具需要的输入参数。

### 2. BaseModel：Pydantic 数据模型

```python
from pydantic import BaseModel, Field

class User(BaseModel):
    name: str
    age: int
```

`BaseModel` 是 Pydantic 提供的基础模型。

继承 `BaseModel` 后，可以获得：

- 数据类型校验
- 数据解析
- 字段约束
- JSON Schema 生成

Day14 中使用它定义工具参数模型。

### 3. Field：定义字段约束

```python
price: float = Field(
    gt=0,
    description="商品单价，必须大于0"
)
```

其中：

| 语法 | 含义 |
|---|---|
| `price` | 字段名称 |
| `float` | 类型注解，表示预期为浮点数 |
| `Field()` | 定义字段约束和描述 |
| `gt=0` | 必须大于0 |
| `ge=0` | 必须大于或等于0 |
| `lt=100` | 必须小于100 |
| `le=1` | 必须小于或等于1 |
| `description` | 字段描述 |

### 4. 类型注解与返回值注解

参数类型注解：

```python
def calculate_order(price: float, quantity: int):
    ...
```

表示：

- `price` 预期为 float。
- `quantity` 预期为 int。

返回值类型注解：

```python
def calculate_order(...) -> str:
    ...
```

表示函数预期返回字符串。

注意：普通 Python 类型注解主要用于说明和工具辅助，本身不会自动强制所有输入和返回值满足类型要求。

### 5. def：定义函数

```python
def add(a, b):
    return a + b
```

基本结构：

```python
def 函数名称(参数):
    函数内部代码
    return 返回结果
```

Day14 中通过 `def` 定义订单计算和订单查询函数。

### 6. 装饰器 @tool

```python
@tool
def lookup_order(order_id: str) -> str:
    ...
```

`@tool` 是 LangChain 提供的工具封装装饰器。

它将普通 Python 函数转换成 LangChain Tool，使 Agent 可以将其交给模型选择和调用。

带有自定义参数 Schema 的写法：

```python
@tool(args_schema=OrderInput)
def calculate_order(...):
    ...
```

其中 `args_schema=OrderInput` 表示使用 `OrderInput` 类定义工具的参数结构。

简单参数可以直接从函数签名和类型注解中推断 Schema，因此 `lookup_order` 不需要额外定义 Pydantic 模型。

### 7. try / except：异常处理

```python
try:
    result = 10 / 2

except Exception as e:
    print("发生错误：", e)
```

作用：

- `try`：尝试执行代码。
- `except`：发生异常时执行。
- `Exception`：捕获常见运行时异常。
- `as e`：将异常对象保存到变量 e。
- `str(e)`：将异常信息转换为字符串。

Day14 使用异常处理，避免工具执行过程中出现错误后直接中断程序。

注意：工具参数 Schema 的校验通常发生在工具函数执行之前，函数内部的 `try/except` 不一定能捕获参数校验失败。

### 8. f-string：格式化字符串

```python
name = "张三"

print(f"你好，{name}")
```

输出：

```text
你好，张三
```

Day14 中：

```python
f"折扣={discount * 100:.0f}%"
f"折后总价={total:.2f}元"
```

格式说明：

- `f""`：格式化字符串。
- `{}`：插入变量或表达式。
- `:.0f`：保留0位小数。
- `:.2f`：保留2位小数。

### 9. 字典与嵌套字典

普通字典：

```python
user = {
    "name": "张三",
    "age": 20
}
```

访问：

```python
user["name"]
```

嵌套字典：

```python
orders = {
    "A1001": {
        "status": "已发货",
        "amount": 199.00
    }
}
```

访问订单状态：

```python
orders["A1001"]["status"]
```

Day14 使用嵌套字典模拟订单数据库，后续可以将其替换为 MySQL 查询。

## 五、实战：多工具 Agent

### 1. 项目结构

```text
day14_Tool_Calling/
└── multi_tool_agent.py
```

### 2. 工具一：订单参数 Schema

```python
class OrderInput(BaseModel):
    price: float = Field(
        gt=0,
        description="商品单价，必须大于0"
    )

    quantity: int = Field(
        gt=0,
        description="购买数量，必须是正整数"
    )

    discount: float = Field(
        ge=0,
        le=1,
        description="折扣比例，0表示不打折，0.2表示打八折"
    )
```

通过 Pydantic 定义订单计算工具的输入参数。

参数说明：

| 参数 | 类型 | 约束 |
|---|---|---|
| price | float | 大于0 |
| quantity | int | 大于0 |
| discount | float | 0到1之间 |

### 3. 工具二：订单金额计算

```python
@tool(args_schema=OrderInput)
def calculate_order(
    price: float,
    quantity: int,
    discount: float
) -> str:
    """计算商品订单的折后总价。适用于用户询问商品总价、订单金额或折扣计算。"""

    try:
        total = price * quantity * (1 - discount)

        return (
            f"订单计算成功："
            f"单价={price}，"
            f"数量={quantity}，"
            f"折扣={discount * 100:.0f}%，"
            f"折后总价={total:.2f}元"
        )

    except Exception as e:
        return f"订单计算失败：{str(e)}"
```

核心计算公式：

```python
total = price * quantity * (1 - discount)
```

例如：

- 单价：100元
- 数量：2件
- 优惠比例：0.2

计算结果：

```text
100 × 2 × (1 - 0.2) = 160元
```

工具返回订单计算结果。

### 4. 工具三：订单查询

```python
@tool
def lookup_order(order_id: str) -> str:
    """根据订单编号查询订单状态和订单金额。适用于用户询问订单进度、订单状态或订单详情。"""

    orders = {
        "A1001": {
            "status": "已发货",
            "amount": 199.00
        },
        "A1002": {
            "status": "待付款",
            "amount": 299.00
        },
        "A1003": {
            "status": "已完成",
            "amount": 599.00
        }
    }

    try:
        order = orders.get(order_id)

        if order is None:
            return f"没有找到订单编号为 {order_id} 的订单。"

        return (
            f"订单编号：{order_id}，"
            f"订单状态：{order['status']}，"
            f"订单金额：{order['amount']:.2f}元"
        )

    except Exception as e:
        return f"订单查询失败：{str(e)}"
```

这里使用嵌套字典模拟订单数据库。

`orders.get(order_id)` 根据订单编号查询对应记录。

如果没有找到订单，返回相应提示。

实际企业项目中，这部分可以替换为 MySQL 查询逻辑。

### 5. 创建 Agent

```python
tools = [
    calculate_order,
    lookup_order
]

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt="""
你是一个业务订单助手。

规则：
1. 用户询问订单金额计算时，调用 calculate_order。
2. 用户询问具体订单状态时，调用 lookup_order。
3. 用户同时提出多个需求时，可以根据需要调用多个工具。
4. 必须依据工具返回结果回答，不得编造订单信息。
5. 普通闲聊不需要调用工具。
"""
)
```

通过 `tools` 列表注册多个工具。

模型根据工具名称、描述和参数 Schema 判断应该调用哪个工具。

### 6. Agent 调用

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

使用 LangChain 1.x 的 `create_agent` 创建 Agent，通过 `invoke()` 提交用户问题。

获取最终回答：

```python
print(result["messages"][-1].content)
```

观察执行过程：

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

`AIMessage.tool_calls` 可以观察模型选择的工具及其参数。

`ToolMessage` 可以观察工具实际执行后的返回结果。

## 六、实际测试结果

### 测试一：单工具调用——订单金额计算

输入：

```text
商品单价100元，购买2件，打八折，计算总价。
```

模型选择：

```text
calculate_order
```

参数：

```python
{
    "price": 100,
    "quantity": 2,
    "discount": 0.2
}
```

工具返回：

```text
订单计算成功：
单价=100.0，
数量=2，
折扣=20%，
折后总价=160.00元
```

测试结果：通过。

### 测试二：单工具调用——订单状态查询

输入：

```text
帮我查询订单A1001的状态。
```

模型选择：

```text
lookup_order
```

参数：

```python
{
    "order_id": "A1001"
}
```

工具返回：

```text
订单编号：A1001，
订单状态：已发货，
订单金额：199.00元
```

测试结果：通过。

### 测试三：多工具调用

输入：

```text
查询订单A1002的状态，同时计算一件单价200元的商品购买3件、打九折后的总价。
```

模型一次生成两个工具调用：

```text
lookup_order
calculate_order
```

工具一返回：

```text
订单编号：A1002，
订单状态：待付款，
订单金额：299.00元
```

工具二返回：

```text
订单计算成功：
单价=200.0，
数量=3，
折扣=10%，
折后总价=540.00元
```

Agent 最终整合两个工具的结果并生成回答。

测试结果：通过。

## 七、Day14 学习成果

本阶段完成了以下内容：

1. 理解 Tool Calling 的完整执行流程。
2. 掌握 Pydantic BaseModel 和 Field。
3. 理解参数类型注解和返回值类型注解。
4. 掌握 `@tool` 和 `args_schema`。
5. 理解 Python 类、函数、装饰器和异常处理。
6. 掌握 f-string 和嵌套字典。
7. 实现两个不同业务工具。
8. 实现 Agent 自主选择工具。
9. 成功完成单工具和多工具调用测试。
10. 通过 AIMessage 和 ToolMessage 观察工具执行轨迹。

## 八、需要注意的工程问题

当前项目属于教学 Demo，仍有一些需要在后续工程化中改进的地方：

1. 订单数据使用 Python 字典模拟，实际业务应接入数据库。
2. 金额计算实际项目建议使用 Decimal，避免浮点数精度问题。
3. 工具异常需要进一步区分参数错误、业务错误和系统错误。
4. 实际 API 工具需要增加超时、重试和错误处理。
5. 工具权限需要根据用户身份和业务场景进行控制。

以上内容将在后续 API Tool、Database Tool 和 Agent 可靠性模块中进一步学习。

## 九、下一阶段学习计划

Day15：API Tool

学习内容：

- HTTP 请求原理
- REST API
- GET / POST
- httpx
- API 封装为 Agent Tool
- 异步请求
- 超时控制
- 错误处理与重试

学习目标：

将当前使用模拟数据的工具升级为能够调用真实 HTTP API 的 Agent 工具。

---

**阶段总结：**

Day14 完成了从单工具调用到多工具调用的进阶学习，掌握了 Pydantic 参数 Schema、LangChain Tool 封装以及 Agent 工具执行机制。

通过订单查询和订单金额计算两个工具，验证了模型自主选择工具、生成参数、执行多个工具并整合结果的完整流程。

当前已具备开发基础业务型 Agent Tool 的能力，下一阶段进入 API Tool，学习将真实外部服务接入 Agent。