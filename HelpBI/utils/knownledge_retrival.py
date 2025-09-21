import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import jieba
from typing import List, Dict
import json

from tools.my_model import my_embedding

# 1. 加载知识库（示例数据）
knowledge_base = {
    "Date": {
        "This week": "The date range from last Sunday (inclusive) to today (inclusive)",
        "Last Week (LWK)": "The date range from the Saturday of the week before last to the Sunday of last week"
    },
    "Store": {
        "O&O": "Retail stores (Owned & Operated). Note: Both 'Retail' and 'O&O' refer to this channel",
        "EC": "E-commerce channel"
    }
}

# 2. 预处理知识库（拆分为语义单元）
def preprocess_knowledge(kb: Dict) -> List[Dict]:
    chunks = []
    for category, items in kb.items():
        for key, value in items.items():
            chunks.append({
                "text": f"{key}: {value}",  # 组合key-value作为文本
                "metadata": {
                    "category": category,
                    "key": key,
                    "value": value
                }
            })
    return chunks

# # 3. 初始化Embedding模型
# class EmbeddingModel:
#     def __init__(self, model_name="qwen/qwen-7b"):
#         self.model = SentenceTransformer(model_name)
    
#     def encode(self, texts: List[str]) -> np.ndarray:
#         return self.model.encode(texts, convert_to_tensor=False)

# 4. FAISS索引构建
class FaissIndex:
    def __init__(self, dimension=768):
        self.index = faiss.IndexFlatL2(dimension)
    
    def add_embeddings(self, embeddings: np.ndarray):
        self.index.add(embeddings)
    
    def search(self, query_embedding: np.ndarray, k=3) -> tuple:
        distances, indices = self.index.search(query_embedding, k)
        return distances, indices

# 5. 关键词提取（简单版）
# def extract_keywords(query: str) -> List[str]:
#     # 使用jieba分词 + 过滤停用词
#     words = jieba.cut(query)
#     stopwords = {"的", "了", "和", "在"}
#     return [w for w in words if w not in stopwords and len(w) > 1]

# 6. 构建完整系统
class KnowledgeRetriever:
    def __init__(self):
        self.faiss_index = FaissIndex()
        self.knowledge_chunks = []
        
    def build_index(self, knowledge_base: Dict):
        # 预处理知识库
        self.knowledge_chunks = preprocess_knowledge(knowledge_base)
        texts = [chunk["text"] for chunk in self.knowledge_chunks]
        
        # 生成embedding并构建索引
        embeddings = my_embedding(texts)
        self.faiss_index.add_embeddings(embeddings)
    
    def retrieve(self, keywords: List[str], k=3) -> List[Dict]:  
        # 生成query embedding
        query_embedding = my_embedding([query])
        
        # FAISS搜索
        distances, indices = self.faiss_index.search(query_embedding, k)
        
        # 返回结果
        results = []
        for idx, dist in zip(indices[0], distances[0]):
            if idx >= 0:  # 有效索引
                result = self.knowledge_chunks[idx]
                result["score"] = float(1 - dist)  # 转换为相似度分数
                results.append(result)
        
        # 按分数排序
        return sorted(results, key=lambda x: x["score"], reverse=True)

# 7. 使用示例
if __name__ == "__main__":
    # 初始化检索系统
    retriever = KnowledgeRetriever()
    retriever.build_index(knowledge_base)
    
    # 测试查询
    query = ['MTD', 'sales', 'achievement', 'China', 'FP']
    results = retriever.retrieve(query, k=2)
    
    print(f"\nQuery: {query}")
    print("Top results:")
    for res in results:
        print(f"- {res['text']} (Score: {res['score']:.2f})")