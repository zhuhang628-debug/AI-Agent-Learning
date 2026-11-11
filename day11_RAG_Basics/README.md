# Day11–Day13：RAG 知识库与 RAG Agent

## 一、项目介绍

本项目基于 LangChain、HuggingFace Embeddings、Chroma 和 DeepSeek API，实现了一个支持多格式文档加载、文本切分、向量存储、相似度检索和 Agent 自主调用知识库的 RAG 系统。

通过本阶段学习，完成了从基础 RAG 问答到 RAG Agent 的升级，实现了 Agent 根据用户问题判断是否调用知识库，并根据检索结果生成回答。

**核心技术栈：**

- Python
- LangChain 1.x
- LangChain Core
- LangChain OpenAI
- LangChain HuggingFace
- LangChain Chroma
- HuggingFace Embeddings
- Chroma Vector Database
- DeepSeek API

## 二、项目结构

```text
day11_RAG_Basics/
│
├── documents/
│   ├── langgraph.md
│   ├── test.pdf
│   └── test.docx
│
├── chroma_db/
│   └── Day11 原始 RAG 向量数据库
│
├── chroma_multi_db/
│   └── Day12 多格式文档向量数据库
│
├── knowledge.txt
│
├── prepare_documents.py
├── test_embeddings.py
├── test_similarity.py
├── test_top_k.py
├── test_chroma.py
├── build_vector_store.py
├── query_vector_store.py
├── rag_qa.py
│
├── test_markdown_loader.py
├── test_pdf_loader.py
├── test_docx_loader.py
├── load_all_documents.py
├── perpare_all_documents.py
├── build_multi_vector_store.py
├── query_multi_vector_store.py
│
└── rag_agent.py
```

注：`perpare_all_documents.py` 为当前学习过程中使用的脚本文件名，如已重命名为 `prepare_all_documents.py`，请同步调整目录说明。

## 三、Day11：RAG 基础

### 1. 学习内容

- RAG（Retrieval-Augmented Generation）基本原理
- Embedding 文本向量化
- 向量相似度检索
- Chroma 向量数据库
- Top-K 检索
- Metadata 元数据
- Retriever 检索器
- RAG 问答链路
- 检索距离与阈值过滤

### 2. Embedding 模型

使用本地 HuggingFace Embedding 模型：

`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`

模型输出维度：384。

通过 `HuggingFaceEmbeddings` 将文本转换成向量，为后续相似度检索提供基础。

### 3. Chroma 向量数据库

使用 Chroma 保存文档向量、原始文本和 Metadata。

主要操作：

- 创建向量数据库
- 文档向量化与入库
- 持久化保存
- 重新加载已有数据库
- 相似度检索
- Top-K 检索
- Metadata Filter

### 4. 相似度检索与阈值过滤

使用：

```python
vector_store.similarity_search_with_score(
    query=query,
    k=3
)
```

获取检索结果及距离分数。

当前实验采用 Chroma 默认 L2 squared distance，距离越小通常表示越接近。

Day11 小型知识库实验中，根据测试结果暂时采用：

```python
MAX_DISTANCE = 18.0
```

该阈值仅适用于当前实验数据和模型配置，更换知识库或 Embedding 模型后需要重新校准。

### 5. 完整 RAG 问答

使用：

- ChatPromptTemplate
- ChatOpenAI
- DeepSeek API
- StrOutputParser
- LCEL

构建完整 RAG 问答链路：

```text
用户问题
   ↓
向量检索
   ↓
获取相关文档
   ↓
构建 Prompt
   ↓
DeepSeek LLM
   ↓
生成回答
```

实现了知识库中没有相关内容时拒绝回答的基本逻辑。

## 四、Day12：多格式文档加载与向量入库

### 1. 学习目标

实现多种格式文件的统一加载、文本切分、Embedding 和批量向量入库。

支持的文件格式：

- TXT
- Markdown
- PDF
- DOCX

### 2. 文档加载器

使用 LangChain Community 提供的 Loader：

| 文件格式 | Loader |
|---|---|
| TXT | TextLoader |
| Markdown | TextLoader |
| PDF | PyPDFLoader |
| DOCX | Docx2txtLoader |

将不同格式的文件统一转换为 LangChain `Document` 对象。

统一加载函数：

```python
def load_all_documents() -> list[Document]:
    documents = []

    # 根据文件扩展名选择 Loader
    # 将加载结果统一添加到 documents

    return documents
```

其中：

- `page_content` 保存文档文本。
- `metadata` 保存来源路径、PDF 页码等信息。

### 3. 多文档统一切分

使用：

```python
RecursiveCharacterTextSplitter(
    chunk_size=200,
    chunk_overlap=40,
    separators=[
        "\n\n",
        "\n",
        "。",
        "！",
        "？",
        "，",
        " ",
        ""
    ]
)
```

通过：

```python
chunks = text_splitter.split_documents(documents)
```

对所有格式的 Document 统一切分。

`split_documents()` 会将原始文档的 Metadata 传递到对应 Chunk 中，保留文档来源和 PDF 页码等信息。

### 4. 多格式文档向量入库

使用新的 Chroma Collection：

```python
vector_store = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    collection_name="rag_multi_format",
    persist_directory=str(CHROMA_DB_DIR)
)
```

数据库目录：

`chroma_multi_db`

Collection：

`rag_multi_format`

### 5. 实际运行结果

| 文件 | 原始 Document 数量 |
|---|---:|
| langgraph.md | 1 |
| test.docx | 1 |
| test.pdf | 2 |
| 合计 | 4 |

切分与入库结果：

| 项目 | 数量 |
|---|---:|
| 原始 Document | 4 |
| 切分后 Chunk | 22 |
| Chroma 向量记录 | 22 |

所有文件均成功加载、切分和向量化。

### 6. 多格式检索测试

测试问题：

**测试一：**

LangGraph 的 Checkpoint 有什么作用？

检索来源：Markdown。

**测试二：**

图书管理系统有哪些用例？

检索来源：DOCX。

**测试三：**

银行计算机储蓄系统如何处理取款业务？

检索来源：PDF。

三组检索均成功，并且 PDF 检索结果保留了页码 Metadata。

## 五、Day13：RAG + Agent

### 1. 学习目标

将已有 Chroma 知识库封装为 Agent 可以调用的工具，实现 Agent 自主判断是否需要查询知识库。

### 2. 核心技术

- LangChain 1.x Agent
- `@tool`
- Tool Calling
- `create_agent`
- Agent 执行流程
- Chroma 检索
- DeepSeek API

### 3. RAG Tool

使用 `@tool` 将普通 Python 检索函数封装成 Agent 工具：

```python
@tool
def search_knowledge(query: str) -> str:
    """搜索企业知识库。"""

    results = vector_store.similarity_search_with_score(
        query=query,
        k=3
    )

    # 整理检索结果
    # 返回文档内容、来源和页码

    return context
```

工具负责：

1. 接收 Agent 传入的查询问题。
2. 调用 Chroma 执行相似度检索。
3. 获取 Top-K 文档。
4. 提取文本及 Metadata。
5. 将检索结果返回给 Agent。

### 4. 使用 LangChain 1.x 创建 Agent

当前环境：

| 依赖 | 版本 |
|---|---:|
| langchain | 1.3.14 |
| langchain-core | 1.6.13 |
| langchain-openai | 1.4.1 |

使用新版 API：

```python
from langchain.agents import create_agent

agent = create_agent(
    model=llm,
    tools=[search_knowledge],
    system_prompt="你是一个企业知识库助手。"
)
```

调用方式：

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

获取最终回答：

```python
result["messages"][-1].content
```

相比旧版 AgentExecutor 写法，LangChain 1.x 使用 `create_agent()` 统一管理 Agent 执行流程和工具调用。

### 5. Agent 执行流程

```text
用户输入问题
     ↓
DeepSeek LLM
     ↓
判断是否需要调用工具
     ↓
 ┌───────────────┐
 │               │
需要知识库      普通闲聊
 │               │
调用 RAG Tool    直接回答
 │
Chroma 检索
 │
返回相关文档
 │
LLM 整理答案
 │
最终回答
```

### 6. 实际测试结果

| 测试问题 | 预期行为 | 实际结果 |
|---|---|---|
| LangGraph 的 Checkpoint 有什么作用？ | 检索 Markdown | 成功 |
| 图书管理系统有哪些用例？ | 检索 DOCX | 成功 |
| 银行计算机储蓄系统如何处理取款业务？ | 检索 PDF | 成功 |
| 你好，介绍一下你自己。 | 直接回答 | 成功 |

测试结果说明：

1. Agent 能够调用 RAG Tool 检索知识库。
2. 能够从 Markdown、DOCX、PDF 中获取相关内容。
3. 能够根据检索结果组织回答。
4. 能够注明文档来源和 PDF 页码。
5. 普通闲聊不需要强制调用知识库。
6. 对于知识库未提供的信息，能够明确说明资料不足，避免将推断当作原文事实。

## 六、核心技术流程总结

```text
Markdown / PDF / DOCX
          ↓
     Document Loader
          ↓
     List[Document]
          ↓
  RecursiveCharacterTextSplitter
          ↓
        Chunks
          ↓
    HuggingFace Embeddings
          ↓
     Chroma Vector DB
          ↓
     Similarity Search
          ↓
       RAG Tool
          ↓
     LangChain Agent
          ↓
       DeepSeek
          ↓
       最终回答
```

## 七、本阶段学习成果

完成 Day11～Day13 后，掌握了：

- RAG 基本架构和工作原理。
- Embedding 与向量相似度检索。
- Chroma 向量数据库的创建、保存和加载。
- 多格式文档加载。
- Document 与 Metadata。
- RecursiveCharacterTextSplitter。
- Chunk 与 Overlap。
- Top-K 检索和距离分数。
- RAG 问答链路。
- RAG Tool 封装。
- LangChain 1.x `create_agent`。
- Agent 自主调用知识库。
- 基于检索资料生成回答。

## 八、后续学习方向

RAG 基础阶段已完成，后续进入 Tool Calling 进阶。

计划学习：

1. Tool Calling 进阶：参数 Schema、工具选择、多个工具调用。
2. API Tool：HTTP、REST API、httpx、异步、超时、重试。
3. Database Tool：MySQL、SQL 查询、Agent 数据库调用。
4. MCP：MCP 原理、Server、Client 和工具接入。
5. Agent Skills：理解 Skills 与 Tool、Workflow 的区别。
6. Multi-Agent：Supervisor、任务分配和 Agent 协作。
7. 企业级后端工程化与 Harness。

**阶段总结：**

完成了从 RAG 基础到多格式文档知识库，再到 RAG Agent 的完整学习流程，实现了 Agent 自主调用知识库、检索文档并生成回答的基础能力。

本阶段重点不只是掌握框架 API，而是理解文档加载、文本切分、向量检索、工具调用和 Agent 执行之间的关系。