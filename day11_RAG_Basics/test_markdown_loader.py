from pathlib import Path
from langchain_community.document_loaders import TextLoader

#1.获取当前文件目录
BASE_DIR = Path(__file__).resolve().parent

#2.设置Markdown 文件路径
FILE_PATH = BASE_DIR / "documents" / "langgraph.md"

# 3. 加载 Markdown 文档
loader = TextLoader(
    str(FILE_PATH),
    encoding="utf-8"
)

# 4. 加载文档
documents = loader.load()


# 5. 输出加载结果
print("文档数量：", len(documents))

for index, document in enumerate(documents, start=1):

    print(f"\n========== 文档 {index} ==========")

    print("文档内容：")
    print(document.page_content)

    print("\n文档元数据：")
    print(document.metadata)