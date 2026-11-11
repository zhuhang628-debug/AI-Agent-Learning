
from pathlib import Path

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma


# 1. 配置数据库路径
BASE_DIR = Path(__file__).resolve().parent
CHROMA_DB_DIR = BASE_DIR / "chroma_multi_db"


# 2. 初始化 Embedding 模型
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)


# 3. 加载已有向量数据库
vector_store = Chroma(
    collection_name="rag_multi_format",
    embedding_function=embeddings,
    persist_directory=str(CHROMA_DB_DIR)
)


# 4. 定义检索函数
def search_documents(query: str, k: int = 3):
    results = vector_store.similarity_search_with_score(
        query=query,
        k=k
    )

    print(f"\n查询问题：{query}")
    print("=" * 60)

    for index, (document, score) in enumerate(results, start=1):
        print(f"\n结果 {index}")
        print("距离分数：", round(score, 4))
        print("来源：", document.metadata.get("source"))
        print("页码：", document.metadata.get("page"))
        print("内容：", document.page_content)


# 5. 测试不同文档的检索
if __name__ == "__main__":
    while True:
        question = input("\n请输入问题（输入 q 退出）：")

        if question.lower() == "q":
            break

        search_documents(question)
