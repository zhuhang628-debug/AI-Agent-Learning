
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


# 1. 获取当前文件目录
BASE_DIR = Path(__file__).resolve().parent

# 2. 加载项目根目录的 .env
load_dotenv(BASE_DIR.parent / ".env")

# 3. 设置 Chroma 数据库路径
CHROMA_DIR = BASE_DIR / "chroma_db"

# 4. 加载 Embedding 模型
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

# 5. 连接 Chroma 向量数据库
vector_store = Chroma(
    collection_name="rag_knowledge",
    persist_directory=str(CHROMA_DIR),
    embedding_function=embeddings
)

# 6. 设置距离阈值
MAX_DISTANCE = 18.0


# 7. 检索知识并过滤低相关性结果
def search_knowledge(query: str, k: int = 3):

    results = vector_store.similarity_search_with_score(
        query=query,
        k=k,
        filter={"source": "knowledge.txt"}
    )

    filtered_results = [
        (document, score)
        for document, score in results
        if score <= MAX_DISTANCE
    ]

    documents = [
        document for document, score in filtered_results
    ]

    return documents


# 8. 初始化 DeepSeek
llm = ChatOpenAI(
    model="deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1",
    temperature=0
)


# 9. 创建 RAG Prompt
prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """你是一个专业的知识库问答助手。

请严格根据下面提供的知识库内容回答用户问题。

要求：
1. 只能依据知识库内容回答。
2. 如果知识库没有相关信息，明确告诉用户不知道。
3. 不要编造知识库中不存在的事实。
4. 回答要清晰、准确、有条理。

知识库内容：
{context}
"""
    ),
    ("human", "{question}")
])


# 10. 构建 RAG Chain
rag_chain = prompt | llm | StrOutputParser()


# 11. 完整 RAG 问答
def rag_qa(question: str):

    # 第一步：检索知识
    documents = search_knowledge(question)

    # 第二步：判断检索结果是否为空
    if not documents:
        print("\n知识库中没有找到相关内容，无法回答。")
        return

    # 第三步：拼接知识片段
    context = "\n\n".join(
        document.page_content for document in documents
    )

    # 第四步：调用大语言模型
    answer = rag_chain.invoke({
        "context": context,
        "question": question
    })

    # 第五步：输出结果
    print("\n========== RAG 检索结果 ==========")

    for index, document in enumerate(documents, start=1):
        print(f"\n知识片段 {index}：")
        print(document.page_content)

    print("\n========== DeepSeek 生成回答 ==========")
    print(answer)


# 12. 程序入口
if __name__ == "__main__":

    while True:

        question = input("\n请输入你的问题（输入 q 退出）：")

        if question.strip().lower() == "q":
            break

        if not question.strip():
            print("问题不能为空！")
            continue

        rag_qa(question)
