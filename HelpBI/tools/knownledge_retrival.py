import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import jieba
from typing import List, Dict
import json
import os
from pathlib import Path

from .my_model import ChatModel

# 1. 加载知识库
knowledge_base = {
    "Date": {
        "This Week": "The date range from last Sunday (inclusive) to today (inclusive)",
        "Last Week (LWK)": "The date range from the Saturday of the week before last to the Sunday of last week",
        "Week-to-Date (WTD)": "The date range from the first day (Sunday) of the current week to yesterday",
        "Month-to-Date (MTD)": "The date range from the first day of the current month to yesterday",
        "Quarter-to-Date (QTD)": "The date range from the first day of the current fiscal quarter to yesterday",
        "Year-to-Date (YTD)": "The date range from the first day of the current calendar year to yesterday",
        "Calendar Year-to-Date (C-YTD)": "Alias for YTD (From the first day of this year to yesterday)",
        "Fiscal Year-to-Date (F-YTD)": "The date range from the first day of the current fiscal year (April 1st) to yesterday",
        "Fiscal Year 2023 (FY23)": "The period from April 1, 2022, to March 31, 2023",
        "Fiscal Year 2024 (FY24)": "The period from April 1, 2023, to March 31, 2024",
        "Fiscal Year 2025 (FY25)": "The period from April 1, 2024, to March 31, 2025",
        "Fiscal Year 2026 (FY26)": "The period from April 1, 2025, to March 31, 2026",
        "Fiscal Year 2027 (FY27)": "The period from April 1, 2026, to March 31, 2027",
        "Week ID": {
            "description": "A six-digit identifier in the 'yyyyww' format (e.g., '202505' for the 5th week of 2025)",
            "Rule for Year Assignment": [
                "If the current date is between April 1st and December 31st, use the current year + 1",
                "If the current date is between January 1st and March 31st, use the current year"
            ],
            "SQL": "SELECT week_id FROM chatbi_dim_calendar WHERE date_code = CURRENT_DATE"
        }
    },
    "Store": {
        "Country": {
            "China/CN/Mainland": "Refers to Mainland China. The database value is country = 'mainland'",
            "HK": "Refers to Hong Kong. The database value is country = 'Hongkong'"
        },
        "Region": "A geographic classification for stores. Common values include APAC (Asia-Pacific), West, East, North, and South",
        "Channel": {
            "EC": "E-commerce",
            "FP": "Distributor (Franchise Partner)",
            "O&O": "Retail stores (Owned & Operated). Note: Both 'Retail' and 'O&O' refer to this channel. Always use channel = 'O&O' in queries"
        },
        "Store Type": {
            "BH": "Direct-operated (Brand House) store",
            "FH": "Factory store"
        },
        "Platform": "(For EC channel) The name of the e-commerce store (e.g., TMALL, JD)",
        "Store Name": "The specific name of a store (e.g., EC-TMALL, VIP STORE 2, UA Korea, Tiktok Store)",
        "Store Code": "A unique identifier for a store, typically structured as UABH_CHN_1234, where CHN is the country code and 1234 is a unique store number",
        "Comp Flag": "Indicates a comparable store that has been open for a full 12 months. These stores are flagged as comp_flag = 'Y' in the database",
        "Customer Name": {
            "description": "The name of the dealer or distributor that operates the store",
            "O&O": "Uniformly 'Retail' for O&O channel stores",
            "FP": "Name of the external partner (e.g., BEIJING JSBR, YYY-HN)"
        }
    },
    "Product": {
        "Division": "The high-level product category. Database values: APP (Apparel), ACC (Accessories), FTW (Footwear)",
        "Gender": "The target gender for the product (e.g., MENS, WOMENS, BOYS, GIRLS, Unisex)",
        "End Use": "The intended sport or activity for the product (e.g., TRAINING, RUNNING, BASEBALL, GOLF, Outdoor)",
        "Silhouette": "The form or shape of the product (e.g., BOTTOMS, ONE PIECES, SANDALS, Gloves)",
        "Fit Type": "The cut or fit of the product (e.g., LOOSE, REGULAR, FITTED, ONE SIZE)",
        "MFO": "A product line attribute (e.g., Inline, MFO, Promo)",
        "Key Stories/Category of Merchandise": "A marketing or thematic attribute for the product (e.g., Curry, HOVR, Armour Print, Women's Bra & Fitted Bottoms, Fat Tire, Slipspeed)",
        "Season Code": {
            "description": "This field in the product/sales tables always refers to the Product Season (the season the item was designed for), not the sales season",
            "SSYY": "Denotes Spring/Summer for the year 'YY'. Product season for items designed for Jan-Jun",
            "FWYY": "Denotes Fall/Winter for the year 'YY'. Product season for items designed for Jul-Dec",
            "In-Season vs. Off-Season": [
                "An item is 'in-season' if its Product Season (season_code) matches the Sales Season",
                "It is 'off-season' if they differ"
            ]
        }
    },
    "Sales": {
        "Sales": "Net Sales Amount. Calculated as total sales minus canceled and returned amounts. This is the amt field in the sales table",
        "Demand Sales": "Represents total sales demand. Calculated as Net Sales plus the value of returned goods: amt + amt_return",
        "SOB": "The proportion of total business, which can be based on either sales amount or sales quantity",
        "Ach": "The achievement rate against a sales target. Formula: (Actual Sales / Target Sales)",
        "Discount": "The effective discount rate given. Formula: ((Original Price - Actual Sales Amount) / Original Price)"
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

# 4. FAISS索引构建
class FaissIndex:
    def __init__(self, index_path: str | None = None):
        self.index_path = index_path
        self.index = None

        # 尝试加载已存在索引
        if self.index_path and os.path.exists(self.index_path):
            self.index = faiss.read_index(self.index_path)

    def add_embeddings(self, embeddings: np.ndarray):
        # 按需创建索引，自动推断维度
        if self.index is None:
            if embeddings is None or len(embeddings.shape) != 2:
                raise ValueError("Embeddings must be 2D array to initialize index")
            self.index = faiss.IndexFlatL2(embeddings.shape[1])
        self.index.add(embeddings)

    def search(self, query_embedding: np.ndarray, k=3) -> tuple:
        if self.index is None:
            raise RuntimeError("FAISS index is not initialized. Build or load the index first.")
        distances, indices = self.index.search(query_embedding, k)
        return distances, indices

    def save(self):
        if self.index is None:
            return
        if not self.index_path:
            return
        # 确保目录存在
        Path(self.index_path).parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, self.index_path)

# 6. 构建完整系统
class KnowledgeRetriever:
    def __init__(self, index_path: str | None = None, chunks_path: str | None = None):
        # 持久化文件路径
        default_dir = Path(__file__).parent
        self.index_path = index_path or str(default_dir / "faiss_index.bin")
        self.chunks_path = chunks_path or str(default_dir / "knowledge_chunks.json")

        self.faiss_index = FaissIndex(self.index_path)
        self.knowledge_chunks: List[Dict] = []
        self.model = ChatModel()

        # 如有持久化数据则加载
        if os.path.exists(self.chunks_path):
            try:
                with open(self.chunks_path, "r", encoding="utf-8") as f:
                    self.knowledge_chunks = json.load(f)
            except Exception:
                self.knowledge_chunks = []
        
    def build_index(self, knowledge_base: Dict, force_rebuild: bool = False):
        # 如果已有索引和chunks并且不强制重建，则跳过
        has_index = self.faiss_index.index is not None
        has_chunks = len(self.knowledge_chunks) > 0
        if has_index and has_chunks and not force_rebuild:
            return

        # 预处理知识库
        self.knowledge_chunks = preprocess_knowledge(knowledge_base)
        # 保存chunks以便下次直接加载
        Path(self.chunks_path).parent.mkdir(parents=True, exist_ok=True)
        with open(self.chunks_path, "w", encoding="utf-8") as f:
            json.dump(self.knowledge_chunks, f, ensure_ascii=False)

        texts = [chunk["text"] for chunk in self.knowledge_chunks]

        all_vecs = []
        batch_size = 10
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            emb_json = self.model.my_embedding(batch)
            emb_obj = json.loads(emb_json)
            vecs = [item["embedding"] for item in emb_obj["data"]]
            all_vecs.extend(vecs)

        embeddings = np.array(all_vecs, dtype="float32")
        self.faiss_index.add_embeddings(embeddings)
        # 持久化索引
        self.faiss_index.save()
    
    def retrieve(self, queries: List[str], k=3) -> List[List[Dict]]:
        """
        为每个query独立召回top k结果
        Args:
            queries: 多个查询字符串的列表
            k: 每个query返回的结果数量
        Returns:
            List[List[Dict]]: 每个query对应的top k结果列表
        """
        if not queries:
            return []

        # 1. 生成所有query的embedding
        try:
            # 假设my_embedding直接返回numpy数组
            emb_json = self.model.my_embedding(queries)  # shape: (num_queries, embedding_dim)
            emb_obj = json.loads(emb_json)
            query_embeddings = [item["embedding"] for item in emb_obj["data"]]
            query_embeddings = np.array(query_embeddings, dtype="float32")
            if not isinstance(query_embeddings, np.ndarray):
                raise ValueError("Embeddings must be numpy array")
        except Exception as e:
            print(f"Embedding generation failed: {str(e)}")
            return [[] for _ in queries]

        # 2. FAISS批量搜索
        distances, indices = self.faiss_index.search(query_embeddings.astype('float32'), k)  # shapes: (num_queries, k)

        # 3. 为每个query组装结果
        all_results = []
        for query_idx in range(len(queries)):
            query_results = []
            for rank_idx in range(k):
                chunk_idx = indices[query_idx, rank_idx]
                if chunk_idx >= 0:  # 有效索引
                    result = self.knowledge_chunks[chunk_idx].copy()  # 避免修改原始数据
                    result.update({
                        "score": float(1 - distances[query_idx, rank_idx]),
                        "keyword": queries[query_idx],  # 记录来源query
                        "rank": rank_idx + 1
                    })
                    query_results.append(result)
            all_results.append(query_results)

        return all_results

# 7. 使用示例与全局复用（单例）
_GLOBAL_RETRIEVER = None

def get_retriever() -> KnowledgeRetriever:
    global _GLOBAL_RETRIEVER
    if _GLOBAL_RETRIEVER is None:
        _GLOBAL_RETRIEVER = KnowledgeRetriever()
        # 首次初始化时尝试构建或加载
        _GLOBAL_RETRIEVER.build_index(knowledge_base, force_rebuild=False)
    return _GLOBAL_RETRIEVER


if __name__ == "__main__":
    retriever = get_retriever()
    query = ['MTD', 'sales', 'achievement', 'China', 'FP']
    results = retriever.retrieve(query, k=1)
    print(results)
  