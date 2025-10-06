import sys
import os
import ast
from unittest import result
import psycopg2 ##导入
from psycopg2 import OperationalError
import json
import logging
import pandas as pd
import numpy as np
from decimal import Decimal
from datetime import datetime, date, time
import math

# 配置logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO) # 可以根据需要设置为DEBUG/INFO/WARNING/ERROR

# 创建控制台处理器并设置格式
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

# 避免重复添加handler
if not logger.hasHandlers():
    logger.addHandler(console_handler)

# 添加backend目录到Python路径
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from tools.my_model import ChatModel
from tools.prompt import query_write_prompt, hightlight_extract, keywords_extract_prompt, text2sql_prompt, sql_parse_prompt, get_chart_prompt, rewrite_sql_prompt


import psycopg2
from psycopg2 import OperationalError
import pandas as pd
import logging
import json
from decimal import Decimal
import numpy as np
from datetime import date, datetime

def _to_jsonable(obj):
    """
    将 PostgreSQL 返回的各种类型转换为 JSON 可序列化的类型
    """
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, (date, datetime)):
        return obj.isoformat()
    elif isinstance(obj, float):
        # 处理特殊浮点值
        if np.isinf(obj):
            return str(obj)  # 或者 return None
        elif np.isnan(obj):
            return None
        return obj
    elif isinstance(obj, (list, tuple)):
        return [_to_jsonable(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: _to_jsonable(v) for k, v in obj.items()}
    elif obj is None:
        return None
    else:
        return str(obj)

def query_write(query):
    chat_model = ChatModel()
    prompt = query_write_prompt(query)
    response = chat_model.chat_with_system(
            system_prompt="You are a helpful assistant.",
            user_message=prompt
        )
    return response

def query_hightlight(query):
    chat_model = ChatModel()
    prompt = hightlight_extract(query)
    response = chat_model.chat_with_system(
        system_prompt="You are a helpful assistant.",
        user_message=prompt
    )
    # print(type(response))
    response = ast.literal_eval(response)
    if not isinstance(response, list):
        response = [str(response)]
    return response

def keyword_extract(query):
    chat_model = ChatModel()
    prompt = keywords_extract_prompt(query)
    response = chat_model.chat_with_system(
        system_prompt="You are a helpful assistant.",
        user_message=prompt
    )
    response = ast.literal_eval(response)
    if not isinstance(response, list):
        response = [str(response)]
    return response

def convert_value(value):
    """转换单个值为 JSON 兼容格式"""
    if value is None:
        return None
    
    try:
        # 先尝试转换为float，处理Decimal和数字字符串
        float_val = float(value)
        
        # 检查特殊浮点值
        if np.isinf(float_val):
            return None
        if np.isnan(float_val):
            return None
        
        # 如果是整数，返回整数类型
        if float_val.is_integer():
            return int(float_val)
        return float_val
    except (TypeError, ValueError):
        # 如果不是数字类型，处理其他情况
        if isinstance(value, (date, datetime)):
            return value.isoformat()
        return str(value)

# def excute_sql(query):
#     """
#     执行sql代码并返回可转换为DataFrame的结果
#     """
#     try:
#         conn = psycopg2.connect(database="postgres", user="postgres", 
#                                password="123456", host="127.0.0.1", port="5432")
#         cursor = conn.cursor()
#         cursor.execute(query)

#         # 获取列名
#         column_names = [desc[0] for desc in cursor.description]

#         # 获取数据并转换
#         rows = cursor.fetchall()
#         processed_rows = [_to_jsonable(r) for r in rows]
        
#         logging.info(f"执行sql得到{len(processed_rows)}条数据")
        
#         # 直接创建DataFrame，避免中间JSON转换
#         df = pd.DataFrame(processed_rows, columns=column_names)
        
#         return df
    
#     except OperationalError as e:
#         print(f"连接数据库失败: {e}")
#         return None
#     except Exception as e:
#         if 'conn' in locals():
#             conn.rollback()
#         print(f"操作失败: {e}")
#         return None
#     finally:
#         if 'cursor' in locals():
#             cursor.close()
#         if 'conn' in locals():
#             conn.close()
#         print("数据库连接已关闭。")

def excute_sql(query):
    """
    执行 SQL 并返回列表格式的结果，第一行为列名，后续为数据行
    """
    try:
        conn = psycopg2.connect(database="mydb", user="postgres", password="123456", host="127.0.0.1", port="5432")
        cursor = conn.cursor()
        cursor.execute(query)

        # 获取列名
        column_names = [desc[0] for desc in cursor.description]
        
        # 获取数据并转换
        rows = cursor.fetchall()
        
        # 构建结果列表
        result = [column_names]  # 第一行是列名
        
        for row in rows:
            # 转换每一行的值为 JSON 兼容格式
            converted_row = [convert_value(value) for value in row]
            result.append(converted_row)
        
        return {"data": result}
    
    except Exception as e:
        print(f"操作失败: {e}")
        return {"error": str(e)}
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

def text2sql(query, knowledges, sql_examples):
    chat_model = ChatModel()
    prompt = text2sql_prompt(query, knowledges, sql_examples)
    response = chat_model.chat_with_system(
        system_prompt="You are a helpful assistant.",
        user_message=prompt
    )
    response = json_format(response)

    sql = response["sql"]
    logger.info(f"文本转成的sql为: {sql}")
    excute_result = excute_sql(sql)
    # if not isinstance(excute_result, dict):
    #     # 修复sql代码
    #     sql_prompt = rewrite_sql_prompt(sql, excute_result)
    #     sql = chat_model.chat_with_system(
    #         system_prompt="You are a helpful assistant.",
    #         user_message=sql_prompt
    #     )

    # # 统一将查询结果转换为 DataFrame: {"column": [...], "data": [...]} -> DataFrame
    # try:
    #     if isinstance(excute_result, dict) and 'column' in excute_result and 'data' in excute_result:
    #         df = pd.DataFrame(excute_result["data"], columns=excute_result["column"])  # 行/列对齐
    #     elif isinstance(excute_result, (list, tuple)):
    #         df = pd.DataFrame(excute_result)
    #     else:
    #         df = pd.DataFrame()
    # except Exception as e:
    #     logger.error(f"结果转换为DataFrame失败: {e}，返回原始结果。")
    #     df = excute_result

    # 记录行数（仅当为DataFrame时）
    try:
        num_rows = len(excute_result)
    except Exception:
        num_rows = 0
    logger.info(f"sql的执行得到 {num_rows} 条数据")

    # 执行sql代码，如果报错重新执行
    # pass
    response['excute_result'] = excute_result

    return excute_result

def json_format(response):
    # 去除markdown包裹
    raw = str(response).replace("```json", '').replace("```", "").strip()
    # 优先按JSON解析
    try:
        return json.loads(raw)
    except Exception as e_json:
        # 回退到 Python 字面量（处理单引号/None/True/False等）
        try:
            obj = ast.literal_eval(raw)
            return obj
        except Exception as e_ast:
            logger.error(f"JSON解析失败: {e_json}，返回原始字符串。response内容为: {response}")
            return response

def knowledges_embedding(texts):
    """
    对文本列表进行向量化，返回 shape: (n, d) 的 numpy 数组。
    """
    if not isinstance(texts, (list, tuple)):
        texts = [texts]
    texts = [str(t) for t in texts]
    model = ChatModel()
    resp_json = model.my_embedding(texts)
    resp_obj = json.loads(resp_json)
    embeddings = [item["embedding"] for item in resp_obj.get("data", [])]
    return np.array(embeddings, dtype='float32')

def cosine_similarity(a, b):
    """
    计算余弦相似度。
    - a: shape (n, d) 或 (d,)
    - b: shape (d,) 或 (n, d)
    返回:
      - 若 a 为 (n, d) 且 b 为 (d,): 返回 (n,) 相似度向量
      - 若二者均为 (n, d): 逐行计算，返回 (n,)
    """
    a_arr = np.array(a, dtype='float32')
    b_arr = np.array(b, dtype='float32')
    # 对齐形状
    if a_arr.ndim == 1 and b_arr.ndim == 2:
        a_arr = np.expand_dims(a_arr, axis=0)
    if b_arr.ndim == 1 and a_arr.ndim == 2:
        # 正常情况
        pass
    # 逐行
    if a_arr.ndim == 2 and b_arr.ndim == 2:
        if a_arr.shape != b_arr.shape:
            raise ValueError("a 和 b 的形状不匹配，无法逐行计算相似度")
        a_norm = a_arr / (np.linalg.norm(a_arr, axis=1, keepdims=True) + 1e-12)
        b_norm = b_arr / (np.linalg.norm(b_arr, axis=1, keepdims=True) + 1e-12)
        return np.sum(a_norm * b_norm, axis=1)
    # a: (n, d), b: (d,)
    if a_arr.ndim == 2 and b_arr.ndim == 1:
        a_norm = a_arr / (np.linalg.norm(a_arr, axis=1, keepdims=True) + 1e-12)
        b_norm = b_arr / (np.linalg.norm(b_arr) + 1e-12)
        return np.dot(a_norm, b_norm)
    # a: (d,), b: (d,)
    if a_arr.ndim == 1 and b_arr.ndim == 1:
        a_norm = a_arr / (np.linalg.norm(a_arr) + 1e-12)
        b_norm = b_arr / (np.linalg.norm(b_arr) + 1e-12)
        return float(np.dot(a_norm, b_norm))
    raise ValueError("不支持的输入形状")

def sql_parse(query, knowledges, sql):
    prompt = sql_parse_prompt(query, sql)
    # print(parsed_sql)
    chat_model = ChatModel()
    response = chat_model.chat_with_system(
        system_prompt="You are a helpful assistant.",
        user_message=prompt
    )
    # 正确处理json数据，去除多余的markdown标记后再解析
    response = json_format(response)
    
    # 向量化 knowledge 的 NL 文本
    kn_values = [str(kn.get('NL', '')) for kn in knowledges]
    kn_emds = knowledges_embedding(kn_values)  # shape: (n, d)

    # 运行每一个sql
    new_response = []
    edges = []
    k = 0
    for res in response:
        # 字典不进行遍历
        if isinstance(res, dict):
            res = [res]
        for r in res:
            try:
                sql = r['sql']
            except Exception as e:
                logging.error(f"sql 解析出错，错误信息：{e}, 返回信息为{r}")
            excute_result = excute_sql(sql)
            logging.info(f"执行step {k}得到：{excute_result}")
            # 统一结果为 DataFrame
            r['Table'] = excute_result
            
            # 可视化模式
            # 判断数据行数，超过15行则不进行可视化
            # try:
            #     row_count = len(r['Table']) if isinstance(r['Table'], pd.DataFrame) else len(excute_result.get('data', []))
            # except Exception:
            #     row_count = 0
            # if row_count > 15:
            #     r['vis_data'] = ""
            # else:
            #     vis_data = get_chart(query, r['Table'])
            #     vis_data = json_format(vis_data)
            #     r['vis_data'] = vis_data
            
            # 向量化 r['NL'] 与 kn_emds 计算相似度
            nl_text = str(r.get('NL', ''))
            nl_vec = knowledges_embedding([nl_text])  # shape: (1, d)
            nl_vec = nl_vec[0] if len(nl_vec.shape) == 2 else nl_vec
            sims = cosine_similarity(kn_emds, nl_vec)
            sims_index = np.where(sims > 0.3)[0]
            related_kn = [knowledges[i]['id'] for i in sims_index]
            # r['activate_edges'] = related_kn
            r['operation'] = {
                "type": r["type"],
                "condition": r["condition"],
                "activate_edges": related_kn
            }

            new_response.append(r)
            # 处理边的关系
            #  { "from": "step1", "to": "step2", "operation": { "type": "Filter", "condition": "province='四川省' AND year=2022" } },
            temp_edges = {
                "edge_id": f"edge_s_{k}",
                "from": r["father_id"],
                "to": r["id"],
            }
            edges.append(temp_edges)
            k += 1

    return new_response, edges

def get_chart(query, data):
    chat_model = ChatModel()
    prompt = get_chart_prompt(query, data)
    # 返回json
    response = chat_model.chat_with_system(
        system_prompt="You are a helpful assistant.",
        user_message=prompt
    )
    response = json_format(response)
    
    return response


if __name__ == '__main__':
    query = 'WTD / MTD / QTD / YTD sales vs Target?'

    # rewrite_query = query_write(query)
    # sql_examples = """
    #     **question sample**:
    #     -WTD / MTD / QTD / YTD sales vs Target?
    #     -what is the MTD sales achievement for China FP?
    #     -WTD / MTD / QTD / YTD sales vs F1 (target)? Means the target use the f1 target.

    #     **SQL query sample**:
    #         SELECT 
    #         'WTD' as period,
    #         SUM(amt_notax) as withouttax_amount,
    #         SUM(amt_notax_target) as target_amount,
    #             case when SUM(amt_notax_target) = 0 then 0 else SUM(amt_notax)/SUM(amt_notax_target)-1 END as achievement 
    #         FROM 
    #             dm_fact_sales_chatbi 
    #         WHERE 
    #             date_code Between {1st of this week} AND CURRENT_DATE - INTERVAL '1 day'
    #         UNION ALL 

    #         SELECT 
    #         'MTD'  as period,
    #         SUM(amt_notax) as withouttax_amount,
    #         SUM(amt_notax_target) as target_amount,
    #             case when SUM(amt_notax_target) = 0 then 0 else SUM(amt_notax)/SUM(amt_notax_target)-1 END as achievement 
    #         FROM 
    #             dm_fact_sales_chatbi 
    #         WHERE 
    #             date_code Between TO_CHAR(DATE_TRUNC('MONTH', CURRENT_DATE), 'YYYY-MM-DD') AND TO_CHAR(CURRENT_DATE - INTERVAL '1 day') 

    #         UNION ALL 

    #         SELECT 
    #         'QTD' as period,
    #         SUM(amt_notax) as withouttax_amount,
    #         SUM(amt_notax_target) as target_amount,
    #             case when SUM(amt_notax_target) = 0 then 0 else SUM(amt_notax)/SUM(amt_notax_target)-1 END as achievement  
    #         FROM 
    #             dm_fact_sales_chatbi 
    #         WHERE 
    #             date_code Between TO_CHAR(DATE_TRUNC(QUARTER', CURRENT_DATE), 'YYYY-MM-DD') AND TO_CHAR(CURRENT_DATE - INTERVAL '1 day') 
            
    #         UNION ALL 

    #         SELECT 
    #         'YTD' as period,
    #         SUM(amt_notax) as withouttax_amount,
    #         SUM(amt_notax_target) as target_amount,
    #             case when SUM(amt_notax_target) = 0 then 0 else SUM(amt_notax)/SUM(amt_notax_target)-1 END as achievement  
    #         FROM 
    #             dm_fact_sales_chatbi 
    #         WHERE 
    #             date_code Between TO_CHAR(DATE_TRUNC('YEAR', CURRENT_DATE), 'YYYY-MM-DD') AND TO_CHAR((CURRENT_DATE - INTERVAL '1 day' )
    #         ;
    # """
    sql =  """
        SELECT 
        'WTD' as period,
        SUM(amt_notax) as withouttax_amount,
        SUM(amt_notax_target) as target_amount,
        CASE WHEN SUM(amt_notax_target) = 0 THEN 0 ELSE SUM(amt_notax) / SUM(amt_notax_target) - 1 END as achievement 
        FROM 
            dm_fact_sales_chatbi 
        WHERE 
            date_code BETWEEN '2025-02-10' AND '2025-02-12'
        UNION ALL 
        SELECT 
            'MTD' as period,
            SUM(amt_notax) as withouttax_amount,
            SUM(amt_notax_target) as target_amount,
            CASE WHEN SUM(amt_notax_target) = 0 THEN 0 ELSE SUM(amt_notax) / SUM(amt_notax_target) - 1 END as achievement 
        FROM 
            dm_fact_sales_chatbi 
        WHERE 
            date_code BETWEEN '2025-02-01' AND '2025-02-12'
        UNION ALL 
        SELECT 
            'QTD' as period,
            SUM(amt_notax) as withouttax_amount,
            SUM(amt_notax_target) as target_amount,
            CASE WHEN SUM(amt_notax_target) = 0 THEN 0 ELSE SUM(amt_notax) / SUM(amt_notax_target) - 1 END as achievement 
        FROM 
            dm_fact_sales_chatbi 
        WHERE 
            date_code BETWEEN '2025-01-01' AND '2025-02-12'
        UNION ALL 
        SELECT 
            'YTD' as period,
            SUM(amt_notax) as withouttax_amount,
            SUM(amt_notax_target) as target_amount,
            CASE WHEN SUM(amt_notax_target) = 0 THEN 0 ELSE SUM(amt_notax) / SUM(amt_notax_target) - 1 END as achievement 
        FROM 
            dm_fact_sales_chatbi 
        WHERE 
            date_code BETWEEN '2025-01-01' AND '2025-02-12';
    """

    knowledges = [
        {'id': 'k22', 
        'type': 'Keyword', 
        'score': -0.1143578290939331, 
        'keyword': 'Customer Name', 
        'NL': {'description': 'The name of the dealer or distributor that operates the store', 
        'O&O': "Uniformly 'Retail' for O&O channel stores", 
        'FP': 'Name of the external partner (e.g., BEIJING JSBR, YYY-HN)'}, 
        'Table': {}, 
        'activate_edges': ['edge1', 'edge_k_22']}, 
        {'id': 'k16', 'type': 'Keyword', 'score': -0.17913031578063965, 'keyword': 'Channel', 'NL': {'EC': 'E-commerce', 'FP': 'Distributor (Franchise Partner)', 'O&O': "Retail stores (Owned & Operated). Note: Both 'Retail' and 'O&O' refer to this channel. Always use channel = 'O&O' in queries"}, 'Table': {}, 'activate_edges': ['edge1', 'edge_k_16']}, {'id': 'k3', 'type': 'Keyword', 'score': -0.19209349155426025, 'keyword': 'Month-to-Date (MTD)', 'NL': 'The date range from the first day of the current month to yesterday', 'Table': {}, 'activate_edges': ['edge1', 'edge_k_3']}, {'id': 'k28', 'type': 'Keyword', 'score': -0.21909403800964355, 'keyword': 'MFO', 'NL': 'A product line attribute (e.g., Inline, MFO, Promo)', 'Table': {}, 'activate_edges': ['edge1', 'edge_k_28']}, {'id': 'k32', 'type': 'Keyword', 'score': -0.2441767454147339, 'keyword': 'Demand Sales', 'NL': 'Represents total sales demand. Calculated as Net Sales plus the value of returned goods: amt + amt_return', 'Table': {}, 'activate_edges': ['edge1', 'edge_k_32']}]
    response, edges = sql_parse(query, knowledges, sql)
    print(edges)