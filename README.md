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
* 流式输出
* SSE响应

---

# 1. Chat Memory（对话记忆）

## 问题

普通API：

```
用户:
我叫朱航

↓

模型:
收到
```

下一次请求：

```
我叫什么？
```

模型不知道。

---

## 解决方案

保存历史消息：

```
system

↓

user

↓

assistant

↓

user
```

发送完整上下文给大模型。

实现：

`chat_history.py`

负责：

* 保存历史消息
* 添加用户输入
* 保存AI回复

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

## system

定义AI身份：

例如：

```
你是一个专业AI助手
```

---

## user

用户输入：

```
介绍一下LangGraph
```

---

## assistant

模型回复：

```
LangGraph是...
```

---

# 3. Streaming流式输出

## 普通返回

```
用户请求

↓

等待模型生成

↓

一次性返回全部答案
```

## 流式返回

```
用户请求

↓

生成一点

↓

返回一点

↓

继续生成
```

效果类似 ChatGPT 打字效果。

---

# 4. Python生成器 yield

流式输出核心：

```python
yield content
```

区别：

return：

一次返回结果。

yield：

不断产生数据。

流程：

```
DeepSeek

↓

chunk数据

↓

yield

↓

StreamingResponse

↓

客户端
```

---

# 5. SSE(Server-Sent Events)

SSE 是企业AI应用常用的流式通信方式。

响应格式：

```
data: 第一段内容

data: 第二段内容

data: 第三段内容
```

FastAPI：

```python
StreamingResponse(
    generate(),
    media_type="text/event-stream"
)
```

---

# 当前项目能力

目前已经实现：

✅ FastAPI后端服务

✅ DeepSeek大模型调用

✅ 多轮对话Memory

✅ Streaming流式输出

✅ SSE接口

✅ Git版本管理

当前架构：

```
用户

↓

FastAPI

↓

Chat Memory

↓

DeepSeek LLM

↓

Streaming SSE

↓

返回结果
```

---

# Git提交记录

当前版本：

```
init: FastAPI + DeepSeek聊天接口

↓

docs: 添加README和学习笔记

↓

add chat memory and streaming response
```

---
