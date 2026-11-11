
from pathlib import Path

from langchain_core.documents import Document
from langchain_community.document_loaders import (
    TextLoader,
    PyPDFLoader,
    Docx2txtLoader
)


# 1. 获取当前文件目录
BASE_DIR = Path(__file__).resolve().parent

# 2. 设置文档目录
DOCUMENTS_DIR = BASE_DIR / "documents"


# 3. 定义统一文档加载函数
def load_all_documents() -> list[Document]:

    documents = []

    # 遍历 documents 文件夹中的所有文件
    for file_path in DOCUMENTS_DIR.iterdir():

        if not file_path.is_file():
            continue

        suffix = file_path.suffix.lower()

        print(f"\n正在加载：{file_path.name}")

        # 4. 根据文件扩展名选择加载器
        if suffix == ".md":

            loader = TextLoader(
                str(file_path),
                encoding="utf-8"
            )

        elif suffix == ".pdf":

            loader = PyPDFLoader(str(file_path))

        elif suffix == ".docx":

            loader = Docx2txtLoader(str(file_path))

        else:

            print(f"暂不支持的文件格式：{suffix}")
            continue

        # 5. 加载文档
        loaded_documents = loader.load()

        # 6. 将加载结果加入统一列表
        documents.extend(loaded_documents)

        print(f"加载成功，Document 数量：{len(loaded_documents)}")

    return documents


# 7. 测试统一加载
if __name__ == "__main__":

    all_documents = load_all_documents()

    print("\n========== 加载汇总 ==========")

    print("Document 总数量：", len(all_documents))

    for index, document in enumerate(all_documents, start=1):

        print(f"\nDocument {index}")
        print("内容长度：", len(document.page_content))
        print("来源：", document.metadata.get("source"))
