
from pathlib import Path

from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

from load_all_documents import load_all_documents
from langchain_text_splitters import RecursiveCharacterTextSplitter


# 1. 路径配置
BASE_DIR = Path(__file__).resolve().parent
CHROMA_DB_DIR = BASE_DIR / "chroma_multi_db"

# 2. 加载环境变量
load_dotenv(BASE_DIR.parent / ".env")

# 3. 加载文档
documents = load_all_documents()

# 4. 文本切分
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=200,
    chunk_overlap=40,
    separators=["\n\n", "\n", "。", "！", "？", "，", " ", ""]
)

chunks = text_splitter.split_documents(documents)

print(f"\n原始 Document 数量：{len(documents)}")
print(f"切分后 Chunk 数量：{len(chunks)}")


# 5. 初始化 Embedding 模型
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)


# 6. 创建 Chroma 向量数据库
vector_store = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    collection_name="rag_multi_format",
    persist_directory=str(CHROMA_DB_DIR)
)


print("\n========== 向量数据库创建成功 ==========")
print("数据库路径：", CHROMA_DB_DIR)
print("Collection：rag_multi_format")
print("向量数量：", vector_store._collection.count())
