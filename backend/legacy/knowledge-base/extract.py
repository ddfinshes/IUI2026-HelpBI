# 获取到底涉及数据库的哪些表
import re
#read txt method one


def extract_table_names(sql):
    # 提取 FROM 后的子句部分（忽略子查询）
    from_match = re.search(
        r'\bFROM\s+((?:(?!\bWHERE\b|\bGROUP BY\b|\bHAVING\b|\bORDER BY\b|\bLIMIT\b|;).)*)',
        sql, re.IGNORECASE | re.DOTALL
    )
    if not from_match:
        return []
    
    # 移除括号内容（简单处理子查询）
    from_clause = re.sub(r'\(.*?\)', '', from_match.group(1), flags=re.DOTALL)
    
    # 匹配表名规则（含 schema 和 JOIN 逻辑）
    table_pattern = re.compile(r'''
        (?:                          # 匹配前缀关键字
            \bFROM\s+                # 起始 FROM
            |,\s*                    # 逗号分隔
            |\b(?:INNER\s+|LEFT\s+|RIGHT\s+|FULL\s+)?JOIN\s+  # 各类 JOIN
        )
        ([\w.]+)                     # 捕获表名/模式名
    ''', re.IGNORECASE | re.VERBOSE)
    
    # 提取所有候选表名
    tables = table_pattern.findall(from_clause)
    
    # 提取第一个表名（可能被正则遗漏）
    first_table = re.search(r'^\s*([\w.]+)', from_clause)
    if first_table and first_table.group(1) not in tables:
        tables.insert(0, first_table.group(1))
    
    # 过滤无效词并去重
    seen = set()
    return [t for t in tables 
            if t.lower() not in {'from', 'join'} 
            and not (seen.add(t.lower()) or seen.__contains__(t.lower()))]

if __name__ == "__main__":
    tables = []
    i = 0
    with open("mobileandtableau.txt", "r", encoding='utf-8') as f:  #打开文本
        lines = f.readlines()
        # print(lines)
        
        for line in lines:
            i += 1
            if 'FROM' in line and len(line) > 8:
                line = line[line.index('FROM'):-1]
                ex = ['inner', 'join', ')', 'AS', 'WHERE']
                tx = -1
                for e in ex:
                    if e in line:
                        tx = line.index(e)
                        break
                line = line[0: tx]
                line_list = line.replace('\n', '').split(' ')
                # print(line_list)
                if len(line_list)>1: 
                    index = line_list.index('FROM')
                    # print(line_list[index+1:-1])
                    tables.extend(line_list)
            elif 'FROM' in line:
                line2 = lines[i].strip().split(' ')
                tables.extend(line2)
                # print(line2)
    
                
    #{'', 'Sep2024ReturningCustomers,', 'Sep2024NewCustomers,', 'sales', 'CASE', 'Store_traffic_monthly', 'NOT', '1)', '=', 'FROM', "'Total'", 'Sep2023RepeatCustomers)', 'MFOSales202526.mfo_amt', 'MFO_amt_per202526,', 'total_amt', 'SELECT', '/', 'Sep2023RepeatCustomers;', 'Store_opentime', 'TotalSales202526', 'TotalSalesly.total_amt', 'title,', ')', 'dm_fact_sales_sku_chatbi', 'Sep2024ReturningCustomers)', 'MFOSalesly,', 'Sep2024RepeatCustomers)', 'MFOSales202526', '(SELECT', 'TotalSales202527', 'inner', 'IN', 'COUNT(DISTINCT', 'MFOSales202527.mfo_amt', 'MFOSales202527,', 'RankedPartners', 'stock', 'Sep2024FirstTimeCustomers)', 'WHERE', 'AS', 'join', 'dm_member_sales_chatbi', '0', 'TotalSales202527.total_amt', 'Sep2023HistoricalTransactions)', 'Sep2024RepeatCustomers,', 'edw_dim_calendar', 'Sep2024Transactions', 'MFO_amt_perlastyear', 'InvOfLastSaturday', 'CurrentPurchases', 'Store_effi', 'salesQty', 'rank', 'END', 'MFOSales202526,', 'Sep2023FirstTimeCustomers)', 'Sep2023NewCustomers,', 'member_code)', 'daily_aov', 'WITH', 'WHEN', 'MFOSalesly', 'TotalSalesly', 'SUM', 'MFO_amt_per202527,', 'Sep2023ReturningCustomers,', 'mfo_amt', 'TotalSales202526.total_amt', 'amt', 'ELSE', 'MFOSalesly.mfo_amt', 'Sep2023ReturningCustomers)', 'THEN', 'MFOSales202527', 'member_code', 'Sep2023Transactions', '(', 'Sep2024HistoricalTransactions)', "'MFO'", 'customer_name'}
    print(set(tables))

                # if line.endswith('\n'):
                #     tables.append(lines[i])
                # else:
                #     table = line.split[' '][1:-1]
                
# {
# 'edw_dim_store',  'dm_fact_sales_sku_chatbi', 
# 'dm_fact_sales_chatbi', 'dm_member_sales_chatbi', 
#  'dm_fact_onhand_chatbi', 'dm_member_chatbi',  'edw_dim_calendar', 
#  'edw_dim_store_prod',  'edw_dim_channel'}

# {'dm_fact_sales_chatbi', 'dm_dim_holiday_chatbi', 'dm_fact_onhand_chatbi', 'dm_fact_sales_sku_chatbi'}
 
    
