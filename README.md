# AI-Agent-Learning

AI Agent 应用开发学习项目。

目标：通过项目实践掌握大模型应用开发技术，为 AI Agent 实习岗位做准备。

---

# Day 1：FastAPI + DeepSeek API 接入

## 学习目标

搭建第一个大模型应用后端服务，实现：

* FastAPI Web 服务
* 调用 DeepSeek 大语言模型
* 基础聊天接口

---

## 技术栈

* Python 3.10
* FastAPI
* Uvicorn
* OpenAI SDK
* DeepSeek API
* Git / GitHub

---

## 项目结构

```
AI-Agent-Learning

├── main.py              # FastAPI服务入口
├── chat_history.py      # 对话历史管理
├── .env                 # 环境变量(API Key)
├── requirements.txt     # 项目依赖
└── README.md            # 学习记录
```

---

# Day 1 学习内容

## 1. FastAPI基础

FastAPI 是 Python 的 Web 开发框架，用于快速构建 API 服务。

基本流程：

```
用户请求

↓

FastAPI接口

↓

Python业务逻辑

↓

返回结果
```

---

## 2. Uvicorn启动服务

启动命令：

```bash
uvicorn main:app --reload
```

含义：

* uvicorn：Python Web服务器
* main：main.py文件
* app：FastAPI实例对象
* --reload：代码修改后自动重启

---

## 3. 接入DeepSeek大模型

使用 OpenAI 兼容接口调用 DeepSeek：

流程：

```
用户输入

↓

FastAPI

↓

OpenAI SDK

↓

DeepSeek API

↓

模型返回结果
```

---

## 4. Git版本管理

学习Git基础：

```bash
git init

git add .

git commit -m "message"

git log

git push
```

掌握：

* 本地仓库
* 远程仓库
* commit版本记录
* GitHub同步

---

# Day 2：Memory + Streaming + SSE

## 学习目标

将普通聊天接口升级为具备实际AI应用能力的接口：

* 多轮对话记忆
* 面向对象Memory设计
* 流式输出
* SSE响应
* Git版本管理


---

# 1. Chat Memory（对话记忆）


## 问题

普通API：

用户:
我叫朱航
↓
模型:
收到


下一次请求：

我叫什么？


模型不知道之前的信息。


原因：

每次请求发送给模型的messages只有当前问题，没有历史上下文。


---


## 解决方案

保存完整历史消息：

system
↓
user
↓
assistant
↓
user


调用大模型时，将完整聊天记录发送给模型。


实现：

`chat_history.py`

负责：

* 保存历史消息
* 添加用户消息
* 保存AI回复
* 返回完整上下文


---


# 2. Message角色理解


大模型消息格式：

```python
{
    "role":"user",
    "content":"你好"
}
```
常见角色：
system
定义AI身份和行为规则。
例如：
你是一名专业的AI助手
作用：
告诉模型：
你是谁
应该如何回答问题
user
用户输入：
介绍一下LangGraph
assistant
模型回复：
LangGraph是一个构建AI Agent的框架
# 3. Memory面向对象重构
第一版Memory
最初使用：
history=[]
通过：
add_message()

get_history()
管理聊天记录。
问题：
所有用户共享同一个history。
结构：
用户A

↓

history


用户B

↓

history
数据无法隔离。
第二版Memory
改造成面向对象形式：
class ChatHistory:
结构：
ChatHistory对象

↓

自己的history列表
代码：
class ChatHistory:

    def __init__(self):

        self.history=[
            {
                "role":"system",
                "content":"你是一个专业的AI助手"
            }
        ]


    def add_message(self, role, content):

        self.history.append(
            {
                "role":role,
                "content":content
            }
        )


    def get_history(self):

        return self.history
优势：
数据隔离
代码结构更清晰
方便后续扩展用户Session
# 4. Streaming流式输出
普通返回
用户请求

↓

等待模型生成完成

↓

一次性返回完整答案
缺点：
用户需要等待较长时间。
流式返回
用户请求

↓

模型生成一部分

↓

立即返回

↓

继续生成
效果类似 ChatGPT 的实时打字效果。
# 5. Streaming实现
DeepSeek调用：
response = client.chat.completions.create(

    model="deepseek-chat",

    messages=get_history(),

    stream=True

)
关键参数：
stream=True
表示开启流式输出。
# 6. Python生成器 yield
流式输出核心：
yield content
区别：
return：
一次返回结果。
yield：
不断产生数据。
流程：
DeepSeek

↓

chunk数据

↓

generate()

↓

yield

↓

StreamingResponse

↓

客户端
# 7. SSE(Server-Sent Events)
SSE 是企业AI应用常用的流式通信方式。
响应格式：
data: 第一段内容

data: 第二段内容

data: 第三段内容
FastAPI：
StreamingResponse(
    generate(),
    media_type="text/event-stream"
)
作用：
让前端可以持续接收模型生成内容。
# 8. 遇到的问题
问题1：response未解析引用
错误：
for chunk in response:
未解析的引用 'response'
原因：
generate函数作用域错误。
解决：
将generate函数放入chat_stream函数内部，使其可以访问response变量。
问题2：Git push连接GitHub超时
错误：
Failed to connect to github.com:443
原因：
Git没有使用Clash代理。
解决：
配置Git代理：
git config --global http.proxy http://127.0.0.1:7897

git config --global https.proxy http://127.0.0.1:7897
成功上传GitHub。
当前项目能力
目前已经实现：
✅ FastAPI后端服务
✅ DeepSeek大模型调用
✅ 多轮对话Memory
✅ 面向对象Memory
✅ Streaming流式输出
✅ SSE接口
✅ Git版本管理
✅ GitHub同步
当前架构：
用户

↓

FastAPI

↓

ChatHistory Memory

↓

DeepSeek LLM

↓

Streaming SSE

↓

返回结果
Git提交记录
当前版本：
init: FastAPI + DeepSeek聊天接口

↓

docs: 添加 README 和学习笔记

↓

add chat memory and streaming response

↓

docs:update learning notes for day1 and day2

↓

refactor chat history to class based memory
# Day2总结
完成内容：
理解大模型消息格式 system/user/assistant
实现聊天上下文Memory
学习Python生成器yield
实现Streaming流式输出
实现SSE通信
使用面向对象方式重构Memory
解决Git代理连接问题

# Day 3：LangChain 基础
## 学习目标
从直接调用大模型 API 升级到使用 LangChain 框架开发大模型应用。
学习：
* LangChain框架基础
* ChatOpenAI模型封装
* PromptTemplate提示词模板
* Chain链式调用
* LCEL表达式
* Prompt Engineering基础
---
# 1. 为什么需要LangChain
之前调用DeepSeek：
```
用户
↓
FastAPI
↓
OpenAI SDK
↓
DeepSeek API
↓
返回结果
```
这种方式可以完成基础聊天。
但是实际AI应用需要更多能力：
* Prompt管理
* Memory管理
* Tool调用
* Agent流程控制
如果全部自己开发，代码会越来越复杂。
因此引入LangChain框架。
---
# 2. LangChain介绍
LangChain 是一个用于构建大语言模型应用的开发框架。
核心组件：
```
LLM
↓
Prompt
↓
Chain
↓
Memory
↓
Tool
↓
Agent
```
对应关系：
| 原项目实现 | LangChain |
|---|---|
| OpenAI SDK调用 | ChatOpenAI |
| history列表 | Memory |
| system提示词 | PromptTemplate |
| 多步骤流程 | Chain |
| 函数调用 | Tool |
| 自主决策 | Agent |
---
# 3. 安装LangChain
安装：
```bash
pip install langchain langchain-openai
```
主要依赖：
## langchain
核心框架：
负责：
* Prompt
* Chain
* Agent
## langchain-openai
模型接口封装。
由于DeepSeek兼容OpenAI接口：
```
LangChain
↓
ChatOpenAI
↓
DeepSeek API
```
---
# 4. ChatOpenAI调用DeepSeek
创建：
`day3_langchain.py`
代码：
```python
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
load_dotenv()
llm = ChatOpenAI(
    model="deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1"
)
response = llm.invoke(
    "什么是AI Agent？"
)
print(response.content)
```
运行：
```bash
python day3_langchain.py
```
成功返回：
```
AI Agent是一种能够自主完成任务的智能系统...
```
---
# 5. ChatOpenAI理解
创建模型对象：
```python
llm = ChatOpenAI()
```
作用：
将大模型接口封装成LangChain对象。
之前：
```python
client.chat.completions.create()
```
现在：
```python
llm.invoke()
```
---
# 6. invoke调用方式
LangChain统一调用方式：
```python
invoke()
```
例如：
```python
response = llm.invoke(
    "什么是LangChain？"
)
```
返回：
```python
AIMessage
```
不是普通字符串。
获取内容：
```python
response.content
```
---
# 7. PromptTemplate（提示词模板）
## 问题
直接调用：
```python
llm.invoke(
"什么是AI Agent？"
)
```
Prompt写死，不方便复用。
## 解决方案
使用模板：
```
固定提示词
+
用户输入
=
最终Prompt
```
例如：
```
你是一名AI Agent开发导师。
请回答：
{question}
```
其中：
```
{question}
```
是变量。
---
# 8. 创建PromptTemplate
代码：
```python
from langchain_core.prompts import ChatPromptTemplate
prompt = ChatPromptTemplate.from_template(
    """
你是一名AI Agent开发导师。
请回答：
{question}
"""
)
```
调用：
```python
message = prompt.invoke(
    {
        "question":"什么是LangGraph？"
    }
)
```
作用：
自动替换模板变量。
---
# 9. Chain链式调用
Prompt负责：
```
组织问题
```
LLM负责：
```
生成答案
```
组合：
```
Prompt
↓
LLM
↓
Answer
```
代码：
```python
chain = prompt | llm
```
其中：
```
|
```
表示管道连接。
---
# 10. LCEL表达式
LangChain Expression Language（LCEL）
用于连接不同组件。
例如：
```python
chain = prompt | llm
```
执行流程：
```
用户输入
↓
Prompt模板格式化
↓
LLM生成回答
↓
返回结果
```
---
# 11. 手动输入问题
之前：
```python
question="什么是LangGraph？"
```
问题固定。
修改：
```python
question=input("请输入你的问题：")
```
实现：
```
用户输入
↓
PromptTemplate
↓
Chain
↓
DeepSeek
↓
返回答案
```
---
# 12. 当前项目能力
目前已经实现：
✅ FastAPI后端服务
✅ DeepSeek大模型调用
✅ Chat Memory
✅ Streaming流式输出
✅ SSE响应
✅ 面向对象Memory
✅ LangChain环境搭建
✅ ChatOpenAI调用
✅ PromptTemplate
✅ Chain链式调用
当前架构：
```
用户
↓
PromptTemplate
↓
LangChain Chain
↓
ChatOpenAI
↓
DeepSeek LLM
↓
返回结果
```
---
# 13. Day3总结
今天学习内容：
* 理解为什么需要LangChain
* 学习LangChain核心结构
* 使用ChatOpenAI调用DeepSeek
* 理解invoke调用方式
* 学习PromptTemplate
* 学习变量替换
* 学习Chain链式调用
* 理解LCEL表达式

# Day 4：LangChain Agent开发
## 学习目标
从LangChain Chain进入AI Agent开发。
学习：
* Agent基本概念
* Chain和Agent区别
* Tool工具调用
* AgentExecutor
* 多Tool Agent
* Agent Memory
目标：
实现一个具备工具调用和记忆能力的AI Agent。
---
# 1. 什么是Agent
Day3学习的Chain：
```
用户
↓
Prompt
↓
LLM
↓
回答
```
Chain流程固定，只能完成固定任务。
但是实际AI应用需要：
* 查询数据库
* 调用API
* 搜索信息
* 执行计算
因此需要Agent。
Agent：
```
用户
↓
Agent
↓
分析任务
↓
调用工具
↓
返回结果
↓
生成答案
```
Agent本质：
```
LLM + Tool + 执行流程
```
---
# 2. Chain和Agent区别
## Chain
特点：
* 流程固定
* 不会自主选择
* 不调用外部工具
流程：
```
用户
↓
Prompt
↓
LLM
↓
答案
```
## Agent
特点：
* 流程动态
* 可以自主选择工具
* 可以完成复杂任务
流程：
```
用户
↓
Agent
↓
LLM判断
↓
Tool调用
↓
结果返回
↓
最终回答
```
---
# 3. Tool工具
Tool是Agent连接外部能力的方法。
LLM负责：
```
理解问题
生成语言
```
Tool负责：
```
执行任务
获取数据
```
例如：
* 天气查询
* 搜索
* 计算
---
# 4. 创建Tool
代码：
```python
from langchain_core.tools import tool
@tool
def search_weather(city:str):
    """
    查询城市天气
    """
    return f"{city}今天晴天，温度25度"
```
@tool作用：
将普通Python函数转换成LangChain Tool。
Agent可以识别：
```
工具名称
工具描述
参数
```
---
# 5. Tool调用流程
用户：
```
上海今天的天气怎么样？
```
LLM分析：
```
需要天气信息
```
生成：
```python
tool_calls=[
{
"name":"search_weather",
"args":{
"city":"上海"
}
}
]
```
流程：
```
用户
↓
LLM判断
↓
Tool调用
↓
返回结果
```
---
# 6. AgentExecutor
手写Agent流程：
```
LLM判断
↓
调用Tool
↓
获得结果
↓
再次调用LLM
↓
生成回答
```
工具多时流程复杂。
LangChain提供：
```
AgentExecutor
```
自动管理：
```
思考
↓
调用工具
↓
观察结果
↓
生成回答
```
代码：
```python
agent=create_tool_calling_agent(
    llm,
    tools,
    prompt
)
executor=AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True
)
```
---
# 7. 多Tool Agent
原本：
```
Agent
↓
天气Tool
```
升级：
```
Agent
↓
----------------
天气Tool
计算Tool
----------------
```
新增计算工具：
```python
@tool
def calculator(expression:str):
    """
    数学计算工具
    """
    result=eval(expression)
    return f"计算结果:{result}"
```
测试：
```
上海天气怎么样？
↓
search_weather
```
```
2*3是多少？
↓
calculator
```
说明Agent可以根据问题自主选择工具。
---
# 8. Agent Memory
普通Agent：
```
用户：我叫朱航
AI：你好朱航
用户：我叫什么？
AI：不知道
```
原因：
没有保存历史消息。
加入Memory：
```
用户
↓
Memory保存
↓
Agent读取历史
↓
LLM回答
```
---
# 9. 创建AgentMemory
代码：
```python
from langchain_core.messages import HumanMessage,AIMessage
class AgentMemory:
    def __init__(self):
        self.messages=[]
    def add_user_message(self,content):
        self.messages.append(
            HumanMessage(content=content)
        )
    def add_ai_message(self,content):
        self.messages.append(
            AIMessage(content=content)
        )
    def get_messages(self):
        return self.messages
```
---
# 10. Memory测试
保存：
```
HumanMessage:
我叫朱航
```
保存：
```
AIMessage:
你好朱航
```
再次输入：
```
我叫什么？
```
AI：
```
你叫朱航
```
说明Memory已经接入Agent。
---
# 11. 当前项目架构
```
用户
↓
AgentExecutor
↓
----------------
Memory
Tools
----------------
↓
LLM
↓
DeepSeek
↓
最终回答
```
---
# 12. Day4完成能力
目前掌握：
✅ LangChain Agent基础
✅ Tool工具开发
✅ @tool装饰器
✅ Tool Calling
✅ AgentExecutor
✅ 多Tool Agent
✅ Agent Memory
对应AI Agent实习要求：
```
LangChain框架
Agent开发
大模型应用开发
```
---
# 13. 遇到的问题
## calculator返回None
原因：
函数没有return。
错误：
```python
print(result)
```
正确：
```python
return result
```
## Memory没有get_messages方法
原因：
方法名称错误：
```python
get_message()
```
修改：
```python
get_messages()
```
---
# Day4总结
今天完成：
```
Chain
↓
Tool
↓
Agent
↓
Multi Tool
↓
Memory Agent
```
AI Agent核心结构：
```
LLM
+
Tools
+
Memory
+
AgentExecutor
=
AI Agent
```