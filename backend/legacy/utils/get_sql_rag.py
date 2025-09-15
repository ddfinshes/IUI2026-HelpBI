from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import json
"""
{
    "ID1": {
        "description": "Query the achievement rate of sales within a certain period of time. The formula for the sales achievement rate is: sales amount / target sales amount - 1, displayed as a percentage with two decimal places.",
        "samples": [
            "WTD / MTD / QTD / YTD sales vs Target?",
            "What is the MTD sales achievement for China FP?",
            "WTD / MTD / QTD / YTD sales vs F1 (target)?"
        ]
    },
    "ID2": {
        "description": "Query the total sales volume for a specific region.",
        "samples": [
            "What is the total sales volume in Europe?",
            "Sales volume for Asia this quarter?",
            "YTD sales volume in North America?"
        ]
    }
    # 可扩展到 ID52
}
"""

def getSQLRAG(user_query):
    user_query = user_query #"What is the sales achievement rate for this month?

    category_texts = []
    with open('./knowledge-base/sql_sample_kb2.txt', encoding='utf-8') as file:
        content = file.read()
        category_texts = content.split('###')
    
    category_ids = []
    for ct in category_texts:
        category_ids.append(ct.strip().split(' ')[0])
    # for cat_id in category_ids:
    #     data = categories[cat_id]
    #     full_text = f"### {cat_id}  **Description**: {data['description']}  **Question Sample**: {' '.join(data['samples'])}"
    #     category_texts.append(full_text)

    # 向量化
    vectorizer = TfidfVectorizer(stop_words='english')  # 去除停用词
    category_vectors = vectorizer.fit_transform(category_texts)
    query_vector = vectorizer.transform([user_query])

    # 计算余弦相似度
    similarities = cosine_similarity(query_vector, category_vectors).flatten()

    # 排序并选择前 4 个类别
    sorted_indices = np.argsort(similarities)[::-1]  # 降序排序
    top_indices = [i for i in sorted_indices if similarities[i] > 0.3][:4]  # 过滤大于0.3的前4个
    top_categories = [(category_ids[i], similarities[i], category_texts[i]) for i in top_indices]
    print(similarities)

    # 构造输出结果
    result = {
        "Align Data": [
            {
                "ID": cat_id,
                "Content": content,
                'Similarity': similarity
            }
            for cat_id, similarity, content in top_categories
        ]
    }


    print(json.dumps(result, indent=4, ensure_ascii=False))
    return result

# user_query = "What is the sales achievement rate for this month?"
# getSQLRAG(user_query)