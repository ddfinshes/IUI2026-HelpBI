from re import S


def query_write_prompt(query):
    prompt = f"""
        You are a data analysis expert. Please refine the user's natural language query into a clearer, more analytical expression. Return only the revised statement as output, with no additional content.

        Note: Modify the statement based on today's date, which is February 10, 2025.

        【Input-Output Examples】:
        Input: "Show me last month's sales in Beijing"
        Output: "Query the sales amount and order quantity in Beijing from January 1, 2025 to January 31, 2025, grouped by product category."

        Input: "Compare user growth in East China this year vs last year"
        Output: "Compare the number of registered users in the East China region (including Shanghai, Jiangsu, Zhejiang, Anhui, Fujian, Jiangxi, Shandong) between January 1, 2025 to December 31, 2025 and January 1, 2024 to December 31, 2024, summarized monthly."

        Input: "Which product has the best sales?"
        Output: "Calculate the total sales volume for all products in the past year (January 1, 2025 to February 10, 2025), group by product name, and rank the top ten."

        Input: "WTD / MTD / QTD / YTD sales vs Target?"
        Output: "Calculate the actual sales and sales targets for WTD, MTD, QTD, and YTD in 2025."

        Now process the following input:
        Input: {query}
        Output:
        """
    return prompt

def hightlight_extract(writed_query):
    prompt = f"""
        Please act as a data analysis expert and process the query according to the following requirements:

        1.  Identify all key business metrics mentioned in the query (e.g., sales revenue, number of users).
        2.  Extract all time period expressions (e.g., annual, quarterly, monthly timeframes).
        3.  Identify all comparative dimensions (e.g., actual value vs. target value, year-over-year comparison).
        4.  Return the extracted key elements in an array format. Provide only the list, with no additional content.

        Examples:
        Input: "Calculate the actual sales and sales targets for WTD, MTD, QTD, and YTD in 2025"
        Output: ["2025", "WTD", "MTD", "QTD", "YTD", "actual sales", "sales target"]

        Input: "Analyze regional customer satisfaction scores for Q1 2024"
        Output: ["2024", "Q1", "region", "customer satisfaction score"]

        Input: "Compare website traffic for the first half of this year versus the same period last year"
        Output: ["last year", "this year", "first half", "website traffic"]

        Please process the following query:
        Input: {writed_query}
        Output:
    """
    return prompt

def keywords_extract_prompt(query):
    prompt = f"""
        Analyze the user's query and extract the keywords that should be used to query the knowledge base. The knowledge base includes keywords related to the following categories:

            • Date-related: This week, Last week, F-YTD, C-YTD, YTD, MTD, QTD, LWK, WTD, FY23, FY24, week id  

            • Store-related: country China, region APAC, Store Name, platform, Channel, EC, FP, O&O, Store type, BH, FH, Comp flag, customer_name, store code  

            • Commodity-related: key_stories, MFO, Division, Gender, End Use, Silhouette, Fit type, Catagory of merchandise, Season code, sales season, product season, SS, FW  

            • Sales-related: Sales, Demand Sales, SOB, Ach, Discount  

            Your task is to identify and return only those keywords present in the user's query that match any of the terms listed above. 

            Return the results as a Python list of strings, with no additional explanations or text.

            Examples:  
            Input: WoW growth% of sales / traffic / CR / AOV / ASP / UPT  
            Output: ["WoW", "sales", "traffic", "CR", "AOV", "ASP", "UPT"]  

            Input: SOB of APP / FTW / ACCS and how does it compare to last week?  
            Output: ["SOB", "APP", "FTW", "ACCS", "last week"]  

            Now process the following query:  
            {query}
        """
    return prompt

# """
#         #角色
#         你是一名资深的数据分析师，擅长将复杂的业务需求转化为精确的PostgreSQL查询。

#         #任务
#         根据用户提供的**业务知识**和**样例sql**，为**业务问题**，编写对应的SQL查询。

#         #工作流程
#         1.  **样例sql：** 理解表、字段之间的关系和数据类型。
#         2.  **理解业务知识和业务问题：** 解析用户的自然语言描述，确定查询目标、条件、排序和分组等。
#         3.  **编写SQL：** 生成符合ANSI SQL标准的、语法正确的查询语句。

#         #业务知识
#         {knowledges}

#         #样例sql
#         {sql_examples}

#         #业务问题
#         {query}

#         #约束条件
#             - 优先使用`JOIN`而不是子查询来关联多张表。
#             - 如果问题中涉及“最近”、“最新”，请使用`ORDER BY`和`LIMIT`。
#             - 如果问题中涉及“总数”、“平均值”，请使用合适的聚合函数（如`COUNT`, `AVG`）。
#             - 确保`WHERE`条件中的字符串值使用单引号。
#             - 除非用户明确要求，否则不要使用`SELECT *`。
#             - 由于数据库只包含2025年1月1日-2025年3月1日的数据，因此生成的sql代码请将current_date静态设置为2025年2月9日。

#         #输出格式
#         仅输出SQL语句，不要有任何额外的解释、注释或Markdown格式。

#         #开始
#         现在，请根据以下问题生成SQL：

#         **用户问题：** {query}
# """

def text2sql_prompt(query, knowledges, sql_examples):
    """
    "dm_dim_holiday_chatbi", "dm_fact_onhand_chatbi", "dm_fact_sales_chatbi","dm_fact_sales_sku_chatbi","dm_member_chatbi", "dm_member_sales_chatbi", "edw_dim_calendar", "edw_dim_channel", "edw_dim_store", "edw_dim_store_prod"
    """
    schema_info = """
        1. dm_fact_sales_chatbi:店铺的销售汇总表，按日期存储门店每日的销售汇总数据，以及门店每日的目标销售数据，同时包含上周同日/上月同日/上年同日的销售汇总数据。
            - date_code: String; format(YYYY-MM-DD).
            - week_id: String; format(YYYYWW); 是财年的周ID.
            - month_id: String; format(YYYYMM).
            - year_id: String; format(YYYY).
            - store_code: String; 店铺code.
            - store_name: String; 店铺名称.用店铺名称查询数据时，使用模糊查询方式：store_name like '%?%'.
            - customer_name: String; 店铺所属经销商名.
            - country: String; 店铺所在国家.
            - channel: String;店铺所属渠道:EC/FP/O&O.
            - sub_channel: String;店铺所属子渠道：EC/BH/FH/UA.com/others.
            - store_type: String; 店铺类型： BH/FH.
            - region: String; 店铺所在区域：north/south/east/west.
            - province: String; 店铺所在省份，拼音存储.
            - city: String; 店铺所在城市，拼音存储.
            - area: decimal; 店铺面积，零售实体店铺有店铺面积的数据.
            - cluster:String，店铺等级：AAA/A/B/C
            - comp_flag: String; Y/N；在计算COMP店铺的销售额或者指标时，需要限制comp_flag=Y。
            - qty_return: decimal; number of returned items.
            - amt_return: decimal; amount of returned items; [Amount field].
            - orig_price: decimal; 不考虑折扣的销售原价。 [Amount field].
            - amt: decimal; datecode当天的销售额，是销售净额; [Amount field].
            - lw_amt: decimal; 上周同日的销售额; [Amount field].
            - lm_amt: decimal; 上月同日的销售额; [Amount field].
            - lyd_amt: decimal; 上年同日的销售额; [Amount field].
            - amt_target: decimal; datecode当天的目标销售金额; [Amount field].
            - qty: decimal; datecode当天的销售数量.
            - lw_qty: decimal;上周同日的销售数量.
            - lm_qty: decimal;上月同日的销售数量.
            - lyd_qty: decimal;上年同日的销售数量.
            - qty_target:decimal;datecode当天的目标销售数量.
            - trans: decimal;datecode当天的交易笔数.
            - lw_trans: decimal;上周同日的交易笔数.
            - lm_trans: decimal;上月同日的交易笔数.
            - lyd_trans: decimal;上年同日的交易笔数.
            - trans_target:decimal;datecode当天的目标交易笔数.
            - traffic: decimal; datecode当天的客流traffic.
            - lw_traffic: decimal;上周同日的traffic.
            - lm_traffic: decimal;上月同日的traffic.
            - lyd_traffic: decimal;上年同日的traffic.
            - traffic_target:decimal;datecode当天的目标traffic.
            - amt_target_f0: decimal;F0 target amount; [Amount field].
            - amt_target_f1: decimal;F1 target amount; [Amount field].
            - amt_target_f2: decimal;F2 target amount; [Amount field].
            - amt_target_f3: decimal;F3 target amount; [Amount field].
            - amt_target_f4: decimal;F4 target amount; [Amount field].
        2. dm_fact_sales_sku_chatbi:店铺商品销售表，存储门店每日商品的销售数据。
            - date_code: String; format(YYYY-MM-DD).
            - week_id: String; format(YYYYWW); 是财年的周ID.
            - month_id: String; format(YYYYMM).
            - year_id: String; format(YYYY).
            - store_code: String; 店铺code.
            - store_name: String; 店铺名称.用店铺名称查询数据时，使用模糊查询方式：store_name like '%?%'.
            - customer_name: String; 店铺所属经销商名.
            - country: String; 店铺所在国家.
            - channel: String;店铺所属渠道:EC/FP/O&O.
            - sub_channel: String;店铺所属子渠道：EC/BH/FH/UA.com/others.
            - store_type: String; 店铺类型： BH/FH.
            - region: String; 店铺所在区域：north/south/east/west.
            - province: String; 店铺所在省份，拼音存储.
            - city: String; 店铺所在城市，拼音存储.
            - area: decimal; 店铺面积，零售实体店铺有店铺面积的数据.
            - cluster:String，店铺等级：AAA/A/B/C
            - division: Division attribute of the product; e.g., Apparel/Accessories/Footwear.
            - enduse: enduse of the product; e.g., Training/Golf/Running.
            - silhouette: silhouette of the product; e.g., Short Sleeve/Warmup Tops/Slides.
            - fit_type: fit type of the product; e.g., Loose/Regular/Fitted.
            - material: String; article of product; e.g., 1234567-123.
            - SKU: String; product sku.
            - product_name: String，商品名称，查询数据时，使用模糊查询方式。
            - key_stories: Key category, key items of the product.查询数据时，使用模糊查询方式。
            - product_line: String; e.g., inline/MFO.
            - msrp: decimal; product label price.
            - qty: decimal; number of sales items.
            - amt: decimal; sales amount; [Amount field].
            - season_code: String; season of the product; e.g., SS24/FW24/SS25.
        3. dm_fact_onhand_chatbi:门店库存表，存储零售门店每天的商品库存。一般只保存每周六的库存数据。
            - store_code: String; 店铺code.
            - store_name: String; 店铺名称.用店铺名称查询数据时，使用模糊查询方式：store_name like '%?%'.
            - customer_name: String; 店铺所属经销商名.
            - country: String; 店铺所在国家.
            - channel: String;店铺所属渠道:EC/FP/O&O.
            - store_type: String; 店铺类型： BH/FH.
            - region: String; 店铺所在区域：north/south/east/west.
            - province: String; 店铺所在省份，拼音存储.
            - city: String; 店铺所在城市，拼音存储.
            - area: decimal; 店铺面积，零售实体店铺有店铺面积的数据.
            - cluster:String，店铺等级：AAA/A/B/C
            - date_code: String; format(YYYY-MM-DD).
            - division: Division attribute of the product; e.g., Apparel/Accessories/Footwear.
            - enduse: enduse of the product; e.g., Training/Golf/Running.
            - silhouette: silhouette of the product; e.g., Short Sleeve/Warmup Tops/Slides.
            - fit_type: fit type of the product; e.g., Loose/Regular/Fitted.
            - material: String; article of product; e.g., 1234567-123.
            - product_name: String，商品名称，查询数据时，使用模糊查询方式。
            - key_stories: Key category, key items of the product.
            - product_line: String; e.g., inline/MFO.
            - stock: decimal; quantity of product inventory.
            - intransit: decimal; quantity of product in transit.
            - stock_amt: decimal; monetary value of product inventory; [Amount field].
            - intransit_amt: decimal; monetary value of product in transit; [Amount field].
        4. chatbi_dim_store:店铺主档表，存储公司所有店铺的信息。
            - country: String; 店铺所在国家.
            - channel: String;店铺所属渠道:EC/FP/O&O.
            - sub_channel: String;店铺所属子渠道：EC/BH/FH/UA.com/others.
            - customer_name: String; 店铺所属经销商名.
            - region: String; 店铺所在区域：north/south/east/west.
            - province: String; 店铺所在省份，拼音存储.
            - city: String; 店铺所在城市，拼音存储.
            - area: decimal; 店铺面积，零售实体店铺有店铺面积的数据.
            - store_type: String; 店铺类型： BH/FH.
            - store_code: String; 店铺code.
            - store_name: String; 店铺名称.用店铺名称查询数据时，使用模糊查询方式：store_name like '%?%'.
            - status: String; 店铺开关状态：open/closed.
            - open_date:date；店铺开店时间。
            - close_date:date；店铺关店时间。店铺关店时填入，开店状态时为null或者9999-12-31.
            - cluster:String，店铺等级：AAA/A/B/C
        5. dm_member_chatbi:会员用户表，存储会员的相关信息。
            - birthday: String; format(YYYY-MM-DD); member's birthday date.
            - country: String; 会员所属国家.
            - register_date_str: date; user's membership registration date.
            - member_code: String.会员号，是会员的唯一代码。
            - gender: String; 性别：Male/Female.
            - regist_channel:String.注册渠道,比如：2-UA_CN/3-TMALL/7-DOUYIN/9-Campaign/8-WeChat/6-FP/4-WMS/5-JD/1-Retail .
            - regist_sub_channel:String.注册子渠道，比如：FP_ULEE/MA_TMALL/Wechat.
        6. dm_member_sales_chatbi:会员交易信息表，存储会员交易信息。每条记录也有会员的基本信息，数据的粒度是按每笔交易存储的。
            - birthday: String; format(YYYY-MM-DD); member's birthday date.
            - register_date_str: date; user's membership registration date.
            - country: String; 所属国家.
            - member_code: String.会员号，是会员的唯一代码。
            - gender: String; 性别：Male/Female.
            - regist_channel:String.注册渠道,比如：2-UA_CN/3-TMALL/7-DOUYIN/9-Campaign/8-WeChat/6-FP/4-WMS/5-JD/1-Retail .
            - regist_sub_channel:String.注册子渠道，比如：FP_ULEE/MA_TMALL/Wechat.
            - transaction_date: date;交易日期.
            - amt_total:decimal;订单金额，并非实际交易产生的金额。
            - amt_real:decimal;实际支付金额，交易金额使用这个字段。
            - qty_total:decimal；交易商品的数量。
    """
    prompt = f"""
        #Role

        You are a senior data analyst skilled at translating complex business requirements into precise PostgreSQL queries.  

        #Task

        Based on the provided database schema information, business knowledge and example SQL, write the corresponding SQL query for the business problem.  

        #Workflow
        1. Example SQL: Understand the relationships between tables and fields, as well as data types.  
        2. Database Schema: Understand the information of each table and its columns in the database, determine which tables and columns are needed to answer the user’s query, and do not use any tables that do not exist.
        3. Understand business knowledge and problem: Parse the natural language description to determine query objectives, conditions, sorting, and grouping.  
        4. Write SQL: Generate a syntactically correct query compliant with ANSI SQL standards.  
        5. The Sample SQL may contain errors; therefore, the generated PostgreSQL must be checked. If any errors are found, please correct them to produce valid PostgreSQL code.

        # Database Schema Information

        {schema_info} 

        #Business Knowledge

        {knowledges}  

        #Sample SQL

        {sql_examples}  

        #Business Problem

        {query}  

        #Constraints

        • Prefer JOIN over subqueries for table associations.  

        • For queries involving "recent" or "latest," use ORDER BY and LIMIT.  

        • For queries involving "total count" or "average," use appropriate aggregate functions (e.g., COUNT, AVG).  

        • Ensure string values in WHERE conditions are enclosed in single quotes.  

        • Avoid SELECT * unless explicitly requested.  

        • Do not use any table or column elements that do not exist in the Example SQL or Database Schema.

        • Since the database only contains data from January 1, 2025, to March 1, 2025, statically set current_date to February 13, 2025 in the generated SQL.
            CURRENT_DATE = '2025-02-13'  
        
        • Ensure the output is correct and executable PostgreSQL statements.
        
        
    """
    prompt1 = """
        #Output Format

        Output the SQL and some easy understanding explanations, comments, or Markdown formatting, but do not contain information about sql example.  
        Output format is Json:
        ```json
        {
            "analyzed_query: "refine the user's query by combining it with the retrieved knowledge, outputting a clearer and more complete version",
            "explanation": "some information help understanding why output this sql",
            "sql": "correct and executable PostgreSQL statements",
        }
        ```

    """

    prompt2 = f"""
        #Start

        Now, generate the SQL for the following problem:  

        User Query: {query}
    """
    return prompt+prompt1 + prompt2


def sql_parse_prompt(query, sql):
    prompt = """
        # 角色定义
        你是一位资深PostgreSQL专家，专注于零售领域数据分析。你的任务是将SQL查询拆解为可执行的步骤，并以结构化JSON格式输出，便于后续树状可视化展示。

        # 任务要求
        1. 输入处理：
        - 接收包含query和sql两个部分的输入
        - query：描述SQL查询的业务目的
        - sql：需要分析的SQL代码

        2. 输出规范：
        - 返回一个列表，每个元素是字典格式的步骤描述
        - 每个步骤必须包含以下字段：
            * id：唯一标识符（格式：类型字母+数字, 如s1,t1等， 请不要以u, r, k, a作为类型字母）
            * father_id：上一步骤ID列表（若无则为空列表）
            * NL：自然语言解释（详细说明操作目的和逻辑）
            * sql：可独立执行的SQL片段
            * condition: 这一步操作的主要影响的列名
            * type：原子操作类型（严格按分类标准标注）

        3. 拆解原则：
        - 确保每个步骤的SQL都可独立执行
        - 遇到UNION/UNION ALL/JOIN等并行结构时：
            * 拆分为独立子查询链
            * 最后添加合并步骤，其father_id指向各子链的末端节点
        - 复杂表达式（如嵌套CASE WHEN）需分步拆解

        # 原子操作分类标准
        1. Filter：WHERE/DISTINCT等条件筛选
        2. Select：SELECT指定查询列
        3. Aggregate：SUM/AVG/COUNT等聚合计算
        4. GroupBy：GROUP BY/HAVING分组操作
        5. Sort/Limit：ORDER BY/LIMIT结果排序限制
        6. Join：JOIN/UNION等表连接操作
        7. Transform：CASE WHEN/算术运算等数据转换
        8. Window：窗口函数计算

        # 处理流程
        1. 语法分析：识别SQL中的关键操作节点
        2. 步骤拆分：将复合操作分解为原子操作
        3. 依赖构建：确定步骤间的父子关系
        4. 解释生成：为每个步骤编写业务和技术说明
        5. 结果验证：确保所有SQL片段可独立执行

        # 示例输出格式
        [
        {
            "id": "s1",
            "father_id": [],
            "NL": "解释文本...",
            "sql": "独立可执行的SQL",
            “condition”: ["col_name1", "col_name2", ...],
            "type": "操作类型"
        },
        ...
        ]

        #举例
            ## 输入：
            query：What's WTD / MTD  sales vs Target?
            sql：SELECT 'WTD' as period,SUM(amt_notax) as withouttax_amount, SUM(amt_notax_target) as target_amount, CASE WHEN SUM(amt_notax_target) = 0 THEN 0 ELSE SUM(amt_notax) / SUM(amt_notax_target) - 1 END as achievement FROM dm_fact_sales_chatbi WHERE date_code BETWEEN '2025-02-10' AND '2025-02-12' UNION ALL SELECT 'MTD' as period, SUM(amt_notax) as withouttax_amount, SUM(amt_notax_target) as target_amount, CASE WHEN SUM(amt_notax_target) = 0 THEN 0 ELSE SUM(amt_notax) / SUM(amt_notax_target) - 1 END as achievement FROM dm_fact_sales_chatbi WHERE date_code BETWEEN '2025-02-01' AND '2025-02-12';

            ## 输出：
            [
            [
            {
                "id": "s1",
                "father_id": [],
                "NL": "这是最基本的查询形式，从dm_fact_sales_chatbi表中选出2025年2月10日至12日的数据，显示每行的period标记为'WTD'（周至今），以及不含税金额和目标金额的原始值。",
                "sql": "SELECT 'WTD' as period, amt_notax, amt_notax_target FROM dm_fact_sales_chatbi WHERE date_code BETWEEN '2025-02-10' AND '2025-02-12'",
                "condition": ["period", "amt_notax", "amt_notax_target"],
                "type": "Select"
            },
            {
                "id": "s2",
                "father_id": ["s1"],
                "NL": "在基础查询上添加了SUM聚合函数，计算选定时间段内：\nwithouttax_amount：不含税金额总和;\ntarget_amount：目标金额总和",
                "sql": "SELECT 'WTD' as period, SUM(amt_notax) as withouttax_amount, SUM(amt_notax_target) as target_amount FROM dm_fact_sales_chatbi WHERE date_code BETWEEN '2025-02-10' AND '2025-02-12'",
                "condition": ["withouttax_amount", "amt_notax_target"],
                "type": "Aggregate"
            },
            {
                "id": "s3",
                "father_id": ["s2"],
                "NL": "在聚合基础上增加了除法计算，显示实际金额与目标金额的原始比率(withouttax_amount/target_amount)。使用CASE WHEN语句处理除零情况，当目标金额总和为零时返回0，避免运行时错误。",
                "sql": "SELECT 'WTD' as period, SUM(amt_notax) as withouttax_amount, SUM(amt_notax_target) as target_amount, CASE WHEN SUM(amt_notax_target) = 0 THEN 0 ELSE SUM(amt_notax) / SUM(amt_notax_target) END as safe_ratio FROM dm_fact_sales_chatbi WHERE date_code BETWEEN '2025-02-10' AND '2025-02-12'",
                "condition": ["safe_ratio"],
                "type": "Aggregate"
            },
            {
                "id": "s4",
                "father_id": ["s3"],
                "NL": "在安全比率计算基础上减去1，得到实际达成率（如1.1表示超额10%，0.9表示差10%未达标)。公式：withouttax_amount / target_amount - 1",
                "sql": "SELECT 'WTD' as period, SUM(amt_notax) as withouttax_amount, SUM(amt_notax_target) as target_amount, CASE WHEN SUM(amt_notax_target) = 0 THEN 0 ELSE SUM(amt_notax) / SUM(amt_notax_target) - 1 END as achievement FROM dm_fact_sales_chatbi WHERE date_code BETWEEN '2025-02-10' AND '2025-02-12'",
                "condition": ["achievement"],
                "type": "Aggregate"
            }
            ],
            [
            {
                "id": "t1",
                "father_id": [],
                "NL": "这是最基本的查询形式，从dm_fact_sales_chatbi表中选出2025年2月10日至12日的数据，显示每行的period标记为'WTD'（周至今），以及不含税金额和目标金额的原始值。",
                "sql": "SELECT 'MTD' as period, amt_notax, amt_notax_target FROM dm_fact_sales_chatbi WHERE date_code BETWEEN '2025-02-10' AND '2025-02-12'",
                "condition": ["period", "amt_notax", "amt_notax_target"],
                "type": "Select"
            },
            {
                "id": "t4",
                "father_id": ["t3"],
                "NL": "在安全比率计算基础上减去1，得到实际达成率（如1.1表示超额10%，0.9表示差10%未达标)。公式：withouttax_amount / target_amount - 1",
                "sql": "SELECT 'MTD' as period, SUM(amt_notax) as withouttax_amount, SUM(amt_notax_target) as target_amount, CASE WHEN SUM(amt_notax_target) = 0 THEN 0 ELSE SUM(amt_notax) / SUM(amt_notax_target) - 1 END as achievement FROM dm_fact_sales_chatbi WHERE date_code BETWEEN '2025-02-10' AND '2025-02-12'",
                "condition": ["achievement"],
                "type": "Aggregate"
            }
            ],
            [
                "id": "m1",
                "father_id": ["s4", "t4"],
                "NL": "聚合操作...",
                "sql": "SELECT 'WTD' as period, SUM(amt_notax) as withouttax_amount, SUM(amt_notax_target) as target_amount, case when SUM(amt_notax_target) = 0 then 0 else SUM(amt_notax)/SUM(amt_notax_target)-1 END as achievement FROM dm_fact_sales_chatbi WHERE  date_code Between {1st of this week} AND CURRENT_DATE - INTERVAL '1 day' UNION ALL SELECT 'MTD'  as period, SUM(amt_notax) as withouttax_amount, SUM(amt_notax_target) as target_amount, case when SUM(amt_notax_target) = 0 then 0 else SUM(amt_notax)/SUM(amt_notax_target)-1 END as achievement FROM dm_fact_sales_chatbi WHERE date_code Between TO_CHAR(DATE_TRUNC('MONTH', CURRENT_DATE), 'YYYY-MM-DD') AND TO_CHAR(CURRENT_DATE - INTERVAL '1 day') ",
                "condition": ["period", "achievement"]
                "type": "Join"
            ]
            ]

        
    """
    prompt2 = f"""
        # 开始执行
        输入:
        query: {query}
        sql: {sql}

        请严格按照上述规范输出结果，确保：
        1. 每个步骤的SQL语法正确且可执行
        2. 父子关系准确无误
        3. 操作类型分类正确
        4. 解释文本清晰完整
        5. 输出仅为json内容，无其他解释信息
    """
    return prompt+prompt2

def get_chart_prompt(query, data):
    prompt = """
            You are a seasoned business data analyst and need to process visualization recommendation requests according to the following rules:
            # Task Description
            1. The user will provide a question description and corresponding structured data (including column names and data rows).
            2. Based on the question and data, determine the most suitable visualization type from the following options:
            - **Bar chart**: Use for comparing categories (≤6 distinct categories) or discrete time series data.
            - **Line chart**: Use for showing trends over continuous time (≥3 time points) or continuous variable changes.
            - **Pie chart**: Use for displaying proportions of a whole (3-5 categories).
            3. Identify the appropriate data fields for:
            - **x-axis**: Data suitable as the horizontal axis (e.g., categories, time points).
            - **y-axis**: Data suitable as the vertical axis (e.g., numerical values).
            - **title**: A concise chart title derived from the question and data.
            - **x-legend**: Label for the x-axis.
            - **y-legend**: Label for the y-axis.
            - **tooltip**: Additional data to display on hover for context (e.g., related metrics or percentages).
            4. Outlier handling, if there is a value in the x or y axis data that cannot be visualized, please handle it as a value that can be visualized normally, e.g. for 'None' please handle the value as 0.

            # Input Data Format
            The input will be a JSON object with:
            - `"question"`: A string describing the analysis goal.
            - `"data"`: An object with:
                - `"columns"`: List of column names (e.g., `["month_id", "sales_amt"]`).
                - `"data"`: List of tuples, each representing a row of data (e.g., `[(202502, -5235)]`).

            ### Example Input
            ```json
            {
            "question": "What is the sales MOM% \for APAC EC?",
            "data": {
                "columns": ["month_id", "sales_amt", "sales_notax", "sales_notax_mom_per"],
                "data": [[202502, -5235, -4634, -1.00029011188026305147]]
            }
            ```

            # Processing Requirements
            1. Select exactly one visualization type (bar-chart, line-chart, or pie-chart) based on the data and question:
                - Verify the data meets the conditions for the chosen type (e.g., number of categories, time points).
                - If no type is suitable, default to bar-chart.
            2. Assign data fields to:
                - "x": List of values or column names for the x-axis.
                - "y": List of numerical values for the y-axis.
                - "title": A string summarizing the chart's purpose.
                - "x-legend": A string describing the x-axis.
                - "y-legend": A string describing the y-axis.
                - "tooltip": A string with additional data (e.g., a column name and value).
            3. Output must be a pure JSON object with no additional text or explanations.
            # Output Format
            ```json
            {
                "vis_tag": "string", // One of: "bar-chart", "line-chart", "pie-chart"
                "x": [], // Array of x-axis data (values or column names)
                "y": [], // Array of y-axis numerical data
                "title": "string", // Chart title
                "x-legend": "string", // x-axis label
                "y-legend": "string", // y-axis label
                "tooltip": "string" // Additional data for hover display
            }
            ```
            ### Example Output
            ```json
            {
                "vis_tag": "bar-chart",
                "x": ["sales_amt", "sales_notax"],
                "y": [-5235, -4634],
                "title": "Sales for APAC EC in Month 202502",
                "x-legend": "Sales Type",
                "y-legend": "Amount",
                "tooltip": "sales_notax_mom_per: -1.000290111880263"
            }
            ```
        }
        """

    prompt2 = f"""
    # Input
    "question": {query},
    "data": {data}
    """

    return prompt + prompt2
    
def rewrite_sql_prompt(sql, e):
    prompt = f"""
        请作为postgresql代码专家，分析该sql代码可能存在的语法错误，并根据错误信息{e}, 修正这条sql语句：{sql}。
        请仅返回正确的sql，无其他额外内容。
    """
    return prompt