# Day 5：LangChain Agent项目开发（Travel Agent）
## 学习目标
基于前几天学习内容，完成一个完整的AI Agent项目。
实现：
* LangChain Agent
* Tool Calling
* 多工具协作
* Memory记忆
* FastAPI接口
* Streaming流式输出
最终实现一个旅游规划Agent。
---
# 项目结构
```text
day5_travel_agent
├── tools.py          # Agent工具
├── agent.py          # Agent配置
├── memory.py         # 对话记忆
├── main.py           # FastAPI接口
└── README.md         # 学习记录
```
---
# Day5 学习内容
# 1. Agent基础
## 什么是Agent
普通LLM：
```text
用户输入
↓
大模型
↓
返回答案
```
Agent：
```text
用户输入
↓
LLM分析任务
↓
选择工具
↓
调用工具
↓
整理结果
↓
返回答案
```
Agent具备：
* 思考能力
* 工具调用能力
* 任务规划能力
---
# 2. 创建Tool工具
文件：
```text
tools.py
```
Agent通过Tool扩展能力。
例如：
天气查询：
```python
@tool
def search_weather(city:str):
```
景点查询：
```python
@tool
def search_attraction(city:str):
```
---
# Tool代码解析
## @tool装饰器
```python
@tool
def search_weather(city:str):
```
作用：
将普通Python函数转换为LangChain Tool。
普通函数：
```text
Python函数
```
转换后：
```text
Agent可调用工具
```
## Tool描述信息
例如：
```python
"""
查询城市天气
"""
```
这个描述会提供给LLM。
模型根据描述判断是否需要调用该工具。
---
# 3. 创建Agent
文件：
```text
agent.py
```
Agent组成：
```text
LLM
+
Tools
+
Prompt
↓
Agent
```
核心代码：
```python
create_tool_calling_agent()
```
作用：
创建支持工具调用的Agent。
---
# Agent执行流程
用户：
```text
帮我规划杭州3日游
```
Agent：
```text
分析需求
↓
调用天气Tool
↓
调用景点Tool
↓
生成旅游方案
```
---
# 4. AgentExecutor
代码：
```python
AgentExecutor(
    agent=agent,
    tools=tools
)
```
作用：
执行Agent任务。
负责：
* 接收用户输入
* 调用Agent
* 执行Tool
* 返回结果
---
# 5. Memory对话记忆
文件：
```text
memory.py
```
作用：
保存用户历史信息。
例如：
第一次：
```text
用户：
我喜欢自然景点，不喜欢购物
```
保存：
```text
HumanMessage
```
第二次：
```text
用户：
帮我规划杭州3日游
```
Agent读取历史：
```text
用户喜欢自然景点
不喜欢购物
```
生成个性化方案。
---
# Memory结构
```text
用户消息
↓
HumanMessage
↓
Memory
↓
Agent
↓
AIMessage
```
---
# 6. FastAPI接口化
文件：
```text
main.py
```
将命令行Agent转换为Web服务。
架构：
```text
浏览器
↓
FastAPI
↓
AgentExecutor
↓
DeepSeek
```
启动：
```bash
uvicorn main:app --reload
```
接口：
```text
GET /
```
测试服务。
```text
GET /travel
```
旅游规划接口。
例如：
```text
/travel?message=帮我规划杭州3日游
```
---
# 7. Streaming流式输出
目标：
实现类似ChatGPT的输出效果。
普通：
```text
等待生成完成
↓
一次返回全部内容
```
Streaming：
```text
生成一点
↓
返回一点
↓
继续生成
```
FastAPI：
```python
StreamingResponse()
```
实现流式HTTP响应。
---
# 8. LangChain Agent Streaming问题
最初：
```python
executor.invoke()
```
特点：
一次返回完整结果。
尝试：
```python
executor.stream()
```
发现：
Agent结果仍然可能整体返回。
最终使用：
```python
executor.astream_events()
```
获取Agent事件流。
流程：
```text
LLM生成token
↓
stream event
↓
yield
↓
浏览器显示
```
---
# 9. 最终项目架构
```text
用户
↓
FastAPI
↓
AgentExecutor
↓
LangChain Agent
↓
-----------------
Memory
Tools
-----------------
↓
DeepSeek LLM
↓
StreamingResponse
↓
返回结果
```
---
# 当前项目能力
已经实现：
✅ FastAPI后端服务
✅ DeepSeek大模型调用
✅ LangChain Agent
✅ Tool Calling
✅ 多工具协作
✅ Memory记忆
✅ Streaming输出
✅ Web接口访问
---
# Day5遇到的问题
## 1. Python模块导入问题
错误：
```text
ModuleNotFoundError:
No module named 'day5_travel_agent'
```
原因：
当前目录运行时，不能使用包形式导入。
解决：
修改：
```python
from day5_travel_agent.agent import executor
```
改为：
```python
from agent import executor
```
## 2. Streaming没有实时输出
问题：
使用：
```python
executor.invoke()
```
导致：
```text
等待Agent完成
↓
一次性返回
```
解决：
使用：
```python
executor.astream_events()
```
获取LLM实时输出事件。
---
# Day5总结
通过Day5学习，实现了第一个完整AI Agent应用。
项目能力从：
```text
调用大模型API
```
升级到：
```text
具备工具调用能力的智能Agent
```
掌握：
```text
LLM
↓
Agent
↓
Tool
↓
Memory
↓
Streaming
↓
API服务
```
这是企业AI Agent应用开发的基础架构。
---
