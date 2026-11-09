import numpy as np
from langchain_huggingface import HuggingFaceEmbeddings

#1.加载本地Embedding模型
embeddings=HuggingFaceEmbeddings(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

#2.定义用户问题
query="LangGraph如何保存工作流状态？"

#3.准备知识库
documents = [
    "LangGraph 使用 State 保存工作流中的共享数据。",
    "Checkpoint 用于保存工作流状态的历史快照。",
    "LangGraph 通过 Node 执行工作流中的具体任务。",
    "Python 可以使用列表保存多个数据。",
    "今天中午我吃了一碗牛肉面。"
]

#4.将用户问题转换为向量
query_vector=np.array(embeddings.embed_query(query))

#5.将所有知识文本转换为向量
document_vectors=embeddings.embed_documents(documents)

# 6. 保存每条文本的相似度
results = []

for text, vector in zip(documents, document_vectors):

    vector = np.array(vector)

    # 计算余弦相似度
    similarity = np.dot(query_vector, vector) / (
        np.linalg.norm(query_vector) * np.linalg.norm(vector)
    )

    results.append({
        "text": text,
        "score": float(similarity)
    })

# 7. 按照相似度从高到低排序
results = sorted(
    results,
    key=lambda item: item["score"],
    reverse=True
)

# 8. 取 Top-3 结果
top_k = 3
top_results = results[:top_k]

# 9. 输出检索结果
print("\n用户问题：", query)
print(f"\nTop-{top_k} 检索结果：")

for rank, item in enumerate(top_results, start=1):
    print(f"\n第 {rank} 名")
    print("知识内容：", item["text"])
    print("相似度：", f"{item['score']:.4f}")