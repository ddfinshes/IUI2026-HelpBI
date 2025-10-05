import imp
from math import log
from unittest import result
from fastapi import FastAPI, Body, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import ast
import logging
import json
import os
import pandas as pd 

from utils.utils import query_write, query_hightlight, keyword_extract, text2sql, sql_parse, get_chart
from tools.knownledge_retrival import get_retriever
from tools.sql_example_retrival import few_shot_retriever

# 配置logger
logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)  # 可以根据需要设置为DEBUG/INFO/WARNING/ERROR
logging.basicConfig(level=logging.INFO)
# 创建控制台处理器并设置格式
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

# 避免重复添加handler
if not logger.hasHandlers():
    logger.addHandler(console_handler)

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


@app.post("/api/query")
async def text2bi(query: str):
    """
        对话界面返回: 解释、sql、table、vis_data
        {
        "sql":"SELECT SUM(sales_amount) AS mtd_sales_achievement\nFROM sales_data\nWHERE region = 'China FP' AND sales_date >= '2025-02-01' AND sales_date <= CURRENT_DATE;",
        "explanation":"This query calculates the Month-to-Date (MTD) sales achievement for the region 'China FP' in February 2025. It sums up the 'sales_amount' from the 'sales_data' table where the 'sales_date' falls between February 1, 2025, and the statically set current date of February 13, 2025. The result is labeled as 'mtd_sales_achievement'.",
        "excute_result":{},
        "vis_data":{"vis_tag":"bar-chart","x":[],"y":[],"title":"MTD Sales Achievement for China FP in February 2025","x-legend":"","y-legend":"","tooltip":""}
        }
    return:
        sql_response: 左边视图需要的内容
        response_dict: 右边视图需要的内容
    """
    response_dict = {}
    
    # 1. query改写
    rewrite_query = query_write(query)

    # 2. 检索知识库
    knownledge_retriever = get_retriever()
    knownledge_retriever_results = knownledge_retriever.retrieve(rewrite_query, k=5)

    knownledges = []
    logging.info(f"knownledge_retriever_results的类别：{type(knownledge_retriever_results)}")
    if isinstance(knownledge_retriever_results, dict):
        knownledge_retriever_results = [knownledge_retriever_results]
    for kn in knownledge_retriever_results:
        knownledges.append(kn['NL'])
    # 3. SQL 样例匹配
    # query和describe 以及样例做相似度匹配，返回id，然后将sql代码提出来
    sql_examples = few_shot_retriever(rewrite_query, k = 1)

    # 4. test2sql动态prompt
    # 执行sql和执行的结果
    logging.info(f"rewrite_query: {rewrite_query}")
    logging.info(f"knownledges: {knownledges}")
    logging.info(f"sql_examples: {sql_examples}")
    sql_response = text2sql(rewrite_query, knownledges, sql_examples)

    # 对话界面返回的内容
    # 将excute_result处理为可视化可支持模式
    vis_data = get_chart(rewrite_query, sql_response['excute_result'])

    sql_response['vis_data'] = vis_data

    # 左边需要传递给右边的内容
    response_dict['user_query'] = query
    response_dict['rewrite_query'] = rewrite_query
    response_dict['knownledge_retriever'] = knownledge_retriever_results
    response_dict['sql_examples'] = sql_examples
    response_dict['analyzed_query'] = sql_response['analyzed_query']
    response_dict['sql'] = sql_response['sql']

    total_info = {
        "left_view_info": sql_response,
        "left_to_right_info": response_dict
    }

    return total_info


# 获取到用户输入的query
@app.post("/api/helpbi")
async def helpbi(data: dict):
    logging.info(f"用户输入的query{data['user_query']}")
    # 1. query改写
    rewrite_query = data['rewrite_query']
    # 1.1 高亮提取
    highlight_keywords = query_hightlight(rewrite_query)
    logging.info(f"高亮词：{highlight_keywords}")
    # 使用assert判断highlight_keywords是否为list，不是则处理为列表

    # 2. 知识库检索
    knownledge_retriever_results = data['knownledge_retriever']
    logging.info(f"检索到{len(knownledge_retriever_results)}条知识")

    # 3. SQL 样例匹配
    sql_examples = data['sql_examples']
    logging.info(f"检索到{len(sql_examples)}条样例sql")

    # 4. 生成sql
    sql = data['sql']
    logging.info(f"生成的sql{sql}")

    # 5. 解析sql
    analyzed_query = data["analyzed_query"]
    highlight_analyzed_keywords = query_hightlight(analyzed_query)
    parsed_sql, sql_edges = sql_parse(analyzed_query, knownledge_retriever_results, sql)
    logging.info(f"将sql解析成{len(parsed_sql)}段内容")
    logging.info(f"在sql树部分具有{len(sql_edges)}条边")


    # 6. 整理nodes信息
    # activate_edges: 点击此节点高亮的边
    nodes = []
    node_input = {
        "id": "u1",
        "type": "Input",
        "NL": data['user_query'],
        "Table": {}, # input没有table
        "operation": {
            "type": "Input",
            "condition": [], # 高亮词
            "activate_edges": [] # 头节点点击无activate边
        }
    }
    nodes.append(node_input)
    node_rewrite = {
        "id": "r1",
        "type": "Rewrite",
        "NL": rewrite_query,
        "Table": {},
         "operation": {
            "type": "Rewrite",
            "condition": highlight_keywords, # 高亮词
            "activate_edges": [] # 头节点点击无activate边
        }
    }
    nodes.append(node_rewrite)
    # 关键词
    nodes.extend(knownledge_retriever_results)

    kn_edge_ids = [f"edge_k_{str(i)}" for i in range(len(knownledge_retriever_results))]
    node_analyzed_query = {
        "id": "a1",
        "type": "Analysis",
        "NL": data["analyzed_query"],
        "Table": {},
        "operation": { 
            "type": "AnalysisRewrite",
            "condition": highlight_analyzed_keywords, # analyzed_query应该也有高亮词
            "activate_edges": ["edge1"] + kn_edge_ids, # 激活起点和所有知识边
        },
    }
    nodes.append(node_analyzed_query)

    # sql nodes
    # 需要计算每个sql nodes和知识库节点的相似度义高亮对应的边
    nodes.extend(parsed_sql)

    # 7. 边的处理
    edges = []
    edge_input = {
        "edge_id": "edge1",
        "from": "u1",
        "to": "r1",
        
    }
    edges.append(edge_input)

    # r1连接所有的knowledge id
    # a1: analyzed应该是每个keywords的id都指向它
    r_edges = []
    kn_edges = []
    for i, kn in enumerate(knownledge_retriever_results):
        edge_rewrite = {
            "edge_id": f"edge_r_{i}",
            "from": "r1", 
            "to": f"k{i}", 
            },
        r_edges.append(edge_rewrite)
        edge_analyzed =  { 
            "edge_id": f"edge_k_{i}",
            "from": f"k{i}", 
            "to": "a1", 
            }
        kn_edges.append(edge_analyzed)
    edges.extend(r_edges)
    edges.extend(kn_edges)
    edges.extend(sql_edges)


    # response_dict = {
    #     "nodes": nodes,
    #     "edges": edges
    # }
    def make_serializable(obj):
        """递归地将对象转换为JSON可序列化的格式"""
        if isinstance(obj, pd.DataFrame):
            return obj.to_dict('records')
        elif isinstance(obj, pd.Series):
            return obj.tolist()
        elif isinstance(obj, list):
            return [make_serializable(item) for item in obj]
        elif isinstance(obj, dict):
            return {k: make_serializable(v) for k, v in obj.items()}
        elif hasattr(obj, '__dict__'):
            return make_serializable(obj.__dict__)
        else:
            return obj

    response_dict = {
        "nodes": make_serializable(nodes),
        "edges": make_serializable(edges)
    }
    logging.info(f"解析树总共具有{len(nodes)}个节点， {len(edges)}条边。")

    # === 新增: 保存为本地 JSON 文件 ===
    os.makedirs("logs", exist_ok=True)
    with open("logs/helpbi_response.json", "w", encoding="utf-8") as f:
        json.dump(response_dict, f, ensure_ascii=False, indent=2)

    


    return response_dict
