# LangGraph 基础知识

## 一、LangGraph 是什么

LangGraph 是一个用于构建有状态、多步骤 AI 应用的框架。
它支持通过 State、Node 和 Edge 构建工作流。

## 二、State

State 用于保存工作流执行过程中共享的数据。
不同节点可以读取和更新 State 中的信息。

## 三、Checkpoint

Checkpoint 用于保存图执行过程中的状态。
结合 thread_id，可以恢复指定会话的执行状态。

## 四、Agent

Agent 可以根据用户任务决定调用什么工具，
并根据工具执行结果继续完成后续任务。