from fastapi import FastAPI, Body, HTTPException
from fastapi.middleware.cors import CORSMiddleware
# from LightRAG.examples.lightrag_openai_compatible_demo import query
# lightrag have error for import 
# from lightrag_deepseek import my_lightrag
import uvicorn  
from typing import Dict, Any
from pydantic import BaseModel, Field
import re
import logging
from db.connect import excute_sql
# from utils.getVisTag import get_vis_tag
from decimal import Decimal
from fastapi import Body
# from sentence_transformers import SentenceTransformer, util
# from db.connect import excute_sql
# from utils.get_sql2json import sql2json
import json
import LightRAG.examples.lightrag_openai_compatible_demo as rag
from utils.get_NLExplain import ExplainAgent
from utils.get_user_sql import SQLExtractAgent
from utils.get_changeNLExSQL import ModifyAgent
from utils.get_Chart import VisAgent
from utils.get_stepNLSQLAgent import StepNLAgent
from utils.analysis_relation import analyze_relation
# from utils.sql_rag import SQLRAGAgent
from utils.get_sql_rag import getSQLRAG
from utils.kb2sql import process_file_to_chunks, get_chunks
from utils.get_LLM4SQL import SQLCodeAgent
from openai import OpenAI
import csv
from io import StringIO

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

# 存储对话历史
conversation_history = []  # 列表存储历史查询
# model = SentenceTransformer('all-MiniLM-L6-v2')  # 加载预训练模型计算相似度
user_query = ""
sql_code = ""
excute_sql_output = {}

def get_extracted_sql(text):
    # 匹配获取sqlcode
    sql_code = re.search(r'```sql\n(.*?)\n```', str(text), re.DOTALL)
    if sql_code:
        extracted_sql = sql_code.group(1)
        print("提取的SQL代码:")
        print(extracted_sql)
    else:
        print("未找到SQL代码块")
        return ''
    return extracted_sql

def getVisData(user_query, excute_sql_output):
    chart_input = {
            "question": user_query,
            "data": str(excute_sql_output)
        }

    vis = VisAgent()
    vis.run(str(chart_input))
    report = vis.getLeastAnalysisReport()
    return report

def getStepNLSQL(sql_code, sql_json):
    user_input = {
        'sql_code': sql_code,
        'sql_json': sql_json
    }
    sna = StepNLAgent()
    sna.run(user_input)
    report = sna.getLeastAnalysisReport()
    print('----------------SQL Step NL---------------------', report)
    return report

def get_anlyaiz_relation(understanding, list_of_lists):
    pair_relevance = analyze_relation(understanding, list_of_lists)


    print('------------pair_relevance------------',pair_relevance)

    # Highlight words
    sql_highlight_words = []
    sql_highlight_knowledges = []
    sql_lines = []
    bus_highlight_words = []
    bus_highlight_knowledges = []
    bus_lines = []
    
    i = 0
    for word in pair_relevance[0]:
        if word != 'none':
            sql_highlight_words.append(word.split('\n')[0].strip())
            sql_highlight_knowledges.append(word.split('\n')[1].strip())
            sql_lines.append(i + 1)
        i += 1

    i = 0
    for word in pair_relevance[1]:
        if word != 'none':
            bus_highlight_words.append(word.split('\n')[0].strip())
            bus_highlight_knowledges.append(word.split('\n')[1].strip())
            bus_lines.append(i + 1)
        i += 1
    # if pair_relevance != 'None':
    #     pair_relevance = pair_relevance.strip('```json\n').strip('```')
    #     pair_relevance = json.loads(pair_relevance)
    #     pairs = pair_relevance['pair']
    #     for p in pairs:
    #         highlight_words.append(p['mu'])
    #         highlight_knowledges.append(p['kb'])
    #         liners.append(p['index']+1)

    # 连线
    # for i in range(len(list_of_lists)):
    #     if pair_relevance[i][0] != 'none':
    #         liners.append(i + 1)
    highlight_words = {
        'sql_highlight_words': sql_highlight_words,
        'bus_highlight_words': bus_highlight_words,
    }
    highlight_knowledges = {
        'sql_highlight_knowledges': sql_highlight_knowledges,
        'bus_highlight_knowledges': bus_highlight_knowledges
    }
    liners = {
        'sql_lines': sql_lines,
        'bus_lines': bus_lines,
    }
    return pair_relevance, highlight_words, highlight_knowledges, liners

def get_SQLRAG(query):
    report = getSQLRAG(query)
    return report

def get_business_chunks():
    business_sentences = []
    with open('./knowledge-base/business_info.txt', encoding='utf-8') as file:
        content = file.read()
        business_sentences = content.split('***')
    return business_sentences

def get_list_of_lists(rag_response):
    sql_sentences = []
    list_of_lists = []
    align_data = rag_response['Align Data']
    for ad in align_data:
        sql_sentence = ad['Content']
        sql_sentences.append(sql_sentence)
    business_sentences = get_business_chunks()
    list_of_lists.append(sql_sentences)
    list_of_lists.append(business_sentences)
    return list_of_lists


def get_ragResponseForSQL(rag_response):
    align_data = rag_response['Align Data']
    ids = []
    for ad in align_data:
        idd = ad['ID']
        ids.append(idd)
    print(ids)
    sql_chunks = get_chunks(ids)
    print('-------------------sql_chunks--------------------------', sql_chunks)
    return sql_chunks


def get_llm4sql_response(user_info):
    sca = SQLCodeAgent()
    sca.run(user_info)
    llm4sql_report = sca.getLeastAnalysisReport()
    return llm4sql_report

@app.post("/api/sql2json")
async def get_sql2json(data: dict = Body(...)):
    # 检查是否存在 'data' 字段
    sql_code = data.get("data")
    if not sql_code:
        raise HTTPException(status_code=400, detail="Missing 'data' field")
    sql_code = sql_code['text']
    try:
        explain = ExplainAgent(model_name="o3-mini")
        explain.run(sql_code)  
        sql_json = explain.getLeastAnalysisReport()
        sql_stepnl = getStepNLSQL(sql_code, sql_json)
        report = {
            "sql_json": sql_json,
            "sql_stepnl": sql_stepnl
        }
        return report
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

    return {"response": "error"}


@app.post("/api/relatsql")
async def get_relatsql(sql_query: Dict[str, Any], query_out: Dict[str, Any], click_info: Dict[str, Any]): #
    print("sql_query: ",sql_query['text'])
    print("query_out: ",query_out)
    print("click_info: ",click_info)
    sql_query = sql_query['text']
    extractagent = SQLExtractAgent()
    extractagent.run(sql_query, query_out, click_info)
    sql_code = extractagent.getLeastAnalysisReport()
    print('---------------------sql_code------------------\n', sql_code)
    # to json
    try:
        explain = ExplainAgent(model_name="o3-mini")
        explain.run(sql_code)  # 无需 str()，因为 request.sql 已保证是字符串
        sql_json = explain.getLeastAnalysisReport()
        print('------------------sub sql to json----------------\n', sql_json)
        sql_stepnl = getStepNLSQL(sql_code, sql_json)
        print('------------------sql to stepnl----------------\n', sql_json)
        report = {
            "sql_json": sql_json,
            "sql_stepnl": sql_stepnl
        }
        return report
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    return {"response": "error"}

@app.post('/api/modify')
def modify_sql(data: Dict[str, Any]):
    ma = ModifyAgent()
    ma.run(data)
    modify_sql = ma.getLeastAnalysisReport()
    explain = ExplainAgent(model_name="o3-mini")
    explain.run(modify_sql)  
    sql_json = explain.getLeastAnalysisReport()
    return sql_json


@app.post("/api/query")
async def query_handler(request: Dict[str, Any]):
    try:
        # 1. 参数提取与验证
        user_query = request['query'][0]
        history = request['query'][1]
        conv_his = ''
        print(history)
        for conv in history:
            conv_his += f'[role: user, content: {conv["query"]}]\n'
            conv_his += f'role: assistant, content: {conv["sql_code"]}'
        revised_knowledge = request['query'][2]
        revised_understanding = request['query'][3]
        if not revised_knowledge:
            revised_knowledge = f'There are some mistakes in the knowledge, you should use the correct version that "{revised_knowledge}"'
        if not revised_understanding:
            revised_understanding = f'And during your thinking process, you need to follow this : {revised_understanding}'
        print("=====================user query=============================", user_query)
        
        if not user_query:
            raise HTTPException(status_code=400, detail="Missing query parameter")
        
        # 2. 知识库检索+生成sql代码
        print("==========================my_lightrag========================================")
        # rag_response, context = await rag.query(user_query)
        rag_response = get_SQLRAG(user_query)
        print('----------------rag_response----------------', rag_response)
        
        # Extract knowledge base
        # csv_file = StringIO(context.strip('"id", "content"\n'))

        # csv_reader = csv.reader(csv_file)

        # list_of_lists = [row[1].split("**SQL query sample**:") for row in csv_reader]
        # list_of_lists = [[row[1], ''] for row in csv_reader]
        list_of_lists = get_list_of_lists(rag_response)
        print('-------------------list_of_lists---------------------', list_of_lists)
        # understanding = rag_response.split('\n')[0]
        # 获取rag_response with sql
        sql_chunks = get_ragResponseForSQL(rag_response)
        business_chunks = get_business_chunks()
        user_info = {
            'user_question': user_query,
            'business_chunks': business_chunks,
            'sql_chunks': sql_chunks,
            'db_schema': "",
            "history": conv_his,
            "revised_knowledge": revised_knowledge,
            "revised_understanding": revised_understanding,
        }
        llm4sql_report = get_llm4sql_response(user_info)

        # LLM4SQL
        # understanding = rag_response.split('SQL Code:')[0]
        # sql_code = get_extracted_sql(rag_response)
        # explanation = rag_response.split("```")[-1]
        understanding = llm4sql_report['Give User Answer']['Model Understanding']
        sql_code = get_extracted_sql(llm4sql_report['Give User Answer']['SQL Code'])
        explanation = llm4sql_report['Give User Answer']['Explanation']
        print('-------------------understanding-----------------------------', understanding)
        print('-------------------sql_code-----------------------------', sql_code)
        print('-------------------explanation-----------------------------', explanation)



        # Analyze relation here
        understanding_pair_relevance, understanding_highlight_words, understanding_highlight_knowledges, understanding_liners = get_anlyaiz_relation(understanding, list_of_lists)
        query_pair_relevance, query_highlight_words, query_highlight_knowledges, query_liners = get_anlyaiz_relation(user_query, list_of_lists)
        
        pair_relevance = {
            'understanding_pair_relevance': understanding_pair_relevance,
            'query_pair_relevance': query_pair_relevance
        }
        highlight_words = {
            'understanding_highlight_words': understanding_highlight_words,
            'query_highlight_words': query_highlight_words
        }
        highlight_knowledges = {
            'understanding_highlight_knowledges': understanding_highlight_knowledges,
            'query_highlight_knowledges': query_highlight_knowledges
        }
        liners = {
            'understanding_liners':understanding_liners,
            'query_liners': query_liners
        }

        # liners = {
        #     'understanding_liners': {
        #         'sql_lines': [1,2,4],
        #         'bus_lines': [1,2,3],
        #     },
        #     'query_liners': {
        #         'sql_lines': [1,2,4],
        #         'bus_lines': [1,2,3],
        #     }
        # }

        # 3. 执行生成的sql 代码
        excute_sql_output = excute_sql(sql_code)
        print(excute_sql_output)

        # excute_sql_output = {'column': ['month_id', 'sales_amt', 'sales_notax', 'sales_notax_mom_per'], 'data': [(202502, Decimal('-5235'), Decimal('-4634'), Decimal('-1.00029011188026305147'))]}

        final_response = {
            "understanding": understanding,
            "explanation": explanation,
            "code": sql_code,
            "data": excute_sql_output,
            "context": list_of_lists,
            "pair_relevance": pair_relevance,
            "highlight_words": highlight_words,
            "highlight_knowledges": highlight_knowledges,
            "liners": liners,
            "list_of_lists": list_of_lists,
            "query": user_query,
        }
        
        # 添加当前查询到历史
        # conversation_history.append(user_query)

        # # 计算与历史查询的相似度
        # if len(conversation_history) > 1:
        #     # 生成当前查询的嵌入
        #     current_embedding = model.encode(user_query, convert_to_tensor=True)
        #     # 历史查询嵌入
        #     history_embeddings = model.encode(conversation_history[:-1], convert_to_tensor=True)
        #     # 计算余弦相似度
        #     similarities = util.cos_sim(current_embedding, history_embeddings)[0].tolist()
        # else:
        #     similarities = []


        # # 准备返回数据：历史查询和相似度
        # history_with_similarity = [
        #     {"query": q, "similarity": sim}
        #     for q, sim in zip(conversation_history[:-1], similarities)
        # ] if similarities else []

        # 按相似度降序排序并取 Top K（例如 K=3）
        # top_k = sorted(history_with_similarity, key=lambda x: x["similarity"], reverse=True)[:3]

        # 4. chart准备数据
        vis_data = getVisData(user_query, excute_sql_output)
        print('------------------vis_data-------------------', vis_data)

        # ===========================================================
        # vis_data = {
        #     "vis_tag": "bar-chart",
        #     "x": ["sales_amt", "sales_notax"],
        #     "y": [-5235, -4634],
        #     "title": "202502's sales for APAC EC",
        #     "x-legend": "class",
        #     "y-legend": "sales",
        #     "tooltip": "sales_notax_mom_per:-1.000290111880263"
        # }
        final_response['vis_data'] = vis_data

        print({"response": final_response, "top_k_similar": 3})

        return {"response": final_response, "top_k_similar": 3}
        # return final_response

    
    except Exception as e:
        # 异常处理与日志记录
        import traceback
        traceback.print_exc()  # 打印完整堆栈跟踪
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/executesql")
def execute_sql(sql_code):
    excute_sql_res = excute_sql(sql_code[0].replace('```sql\n', '').replace('\n```', ''))
    return {"response": excute_sql_res}

if __name__ == "__main__":
    uvicorn.run(
        app=app,  # 直接传递应用实例
        host="0.0.0.0",
        port=5000,
        reload=False  # 开发时启用热重载
    )