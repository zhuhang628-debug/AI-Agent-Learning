
from langchain_text_splitters import RecursiveCharacterTextSplitter

from load_all_documents import load_all_documents


# 1. 加载所有格式的文档
documents = load_all_documents()

print("\n========== 原始文档统计 ==========")
print("Document 总数量：", len(documents))


# 2. 创建文本切分器
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=200,
    chunk_overlap=40,
    separators=["\n\n", "\n", "。", "！", "？", "，", " ", ""]
)


# 3. 对所有 Document 统一切分
chunks = text_splitter.split_documents(documents)


# 4. 输出切分结果
print("\n========== 切分结果 ==========")
print("Chunk 总数量：", len(chunks))

for index, chunk in enumerate(chunks, start=1):
    print(f"\nChunk {index}")
    print("内容长度：", len(chunk.page_content))
    print("Metadata：", chunk.metadata)
    print("内容预览：", chunk.page_content[:100])
