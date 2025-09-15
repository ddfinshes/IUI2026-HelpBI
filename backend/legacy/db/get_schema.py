import psycopg2

# 数据库连接配置
conn_params = {
    "dbname": "chatbi",
    "user": "postgres",
    "password": "123456",
    "host": "127.0.0.1",
    "port": "5432"
}

# SQL 查询
query_sql = """
SELECT 
    table_schema,
    table_name,
    column_name,
    data_type,
    character_maximum_length,
    is_nullable,
    column_default
FROM 
    information_schema.columns
WHERE 
    table_schema NOT IN ('pg_catalog', 'information_schema')
ORDER BY 
    table_schema, table_name, ordinal_position;
"""

# 输出文件路径
output_file = "./schema_information.txt"

try:
    # 连接到数据库
    conn = psycopg2.connect(**conn_params)
    cursor = conn.cursor()

    # 执行查询
    cursor.execute(query_sql)
    rows = cursor.fetchall()

    # 获取列名
    col_names = [desc[0] for desc in cursor.description]

    # 将结果写入文件
    with open(output_file, "w") as f:
        # 写入列名
        f.write("\t".join(col_names) + "\n")
        # 写入每一行数据
        for row in rows:
            f.write("\t".join(map(str, row)) + "\n")

    print(f"数据已成功导出到本地文件 {output_file}")
except Exception as e:
    print(f"发生错误: {e}")
finally:
    # 关闭连接
    if cursor:
        cursor.close()
    if conn:
        conn.close()