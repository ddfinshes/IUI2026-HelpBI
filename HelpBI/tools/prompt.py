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
        1. dm_fact_sales_chatbi: Store sales summary table, stores daily sales summary data for each store by date, as well as daily target sales data for each store, and also includes sales summary data for the same day last week/last month/last year.
            - date_code: String; format(YYYY-MM-DD).
            - week_id: String; format(YYYYWW); fiscal year week ID.
            - month_id: String; format(YYYYMM).
            - year_id: String; format(YYYY).
            - store_code: String; store code.
            - store_name: String; store name. When querying by store name, use fuzzy search: store_name like '%?%'.
            - customer_name: String; distributor name to which the store belongs.
            - country: String; country where the store is located.
            - channel: String; store channel: EC/FP/O&O.
            - sub_channel: String; store sub-channel: EC/BH/FH/UA.com/others.
            - store_type: String; store type: BH/FH.
            - region: String; store region: north/south/east/west.
            - province: String; province where the store is located, stored in pinyin.
            - city: String; city where the store is located, stored in pinyin.
            - area: decimal; store area, only physical retail stores have area data.
            - cluster: String; store level: AAA/A/B/C.
            - comp_flag: String; Y/N; when calculating COMP store sales or metrics, need to filter comp_flag=Y.
            - qty_return: decimal; number of returned items.
            - amt_return: decimal; amount of returned items; [Amount field].
            - orig_price: decimal; original sales price without discount. [Amount field].
            - amt: decimal; sales amount on date_code, net sales; [Amount field].
            - lw_amt: decimal; sales amount on the same day last week; [Amount field].
            - lm_amt: decimal; sales amount on the same day last month; [Amount field].
            - lyd_amt: decimal; sales amount on the same day last year; [Amount field].
            - amt_target: decimal; target sales amount on date_code; [Amount field].
            - qty: decimal; sales quantity on date_code.
            - lw_qty: decimal; sales quantity on the same day last week.
            - lm_qty: decimal; sales quantity on the same day last month.
            - lyd_qty: decimal; sales quantity on the same day last year.
            - qty_target: decimal; target sales quantity on date_code.
            - trans: decimal; number of transactions on date_code.
            - lw_trans: decimal; number of transactions on the same day last week.
            - lm_trans: decimal; number of transactions on the same day last month.
            - lyd_trans: decimal; number of transactions on the same day last year.
            - trans_target: decimal; target number of transactions on date_code.
            - traffic: decimal; customer traffic on date_code.
            - lw_traffic: decimal; customer traffic on the same day last week.
            - lm_traffic: decimal; customer traffic on the same day last month.
            - lyd_traffic: decimal; customer traffic on the same day last year.
            - traffic_target: decimal; target customer traffic on date_code.
            - amt_target_f0: decimal; F0 target amount; [Amount field].
            - amt_target_f1: decimal; F1 target amount; [Amount field].
            - amt_target_f2: decimal; F2 target amount; [Amount field].
            - amt_target_f3: decimal; F3 target amount; [Amount field].
            - amt_target_f4: decimal; F4 target amount; [Amount field].
        2. dm_fact_sales_sku_chatbi: Store product sales table, stores daily product sales data for each store.
            - date_code: String; format(YYYY-MM-DD).
            - week_id: String; format(YYYYWW); fiscal year week ID.
            - month_id: String; format(YYYYMM).
            - year_id: String; format(YYYY).
            - store_code: String; store code.
            - store_name: String; store name. When querying by store name, use fuzzy search: store_name like '%?%'.
            - customer_name: String; distributor name to which the store belongs.
            - country: String; country where the store is located.
            - channel: String; store channel: EC/FP/O&O.
            - sub_channel: String; store sub-channel: EC/BH/FH/UA.com/others.
            - store_type: String; store type: BH/FH.
            - region: String; store region: north/south/east/west.
            - province: String; province where the store is located, stored in pinyin.
            - city: String; city where the store is located, stored in pinyin.
            - area: decimal; store area, only physical retail stores have area data.
            - cluster: String; store level: AAA/A/B/C.
            - division: Division attribute of the product; e.g., Apparel/Accessories/Footwear.
            - enduse: End use of the product; e.g., Training/Golf/Running.
            - silhouette: Silhouette of the product; e.g., Short Sleeve/Warmup Tops/Slides.
            - fit_type: Fit type of the product; e.g., Loose/Regular/Fitted.
            - material: String; article of product; e.g., 1234567-123.
            - SKU: String; product SKU.
            - product_name: String; product name, use fuzzy search when querying.
            - key_stories: Key category, key items of the product. Use fuzzy search when querying.
            - product_line: String; e.g., inline/MFO.
            - msrp: decimal; product label price.
            - qty: decimal; number of sales items.
            - amt: decimal; sales amount; [Amount field].
            - season_code: String; season of the product; e.g., SS24/FW24/SS25.
        3. dm_fact_onhand_chatbi: Store inventory table, stores daily product inventory for retail stores. Usually only keeps inventory data for Saturdays.
            - store_code: String; store code.
            - store_name: String; store name. When querying by store name, use fuzzy search: store_name like '%?%'.
            - customer_name: String; distributor name to which the store belongs.
            - country: String; country where the store is located.
            - channel: String; store channel: EC/FP/O&O.
            - store_type: String; store type: BH/FH.
            - region: String; store region: north/south/east/west.
            - province: String; province where the store is located, stored in pinyin.
            - city: String; city where the store is located, stored in pinyin.
            - area: decimal; store area, only physical retail stores have area data.
            - cluster: String; store level: AAA/A/B/C.
            - date_code: String; format(YYYY-MM-DD).
            - division: Division attribute of the product; e.g., Apparel/Accessories/Footwear.
            - enduse: End use of the product; e.g., Training/Golf/Running.
            - silhouette: Silhouette of the product; e.g., Short Sleeve/Warmup Tops/Slides.
            - fit_type: Fit type of the product; e.g., Loose/Regular/Fitted.
            - material: String; article of product; e.g., 1234567-123.
            - product_name: String; product name, use fuzzy search when querying.
            - key_stories: Key category, key items of the product.
            - product_line: String; e.g., inline/MFO.
            - stock: decimal; quantity of product inventory.
            - intransit: decimal; quantity of product in transit.
            - stock_amt: decimal; monetary value of product inventory; [Amount field].
            - intransit_amt: decimal; monetary value of product in transit; [Amount field].
        4. chatbi_dim_store: Store master data table, stores information of all stores in the company.
            - country: String; country where the store is located.
            - channel: String; store channel: EC/FP/O&O.
            - sub_channel: String; store sub-channel: EC/BH/FH/UA.com/others.
            - customer_name: String; distributor name to which the store belongs.
            - region: String; store region: north/south/east/west.
            - province: String; province where the store is located, stored in pinyin.
            - city: String; city where the store is located, stored in pinyin.
            - area: decimal; store area, only physical retail stores have area data.
            - store_type: String; store type: BH/FH.
            - store_code: String; store code.
            - store_name: String; store name. When querying by store name, use fuzzy search: store_name like '%?%'.
            - status: String; store open/close status: open/closed.
            - open_date: date; store opening date.
            - close_date: date; store closing date. Fill in when the store is closed, for open stores it is null or 9999-12-31.
            - cluster: String; store level: AAA/A/B/C.
        5. dm_member_chatbi: Member user table, stores member-related information.
            - birthday: String; format(YYYY-MM-DD); member's birthday date.
            - country: String; country to which the member belongs.
            - register_date_str: date; user's membership registration date.
            - member_code: String; member number, the unique code of the member.
            - gender: String; gender: Male/Female.
            - regist_channel: String; registration channel, e.g., 2-UA_CN/3-TMALL/7-DOUYIN/9-Campaign/8-WeChat/6-FP/4-WMS/5-JD/1-Retail.
            - regist_sub_channel: String; registration sub-channel, e.g., FP_ULEE/MA_TMALL/Wechat.
        6. dm_member_sales_chatbi: Member transaction information table, stores member transaction information. Each record also contains basic member information, and the data granularity is stored by transaction.
            - birthday: String; format(YYYY-MM-DD); member's birthday date.
            - register_date_str: date; user's membership registration date.
            - country: String; country.
            - member_code: String; member number, the unique code of the member.
            - gender: String; gender: Male/Female.
            - regist_channel: String; registration channel, e.g., 2-UA_CN/3-TMALL/7-DOUYIN/9-Campaign/8-WeChat/6-FP/4-WMS/5-JD/1-Retail.
            - regist_sub_channel: String; registration sub-channel, e.g., FP_ULEE/MA_TMALL/Wechat.
            - transaction_date: date; transaction date.
            - amt_total: decimal; order amount, not the actual transaction amount.
            - amt_real: decimal; actual payment amount, use this field for transaction amount.
            - qty_total: decimal; quantity of goods in the transaction.
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
        # Role Definition
        You are a senior PostgreSQL expert specializing in data analysis for the retail sector. Your task is to decompose SQL queries into executable steps and output them in a structured JSON format to facilitate subsequent tree-structured visualization.

        # Task Requirements
        1. Input Processing:
        - Accept input containing two parts: query and sql
        - query: describes the business purpose of the SQL query
        - sql: the SQL code to be analyzed

        2. Output Specification:
        - Return a list, where each element is a dictionary describing a step.
        - Each step must include the following fields:
            * id: Unique identifier (format: type letter + number, e.g., s1, t1, etc. Do not use u, r, k, or a as type letters)
            * father_id: List of previous step IDs (empty list if none)
            * NL: Natural language explanation (detailed description of the operation's purpose and logic), explanations should related to the query and easy to understand.
            * sql: Independently executable SQL fragment. Additionally, to mitigate the risk of excessive resource consumption and performance degradation, intermediate SQL statements shall incorporate a row limitation clause, such as LIMIT 100, at appropriate stages of query execution.
            * condition: The main column names affected by this step
            * type: Atomic operation type (strictly follow the classification standard)

        3. Decomposition Principles:
        - Ensure that the SQL of each step can be executed independently.
        - When encountering parallel structures such as UNION/UNION ALL/JOIN:
            * Split into independent subquery chains.
            * Finally, add a merge step whose father_id points to the end nodes of each subchain.
        - Complex expressions (such as nested CASE WHEN) should be decomposed step by step.

        # Atomic Operation Classification Standard
        1. Filter: Conditional filtering such as WHERE/DISTINCT
        2. Select: SELECT specific query columns
        3. Aggregate: Aggregation calculations such as SUM/AVG/COUNT
        4. GroupBy: GROUP BY/HAVING grouping operations
        5. Sort/Limit: Result sorting and limiting such as ORDER BY/LIMIT
        6. Join: Table join operations such as JOIN/UNION
        7. Transform: Data transformation such as CASE WHEN/arithmetic operations
        8. Window: Window function calculations

        # Processing Steps
        1. Syntax Analysis: Identify key operation nodes in the SQL.
        2. Step Decomposition: Break down compound operations into atomic operations.
        3. Dependency Construction: Determine parent-child relationships between steps.
        4. Explanation Generation: Write business and technical explanations for each step.
        5. Result Validation: Ensure all SQL fragments can be executed independently.

        # Example output format
        [
        {
            "id": "s1",
            "father_id": [],
            "NL": "Explanation text...",
            "sql": "Independently executable SQL",
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
                "NL": "This is the most basic query form. It selects data from the dm_fact_sales_chatbi table for the period from February 10 to February 12, 2025, displaying each row with the period marked as 'WTD' (Week-to-Date), along with the original values of the untaxed amount and target amount.",
                "sql": "SELECT 'WTD' as period, amt_notax, amt_notax_target FROM dm_fact_sales_chatbi WHERE date_code BETWEEN '2025-02-10' AND '2025-02-12'",
                "condition": ["period", "amt_notax", "amt_notax_target"],
                "type": "Select"
            },
            {
                "id": "s2",
                "father_id": ["s1"],
                "NL": "Added SUM aggregation function to the base query to calculate, for the selected time period:\nwithouttax_amount: total untaxed amount;\ntarget_amount: total target amount.",
                "sql": "SELECT 'WTD' as period, SUM(amt_notax) as withouttax_amount, SUM(amt_notax_target) as target_amount FROM dm_fact_sales_chatbi WHERE date_code BETWEEN '2025-02-10' AND '2025-02-12'",
                "condition": ["withouttax_amount", "amt_notax_target"],
                "type": "Aggregate"
            },
            {
                "id": "s3",
                "father_id": ["s2"],
                "NL": "On the basis of aggregation, a division calculation is added to show the original ratio of actual amount to target amount (withouttax_amount/target_amount). The CASE WHEN statement is used to handle division by zero: if the total target amount is zero, return 0 to avoid runtime errors.",
                "sql": "SELECT 'WTD' as period, SUM(amt_notax) as withouttax_amount, SUM(amt_notax_target) as target_amount, CASE WHEN SUM(amt_notax_target) = 0 THEN 0 ELSE SUM(amt_notax) / SUM(amt_notax_target) END as safe_ratio FROM dm_fact_sales_chatbi WHERE date_code BETWEEN '2025-02-10' AND '2025-02-12'",
                "condition": ["safe_ratio"],
                "type": "Aggregate"
            },
            {
                "id": "s4",
                "father_id": ["s3"],
                "NL": "Subtract 1 from the safe ratio calculation to obtain the actual achievement rate (e.g., 1.1 means 10% over target, 0.9 means 10% below target). Formula: withouttax_amount / target_amount - 1",
                "sql": "SELECT 'WTD' as period, SUM(amt_notax) as withouttax_amount, SUM(amt_notax_target) as target_amount, CASE WHEN SUM(amt_notax_target) = 0 THEN 0 ELSE SUM(amt_notax) / SUM(amt_notax_target) - 1 END as achievement FROM dm_fact_sales_chatbi WHERE date_code BETWEEN '2025-02-10' AND '2025-02-12'",
                "condition": ["achievement"],
                "type": "Aggregate"
            }
            ],
            [
            {
                "id": "t1",
                "father_id": [],
                "NL": "This is the most basic query form. It selects data from the dm_fact_sales_chatbi table for the period from February 10 to February 12, 2025, displaying each row with the period marked as 'WTD' (Week-to-Date), along with the original values of the untaxed amount and target amount.",
                "sql": "SELECT 'MTD' as period, amt_notax, amt_notax_target FROM dm_fact_sales_chatbi WHERE date_code BETWEEN '2025-02-10' AND '2025-02-12'",
                "condition": ["period", "amt_notax", "amt_notax_target"],
                "type": "Select"
            },
            {
                "id": "t4",
                "father_id": ["t3"],
                "NL": "Subtract 1 from the safe ratio calculation to obtain the actual achievement rate (e.g., 1.1 means 10\% above target, 0.9 means 10% below target). Formula: withouttax_amount / target_amount - 1",
                "sql": "SELECT 'MTD' as period, SUM(amt_notax) as withouttax_amount, SUM(amt_notax_target) as target_amount, CASE WHEN SUM(amt_notax_target) = 0 THEN 0 ELSE SUM(amt_notax) / SUM(amt_notax_target) - 1 END as achievement FROM dm_fact_sales_chatbi WHERE date_code BETWEEN '2025-02-10' AND '2025-02-12'",
                "condition": ["achievement"],
                "type": "Aggregate"
            }
            ],
            [
                "id": "m1",
                "father_id": ["s4", "t4"],
                "NL": "Aggregate operation...",
                "sql": "SELECT 'WTD' as period, SUM(amt_notax) as withouttax_amount, SUM(amt_notax_target) as target_amount, case when SUM(amt_notax_target) = 0 then 0 else SUM(amt_notax)/SUM(amt_notax_target)-1 END as achievement FROM dm_fact_sales_chatbi WHERE  date_code Between {1st of this week} AND CURRENT_DATE - INTERVAL '1 day' UNION ALL SELECT 'MTD'  as period, SUM(amt_notax) as withouttax_amount, SUM(amt_notax_target) as target_amount, case when SUM(amt_notax_target) = 0 then 0 else SUM(amt_notax)/SUM(amt_notax_target)-1 END as achievement FROM dm_fact_sales_chatbi WHERE date_code Between TO_CHAR(DATE_TRUNC('MONTH', CURRENT_DATE), 'YYYY-MM-DD') AND TO_CHAR(CURRENT_DATE - INTERVAL '1 day') ",
                "condition": ["period", "achievement"]
                "type": "Join"
            ]
            ]

        
    """
    prompt2 = f"""
        # Begin Execution
        Input:
        query: {query}
        sql: {sql}

        Please strictly follow the above specifications to output the result, ensuring:
        1. The SQL syntax of each step is correct and executable.
        2. Parent-child relationships are accurate.
        3. Operation types are correctly classified.
        4. Explanatory text is clear and complete.
        5. The output is JSON only, with no additional explanations or information.
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
        Please analyze this SQL code "{sql}" as a PostgreSQL expert to identify potential syntax errors, and correct the statement based on the error message {e}. Only return the corrected SQL without any additional content.
    """
    return prompt