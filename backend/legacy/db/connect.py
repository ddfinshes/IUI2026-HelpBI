import psycopg2 ##导入
from psycopg2 import OperationalError

## 通过connect方法，创建连接对象 conn
## 这里连接的是本地的数据库


def excute_sql(query):
#     query = """
#       SELECT 
#  month_id,
#     SUM(amt) as sales_amt,  
#  SUM(amt_notax) as Sales_notax , 
#  SUM(amt_notax)/SUM(lm_amt_notax)-1 as sales_notax_mom_per   
#  FROM 
#     dm_fact_sales_chatbi 
#  WHERE 
#     date_code Between '2025-02-01' AND '2025-02-10'  
#  GROUP BY 
#     month_id
# ;
# """
    try:
        conn = psycopg2.connect(database="chatbi", user="postgres", password="123456", host="127.0.0.1", port="5432")
        cursor = conn.cursor()
        cursor.execute(query)

        # 获取列名
        column_names = [desc[0] for desc in cursor.description]

        # 获取数据
        rows = cursor.fetchall()
        print("数据库查询结果：")
        for row in rows:
            print(row)
        result = {
            "column": column_names,
            "data": rows
        }
        return result
    
    except OperationalError as e:
        print(f"连接数据库失败: {e}")
    except Exception as e:
        # 发生错误时回滚事务
        if 'conn' in locals():
            conn.rollback()
        print(f"操作失败: {e}")
    finally:
        # 4. 关闭游标和连接
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
        print("数据库连接已关闭。")
        ## 执行之后不报错，就表示连接成功了！
# query = 'SELECT * FROM test;'
# excute_sql(query)

excute_sql(query='')