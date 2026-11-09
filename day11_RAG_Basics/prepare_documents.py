from pathlib import Path
from langchain_core.documents import  Document
from langchain_text_splitters import RecursiveCharacterTextSplitter



#1.获取当前Python文件所在目录
BASE_DIR=Path(__file__).resolve().parent

#2.定位知识库文件
KNOWLEDGE_FILE=BASE_DIR / "knowledge.txt"


def load_documents() -> list[Document]:
    if not KNOWLEDGE_FILE.exists():
        raise FileNotFoundError(f"知识库文件不存在：{KNOWLEDGE_FILE}")

    text = KNOWLEDGE_FILE.read_text(encoding="utf-8")

    if not text.strip():
        raise ValueError("知识库文件为空")

    document = Document(
        page_content=text,
        metadata={"source": KNOWLEDGE_FILE.name}
    )

    return [document]

def split_documents(
        documents: list[Document]
) -> list[Document]:
    """将长文档切分为较小的文本块。"""
    splitter=RecursiveCharacterTextSplitter(
        chunk_size=200,
        chunk_overlap=40,
        length_function=len,
        separators=["\n\n", "\n", "。", "！", "？", "，", " ", ""]
    )
    return splitter.split_documents(documents)

if __name__ == "__main__":
    documents=load_documents()
    chunks=split_documents(documents)
    print("原始文档元数据：", documents[0].metadata)
    print("切分后第一个文本块的元数据：", chunks[0].metadata)
    print(f"原始文档数量：{len(documents)}")
    print(f"切分后的文本块数量：{len(chunks)}")

    for index,chunk in enumerate(chunks,start=1):
        print(f"\n===== 文本块 {index} =====")
        print(chunk.page_content)
        print("元数据：", chunk.metadata)