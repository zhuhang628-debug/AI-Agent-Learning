from langchain_huggingface import HuggingFaceEmbeddings

#1.加载本地Embedding模型
embeddings=HuggingFaceEmbeddings(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

#2.准备一段测试文本
text="LangGraph使用State保存工作流中的共享数据"

#3.将文本转换为向量
vector=embeddings.embed_query(text)

#4.输出向量信息
print("原始文本：",text)
print("向量维度：",len(vector))
print("向量前10个值：",vector[:10])