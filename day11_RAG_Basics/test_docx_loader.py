
from pathlib import Path

from langchain_community.document_loaders import Docx2txtLoader


# 1. 获取当前文件目录
BASE_DIR = Path(__file__).resolve().parent

# 2. 设置 DOCX 文件路径
FILE_PATH = BASE_DIR / "documents" / "test.docx"


# 3. 创建 Word 加载器
loader = Docx2txtLoader(str(FILE_PATH))

# 4. 加载 Word 文档
documents = loader.load()


# 5. 输出加载结果
print("Word 文档数量：", len(documents))

for index, document in enumerate(documents, start=1):

    print(f"\n========== 文档 {index} ==========")

    print("文档内容：")
    print(document.page_content)

    print("\n文档元数据：")
    print(document.metadata)
