from pathlib import Path
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from prepare_documents import load_documents,split_documents

#1.获取当前文件所在目录
BASE_DIR=Path(__file__).resolve().parent

#2.设置Chroma数据库保存位置
CHROMA_DIR=BASE_DIR / "chroma_db"

#3.加载本地Embedding模型
embeddings=HuggingFaceEmbeddings(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)
def build_vector_store():

    #4.加载原始知识文档
    documents=load_documents()
    print(f"原始文档数量：{len(documents)}")

    #5.切分文档
    chunks=split_documents(documents)
    print(f"切分后的文本块数量：{len(chunks)}")

    #6.创建Chroma向量数据库
    vector_store=Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name="rag_knowledge",
        persist_directory=str(CHROMA_DIR),
    )
    print("\n向量数据库创建成功！")
    print("数据库保存位置：", CHROMA_DIR)
    print("数据库中的文本块数量：", vector_store._collection.count())

    return vector_store
if __name__ =="__main__":
    build_vector_store()