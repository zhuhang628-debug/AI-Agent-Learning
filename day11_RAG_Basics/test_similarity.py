import numpy as np
from langchain_huggingface import HuggingFaceEmbeddings


#1.加载已经下载好的本地Embedding 模型
embeddings=HuggingFaceEmbeddings(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
)

#2.定义用户问题
query="LangGraph 如何保存工作流状态？"

#3.准备两段候选知识
documents=[
    "LangGraph使用State保存工作流中的共享数据",
    "今天中午我吃了一碗牛肉面。"
]

#4.将用户问题转换成向量
query_vector=np.array(embeddings.embed_query(query))

#5.将候选知识分别转换成向量
document_vectors=np.array(embeddings.embed_documents(documents))

#6.计算每段知识与问题的余弦相似度
for text,vector in zip(documents,document_vectors):
    similarity=np.dot(query_vector,vector)/(
        np.linalg.norm(query_vector)*np.linalg.norm(vector)
    )
    print(f"知识内容：{text}")
    print(f"余弦相似度：{similarity:4f}")
    print("-"*50)