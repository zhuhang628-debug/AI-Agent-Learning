
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader


# 1. 获取当前文件目录
BASE_DIR = Path(__file__).resolve().parent

# 2. 设置 PDF 文件路径
FILE_PATH = BASE_DIR / "documents" / "test.pdf"


# 3. 创建 PDF 加载器
loader = PyPDFLoader(str(FILE_PATH))

# 4. 加载 PDF 文档
documents = loader.load()


# 5. 输出加载结果
print("PDF 页面数量：", len(documents))

for index, document in enumerate(documents, start=1):

    print(f"\n========== 第 {index} 页 ==========")

    print("页面内容：")
    print(document.page_content)

    print("\n页面元数据：")
    print(document.metadata)
