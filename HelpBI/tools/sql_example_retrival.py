# from HelpBI.HelpBI.tools.sql_example_descripe_embedding import data
import pandas as pd
import json
import numpy as np
import os

from tools.my_model import ChatModel
# from my_model import ChatModel

def load_knowledge_embeddings(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    # 假设json文件是一个list，每个元素是embedding向量
    return np.array(data, dtype='float32')

def load_knowlege(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return list(data)

def vectorize_query(query):
    model = ChatModel()
    # my_embedding 返回 JSON 字符串，需要解析并取出向量
    resp_json = model.my_embedding([str(query)])
    resp_obj = json.loads(resp_json)
    vec = resp_obj["data"][0]["embedding"]
    return np.array(vec, dtype='float32')

def cosine_similarity(a, b):
    # a: (n, d), b: (d,)
    a_norm = a / np.linalg.norm(a, axis=1, keepdims=True)
    b_norm = b / np.linalg.norm(b)
    return np.dot(a_norm, b_norm)

def few_shot_retriever(query, k=3):
    # 获取当前文件的目录，然后构建正确的路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)  # 回到HelpBI目录
    
    # 1. 读取knowledge-base/knownledge_embeddings.json得到knownledge_embeddings
    embeddings_path = os.path.join(project_root, 'knowledge-base', 'knownledge_embeddings.json')
    sections_path = os.path.join(project_root, 'knowledge-base', 'sql_sample_kb3_sections.json')
    
    knowledge_embeddings = load_knowledge_embeddings(embeddings_path)
    text_knowledge = load_knowlege(sections_path)
    # 2. 将接收到的query使用from my_model import ChatModel 向量化
    query_vec = vectorize_query(query)
    # 3. 计算相似度
    sims = cosine_similarity(knowledge_embeddings, query_vec)
    # 召回最相近3个数据的下标和相似度
    top_k_idx = np.argsort(sims)[-k:][::-1]
    top_k_sims = sims[top_k_idx]
    # 整理返回到数据
    results = []
    for idx, sim in zip(top_k_idx.tolist(), top_k_sims.tolist()):
        result = {
            'sql_examples': text_knowledge[idx]['sql_example'],
            'score': sim
        }
        results.append(result)

    # return list(zip(top_k_idx.tolist(), top_k_sims.tolist()))
    return results

# 示例用法
if __name__ == "__main__":
    query = "你的查询内容"
    results = few_shot_retriever(query, k=3)
    print("最相近的3个数据的下标和相似度：", results)