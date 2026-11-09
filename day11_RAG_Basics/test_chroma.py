
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

# 1. 加载 Embedding 模型
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

# 2. 创建 Document 文档对象
documents = [
    Document(
        page_content="LangGraph 使用 State 保存工作流中的共享数据。",
        metadata={"source": "knowledge.txt", "topic": "State"}
    ),
    Document(
        page_content="Checkpoint 用于保存工作流状态的历史快照。",
        metadata={"source": "knowledge.txt", "topic": "Checkpoint"}
    ),
    Document(
        page_content="LangGraph 通过 Node 执行工作流中的具体任务。",
        metadata={"source": "knowledge.txt", "topic": "Node"}
    ),
    Document(
        page_content="Python 可以使用列表保存多个数据。",
        metadata={"source": "python_notes.txt", "topic": "Python"}
    ),
    Document(
        page_content="今天中午我吃了一碗牛肉面。",
        metadata={"source": "daily_notes.txt", "topic": "生活"}
    )
]

# 3. 创建 Chroma 向量数据库
vector_store = Chroma.from_documents(
    documents=documents,
    embedding=embeddings,
    collection_name="langgraph_knowledge",
    persist_directory="./chroma_db_metadata"
)

# 4. 检查知识库数量
print("知识库创建成功！")
print("知识条目数量：", vector_store._collection.count())

# 5. 执行相似度检索
query = "LangGraph 如何保存工作流状态？"

results = vector_store.similarity_search(
    query,
    k=3
)

# 6. 输出检索结果
print("\n用户问题：", query)
print("\nTop-3 检索结果：")

for rank, document in enumerate(results, start=1):
    print(f"\n第 {rank} 名")
    print("知识内容：", document.page_content)
    print("元数据：", document.metadata)
