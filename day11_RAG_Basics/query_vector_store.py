
from pathlib import Path

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma


# 1. 获取当前文件所在目录
BASE_DIR = Path(__file__).resolve().parent

# 2. 设置数据库路径
CHROMA_DIR = BASE_DIR / "chroma_db"

# 3. 加载 Embedding 模型
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

# 4. 连接已经存在的 Chroma 数据库
vector_store = Chroma(
    collection_name="rag_knowledge",
    persist_directory=str(CHROMA_DIR),
    embedding_function=embeddings
)


# 5. 普通知识检索
MAX_DISTANCE = 18.0


def search_knowledge(query: str, k: int = 3):

    results = vector_store.similarity_search_with_score(
        query=query,
        k=k,
        filter={"source": "knowledge.txt"}
    )

    # 过滤不相关的知识片段
    filtered_results = [
        (document, score)
        for document, score in results
        if score <= MAX_DISTANCE
    ]

    # 如果没有足够相关的结果
    if not filtered_results:
        print("\n知识库中没有找到相关内容，无法回答。")
        return []

    print(f"\n用户问题：{query}")
    print(f"有效检索结果数量：{len(filtered_results)}")

    for index, (document, score) in enumerate(filtered_results, start=1):
        print(f"\n===== 检索结果 {index} =====")
        print(f"距离分数：{score:.4f}")
        print("知识内容：", document.page_content)
        print("元数据：", document.metadata)

    return [document for document, score in filtered_results]


# 6. 测试不同问题的检索距离
def test_retrieval_scores():

    test_queries = [
        "LangGraph 如何保存工作流状态？",
        "什么是 LangGraph 的 State？",
        "什么是 RAG？",
        "文本切分为什么需要 overlap？",
        "Python 的 GIL 是什么？",
        "如何使用 Java 开发 Web 项目？"
    ]

    for query in test_queries:

        results = vector_store.similarity_search_with_score(
            query=query,
            k=3,
            filter={"source": "knowledge.txt"}
        )

        print(f"\n用户问题：{query}")

        for index, (document, score) in enumerate(results, start=1):
            print(f"\n结果 {index}")
            print(f"距离：{score:.4f}")
            print(f"内容：{document.page_content[:100]}...")


# 7. 程序入口
# 7. 程序入口
if __name__ == "__main__":

    while True:
        query = input("\n请输入问题（输入 q 退出）：")

        if query.strip().lower() == "q":
            break

        if not query.strip():
            print("问题不能为空！")
            continue

        search_knowledge(query, k=3)
