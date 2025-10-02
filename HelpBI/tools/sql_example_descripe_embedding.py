from pydoc import describe
from my_model import ChatModel
import json
import numpy as np

embedding_model = ChatModel()
with open('../knowledge-base/sql_sample_kb3_sections.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

describe_list = []
for ex in data:
    describe_list.append(ex['description'])

# Batch to comply with API limit (<=10 per request)
all_vecs = []
batch_size = 10
for i in range(0, len(describe_list), batch_size):
    batch = describe_list[i:i+batch_size]
    resp_json = embedding_model.my_embedding(batch)
    resp_obj = json.loads(resp_json)
    vecs = [item["embedding"] for item in resp_obj["data"]]
    all_vecs.extend(vecs)

embeddings = np.array(all_vecs, dtype='float32')
with open('../knowledge-base/knownledge_embeddings.json', 'w', encoding='utf-8') as f_emb:
    json.dump(all_vecs, f_emb, ensure_ascii=False)
print(f"Embeddings shape: {embeddings.shape}")
print(f"First vector dim: {embeddings.shape[1] if embeddings.size else 0}")
