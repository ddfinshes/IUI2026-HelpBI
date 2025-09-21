# 读取csv数据插入到数据库表中
import psycopg2
from psycopg2 import sql
import csv
import os


def insert_query(conn, cursor, table_name, CSV_FILE):
    try:
        with open(CSV_FILE, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # 跳过CSV头部
            print(reader)

            # 构造INSERT语句
            insert_query = ''
            print(table_name)
            if table_name == 'dm_fact_sales_chatbi':
                insert_query = sql.SQL("""
                    INSERT INTO dm_fact_sales_chatbi VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                """)
            elif table_name == 'dm_fact_sales_sku_chatbi':
                
                insert_query = sql.SQL("""
                    INSERT INTO dm_fact_sales_sku_chatbi VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                """)
            elif table_name == 'dm_member_sales_chatbi':
                insert_query = sql.SQL("""
                    INSERT INTO dm_member_sales_chatbi VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                """)
            elif table_name == 'edw_dim_store':
                insert_query = sql.SQL("""
                    INSERT INTO edw_dim_store VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                """)
            elif table_name == 'dm_fact_onhand_chatbi':
                insert_query = sql.SQL("""
                    INSERT INTO dm_fact_onhand_chatbi VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                """)
            elif table_name == 'dm_member_chatbi':
                insert_query = sql.SQL("""
                    INSERT INTO dm_member_chatbi VALUES (
                       %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                """)
            elif table_name == 'edw_dim_calendar':
                insert_query = sql.SQL("""
                    INSERT INTO edw_dim_calendar VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s                    )
                """)
            elif table_name == 'edw_dim_store_prod':
                insert_query = sql.SQL("""
                    INSERT INTO edw_dim_store_prod VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """)
            elif table_name == 'edw_dim_channel':
                insert_query = sql.SQL("""
                    INSERT INTO edw_dim_channel VALUES (
                        %s, %s
                """)
            elif table_name == 'dm_dim_holiday_chatbi':
                insert_query = sql.SQL("""
                    INSERT INTO dm_dim_holiday_chatbi VALUES (
                        %s, %s, %s
                """)
            # 批量插入数据
            for row in reader:
                try:
                    # 将所有空字符串转换为None
                    converted_row = [None if cell == '' else cell for cell in row]
                    
                    # 执行插入
                    cursor.execute(insert_query, converted_row)
                    
                except Exception as e:
                    print(f"插入失败的行: {row}")
                    print(f"错误信息: {str(e)}")
                    conn.rollback()  # 回滚当前事务
                    return -1

            # 提交事务
            conn.commit()
            print("数据插入完成！")

    except Exception as e:
        print(f"发生错误: {str(e)}")
        conn.rollback()

        

if __name__ == "__main__":
    # 数据库连接配置
    DB_CONFIG = {
        "dbname": "postgres",
        "user": "postgres",
        "password": "123456",
        "host": "localhost",
        "port": "5432",
        "options": "-c client_encoding=utf8"
    }
    
    # 尝试建立数据库连接，并判断是否连接成功
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        print("数据库连接成功！")
    except Exception as e:
        print("数据库连接失败！")
        print(f"错误信息: {str(e)}")
        exit(1)
        
    
    # CSV文件路径
    table_name = ''
    CSV_FILE = ""
    root_path = './data/2025-03-04'
    dirs = os.listdir(root_path)
    i = 0
    for dir in dirs:
        table_name = dir.split('-')[0]
        CSV_FILE = os.path.join(root_path, dir)
        i += 1
        if(insert_query(conn, cursor, table_name, CSV_FILE)):
            print('Error: '+table_name)
            print("Error index: ", i-1)
            continue
        
        
    if conn:
            cursor.close()
            conn.close()
    