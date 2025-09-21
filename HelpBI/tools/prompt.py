

def query_write_prompt(query):
    prompt = f"""
        你是一个数据分析专家，请将用户的自然语言查询，表达更清晰、符合数据分析思维的表达。严格按照输出要求返回，返回的结果仅是修改后的语句，无额外内容。
        注意，请基于今天的日期修改语句，今天的日期为2025年2月10日。

        【输入输出示例】：
        输入：“帮我看看上个月北京的销售情况”  
        输出：“查询2025年1月1日至2025年1月31日期间，北京市的销售金额和订单数量，按产品类别分组统计。”

        输入：“对比一下今年和去年华东区的用户增长”  
        输出：“对比2025年1月1日至2025年12月31日与2024年1月1日至2024年12月31日期间，华东地区（包括上海、江苏、浙江、安徽、福建、江西、山东）的注册用户数量，按月汇总。”

        输入：“哪个产品的销量最好？”  
        输出：“统计最近一年（2025年1月1日至2025年2月10日）所有产品的总销量，按产品名称分组，并排序取前十名。”

        输入：“WTD / MTD / QTD / YTD sales vs Target?”
        输出：“统计2025年WTD、MTD、QTD和YTD的实际销售额与销售目标。”

        现在请处理以下输入：
        输入：{query}  
        输出：
        """
    return prompt

def hightlight_extract(writed_query):
    prompt = f"""
    请你作为数据分析专家，请按以下要求处理查询：
    1. 识别查询中涉及的所有关键业务指标（如销售额、用户数等）
    2. 提取所有时间范围表述（如年度、季度、月度等时间段）
    3. 识别所有比较维度（如实际值vs目标值、同期对比等）
    4. 将提取出的关键元素以数组格式返回，仅返回列表，无额外内容。

    示例：
    输入："统计2025年WTD、MTD、QTD和YTD的实际销售额与销售目标"
    输出：["2025年", "WTD", "MTD", "QTD", "YTD", "实际销售额", "销售目标"]

    输入："分析各区域2024年第一季度客户满意度得分"
    输出：["2024年", "第一季度", "区域", "客户满意度得分"]

    输入："对比去年和今年上半月的网站访问量"
    输出：["去年", "今年", "上半月", "网站访问量"]

    请处理以下查询：
    输入：{writed_query}
    输出：
    """
    return prompt

def keywords_extract_prompt(query):
    prompt = f"""
        Analyze the user's query and extract the keywords that should be used to query the knowledge base. The knowledge base includes keywords related to the following categories:

            • Date-related: This week, Last week, F-YTD, C-YTD, YTD, MTD, QTD, LWK, WTD, FY23, FY24, week id  

            • Store-related: country China, region APAC, Store Name, platform, Channel, EC, FP, O&O, Store Type, BH, FH, Comp flag, customer_name, store code  

            • Commodity-related: key_stories, MFO, Division, Gender, End Use, Silhouette, Fit Type, Catagory of merchandise, Season code, sales season, product season, SS, FW  

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