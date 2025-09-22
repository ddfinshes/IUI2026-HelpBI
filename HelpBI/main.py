from fastapi import FastAPI, Body, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import ast

from utils.utils import query_write, query_hightlight, keyword_extract
from tools.knownledge_retrival import get_retriever

# 初始化FastAPI应用
app = FastAPI(
    title="NL2BI Backend",
    description="NL2BI系统的转换接口",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制具体域名
    allow_credentials=True,
    allow_methods=["POST", "GET"],  # 根据实际需求调整
    allow_headers=["*"],
)

def format_knownledge_retriever_results(results):
    format_result = []
    for r in results:
        f_r = {}
        f_r['keyword'] = r['keyword']
        f_r['knownledge'] = r['text']
        f_r['score'] = r['score']
        format_result.append(f_r)
    return format_result

       

# 获取到用户输入的query
@app.post("/api/query")
async def query_handler(query: str):
    response_dict = {}
    response_dict['user_query'] = query
    # 1. query改写
    rewrite_query = query_write(query)
    # 1.1 高亮提取
    highlight_keywords = query_hightlight(rewrite_query)
    # 使用assert判断highlight_keywords是否为list，不是则处理为列表
    
    # 存入dict
    rewrite_query_dict = {
        "rewrited_query": rewrite_query,
        "hightlight_keywords": highlight_keywords
    }
    response_dict['rewrite_query'] = rewrite_query_dict

    # 2. 关键词抽取
    highlight_keywords = keyword_extract(rewrite_query)
    # 2.1 关键词以及关键词中的解释提取
    knownledge_retriever = get_retriever()
    # query = ['MTD', 'sales', 'achievement', 'China', 'FP']
    knownledge_retriever_results = knownledge_retriever.retrieve(highlight_keywords, k=1)[0]
    # print(results)
    # 处理results格式
    knownledge_retriever_results = format_knownledge_retriever_results(knownledge_retriever_results)
    response_dict['knowledge_retrive'] = knownledge_retriever_results

    

    
    return response_dict
