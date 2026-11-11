
import os
from pathlib import Path

from dotenv import load_dotenv

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent


# ==========================================
# 1. 路径配置与环境变量加载
# ==========================================

BASE_DIR = Path(__file__).resolve().parent

CHROMA_DB_DIR = BASE_DIR / "chroma_multi_db"

# 加载项目根目录下的 .env
load_dotenv(BASE_DIR.parent / ".env")

api_key = os.getenv("DEEPSEEK_API_KEY")

if not api_key:
    raise ValueError(
        "没有找到 DEEPSEEK_API_KEY，请检查项目根目录下的 .env 文件"
    )


# ==========================================
# 2. 加载 Embedding 模型
# ==========================================

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)


# ==========================================
# 3. 加载已有 Chroma 向量数据库
# ==========================================

vector_store = Chroma(
    collection_name="rag_multi_format",
    embedding_function=embeddings,
    persist_directory=str(CHROMA_DB_DIR)
)

print("Chroma 数据库连接成功")
print("当前向量数量：", vector_store._collection.count())


# ==========================================
# 4. 定义 RAG Tool
# ==========================================

@tool
def search_knowledge(query: str) -> str:
    """
    搜索企业知识库。

    当用户询问知识库中的文档、案例、定义、
    实验内容或具体业务信息时，使用此工具。
    """

    # 执行相似度检索
    results = vector_store.similarity_search_with_score(
        query=query,
        k=3
    )

    # 没有检索结果
    if not results:
        return "知识库中没有检索到相关内容。"

    context_list = []

    for index, (document, score) in enumerate(results, start=1):

        # 获取文档来源
        source = document.metadata.get(
            "source",
            "未知来源"
        )

        # 获取 PDF 页码
        page = document.metadata.get("page_label")

        source_info = f"来源：{source}"

        if page:
            source_info += f"，页码：{page}"

        # 整理检索结果
        context = (
            f"资料 {index}\n"
            f"{source_info}\n"
            f"距离分数：{score:.4f}\n"
            f"内容：{document.page_content}"
        )

        context_list.append(context)

    return "\n\n".join(context_list)


# ==========================================
# 5. 初始化 DeepSeek LLM
# ==========================================

llm = ChatOpenAI(
    model="deepseek-chat",
    api_key=api_key,
    base_url="https://api.deepseek.com/v1",
    temperature=0
)


# ==========================================
# 6. 创建 Agent
# ==========================================

tools = [search_knowledge]

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt="""
你是一个企业知识库助手。

你的任务是根据用户问题，合理使用知识库工具，
提供准确、可靠的回答。

执行规则：

1. 用户询问知识库中的具体内容时，
   应优先调用 search_knowledge 工具。

2. 如果用户询问普通闲聊问题，
   可以直接回答，不需要调用知识库。

3. 回答知识库问题时，
   必须以工具返回的资料为依据。

4. 如果知识库没有提供相关信息，
   明确告诉用户没有找到相关依据。

5. 不要编造文档中不存在的内容。

6. 如果检索资料提供了文件来源和页码，
   回答时尽可能注明。

7. 对于资料中没有明确说明的内容，
   不要自行推断为确定事实。
"""
)


# ==========================================
# 7. 交互式测试
# ==========================================

if __name__ == "__main__":

    print("\n========== RAG Agent 已启动 ==========")
    print("输入 q 退出程序")

    while True:

        question = input("\n请输入问题：").strip()

        if question.lower() == "q":
            print("程序已退出")
            break

        if not question:
            print("问题不能为空，请重新输入")
            continue

        try:
            # 调用 Agent
            result = agent.invoke({
                "messages": [
                    {
                        "role": "user",
                        "content": question
                    }
                ]
            })

            # 获取最终回答
            final_message = result["messages"][-1]

            print("\n========== Agent 回答 ==========")
            print(final_message.content)

        except Exception as e:
            print("\nAgent 执行失败：")
            print(type(e).__name__, str(e))
