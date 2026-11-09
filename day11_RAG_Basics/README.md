# Day11：RAG 基础与完整知识库问答系统

## 一、今日学习目标

完成 RAG（Retrieval-Augmented Generation，检索增强生成）的核心学习，掌握从文档加载、文本切分、Embedding 向量化、Chroma 向量存储，到 Retriever 检索、距离阈值过滤和 LLM 生成回答的完整流程。

## 二、核心知识

### 1. RAG 基本原理

RAG 是检索增强生成技术，通过从外部知识库中检索与用户问题相关的文档片段，将检索结果作为上下文提供给大语言模型，从而辅助模型生成回答。

基本流程：

用户提问 → Embedding 向量化 → 向量数据库检索 → 获取相关文档 → 构建 Prompt → LLM 生成回答。

### 2. Embedding 向量化

使用 HuggingFaceEmbeddings 加载本地 Embedding 模型：

`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`

掌握了将文本转换为向量表示的过程，理解了向量距离与语义相似度之间的关系。

本次使用的模型输出维度为 384。

### 3. Chroma 向量数据库

学习 Chroma 的基本使用，包括：

- `Chroma.from_texts()`：将文本转换为向量并存储。
- `Chroma.from_documents()`：存储 Document 对象及其 Metadata。
- `persist_directory`：指定持久化数据库目录。
- `similarity_search()`：执行相似度检索。
- `similarity_search_with_score()`：检索文档并返回距离分数。

完成了 Chroma 数据库的创建、持久化存储和重新加载。

### 4. Top-K 检索

通过指定 K 值获取距离最接近的前 K 个知识片段。

理解 Top-K 的作用：控制检索候选文档数量，但 Top-K 本身不代表结果一定相关。

### 5. Retriever 检索器

使用 `vector_store.as_retriever()` 将 Chroma 向量数据库转换为 Retriever。

通过 `retriever.invoke(query)` 实现统一的文档检索接口。

### 6. Metadata Filter

学习利用 Metadata 进行检索条件过滤。

本次使用：

`filter={"source": "knowledge.txt"}`

根据文档来源筛选知识片段。

### 7. 距离阈值过滤

通过 `similarity_search_with_score()` 获取原始距离分数，结合距离阈值过滤低相关性结果。

本次实验使用：

`MAX_DISTANCE = 18.0`

当前 Chroma 集合使用默认 L2 距离，距离越小代表向量越接近。

根据六组测试问题的距离分布，选择 18.0 作为当前实验的初始阈值。

注意：该阈值仅适用于当前小型知识库的实验验证，不是通用标准。更换 Embedding 模型或知识库后需要重新评估。

## 三、实践内容

### 1. 文档加载与切分

使用 `prepare_documents.py`：

- 读取 knowledge.txt。
- 将原始文本转换为 LangChain Document 对象。
- 使用 RecursiveCharacterTextSplitter 进行文本切分。
- 设置 chunk_size=200、chunk_overlap=40。
- 保留 source 元数据。

成功将原始知识文档切分为 4 个文本块。

### 2. Embedding 实验

使用本地多语言 Embedding 模型进行文本向量化。

完成了：

- 文本向量生成。
- 向量维度检查。
- 余弦相似度计算。
- 不同问题与知识片段的语义相似度比较。

### 3. Chroma 持久化存储

使用 `build_vector_store.py` 构建持久化向量数据库。

数据库配置：

- Collection：`rag_knowledge`
- 数据库目录：`chroma_db`
- 原始文档数量：1
- 切分后文本块数量：4

成功完成向量数据库构建和数据持久化。

### 4. 向量检索与距离分析

使用 `query_vector_store.py` 完成：

- Chroma 数据库重新加载。
- Top-K 相似度检索。
- 原始 L2 距离查看。
- Retriever 检索。
- Metadata Filter。
- 距离阈值过滤。

通过不同问题测试知识库内外的检索效果。

实验结果：

| 测试问题 | 最小距离 | 结果 |
|---|---:|---|
| LangGraph 如何保存工作流状态？ | 11.2592 | 相关 |
| 什么是 LangGraph 的 State？ | 12.3877 | 相关 |
| 什么是 RAG？ | 13.2242 | 相关 |
| 文本切分为什么需要 overlap？ | 14.6434 | 相关 |
| Python 的 GIL 是什么？ | 28.5161 | 不相关 |
| 如何使用 Java 开发 Web 项目？ | 24.5399 | 不相关 |

根据实验结果设置初始距离阈值 18.0，实现了对低相关性检索结果的过滤。

### 5. 完整 RAG 问答系统

使用 `rag_qa.py` 将 Chroma 检索与 DeepSeek 大语言模型整合。

主要组件：

- HuggingFaceEmbeddings：文本向量化。
- Chroma：向量数据库。
- ChatOpenAI：兼容 DeepSeek API 的模型调用接口。
- ChatPromptTemplate：构建 RAG 提示词。
- StrOutputParser：解析模型输出。
- RAG Chain：通过 LCEL 管道组合 Prompt、LLM 和输出解析器。

核心代码结构：

`rag_chain = prompt | llm | StrOutputParser()`

通过 `search_knowledge()` 执行检索与阈值过滤，再将相关文档拼接为 Context，传入 RAG Chain 生成回答。

增加空检索结果判断：

`if not documents:`

当知识库中没有足够相关的内容时，直接返回，不调用大语言模型。

## 四、运行测试结果

完成四组端到端测试：

| 用户问题 | 实际运行结果 | 测试状态 |
|---|---|---|
| LangGraph 如何保存工作流状态？ | 检索 3 个片段，DeepSeek 正确回答 Checkpoint、thread_id、MemorySaver | 通过 |
| 什么是 RAG？ | 检索 1 个片段，DeepSeek 正确解释 RAG | 通过 |
| Python 的 GIL 是什么？ | 没有相关知识，直接拒答 | 通过 |
| 如何使用 Java 开发 Web 项目？ | 没有相关知识，直接拒答 | 通过 |

四组测试均符合预期，完整 RAG 核心链路运行成功。

## 五、今日项目文件

`day11_RAG_Basics/`

- `knowledge.txt`：知识库原始文档。
- `prepare_documents.py`：文档加载与文本切分。
- `test_embeddings.py`：Embedding 向量化实验。
- `test_similarity.py`：相似度计算实验。
- `test_top_k.py`：Top-K 检索实验。
- `test_chroma.py`：Chroma 基础实验。
- `build_vector_store.py`：构建持久化向量数据库。
- `query_vector_store.py`：向量检索、距离分析及阈值过滤。
- `rag_qa.py`：完整 RAG 知识库问答系统。
- `chroma_db/`：持久化向量数据库。

## 六、今日总结

今天完成了 RAG 基础模块的核心学习，掌握了从文档加载、文本切分、Embedding 向量化、Chroma 向量存储，到 Top-K 检索、Retriever、Metadata Filter 和距离阈值过滤的完整流程。

通过 LangChain LCEL 将 Prompt、DeepSeek 和输出解析器组合为 RAG Chain，实现了完整的知识库问答系统。

同时，通过距离阈值过滤实现了基础的检索拒答机制：当知识库中没有足够相关的内容时，系统直接返回空结果，不再调用大语言模型，避免模型在缺乏知识库依据时生成超出知识库范围的答案。

**今日完成：RAG 核心链路与基础拒答机制。**

## 七、下一步学习计划

1. 学习 Markdown、PDF、DOCX 等不同格式的文档加载。
2. 实现多文档批量加载与文本切分。
3. 完善文档 Metadata 管理。
4. 实现多文档向量数据库构建。
5. 优化 RAG 检索质量。
6. 将 RAG 知识库封装为 Agent Tool，接入 LangGraph Agent。

**Day11 核心学习任务完成，下一阶段进入多格式文档加载与多文档 RAG。**