# 改良版 insert.py
import psycopg2
import csv
import os

def insert_csv_to_table(conn, cursor, table_name, csv_file):
    success_count = 0
    fail_count = 0
    failed_rows = []

    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            headers = next(reader)  # 跳过表头
            num_cols = len(headers)

            # 动态生成 INSERT 占位符
            placeholders = ", ".join(["%s"] * num_cols)
            query = f"INSERT INTO {table_name} VALUES ({placeholders})"

            for row in reader:
                try:
                    converted_row = [None if cell == '' else cell for cell in row]
                    cursor.execute(query, converted_row)
                    success_count += 1
                except Exception as e:
                    fail_count += 1
                    failed_rows.append((row, str(e)))

        # 提交事务
        conn.commit()
        print(f"[{table_name}] 插入完成！成功 {success_count} 行，失败 {fail_count} 行")

        # 如果有失败，打印前几条示例
        if fail_count > 0:
            print("部分失败行示例：")
            for r, err in failed_rows[:5]:
                print(f"行: {r}, 错误: {err}")

    except Exception as e:
        conn.rollback()
        print(f"[{table_name}] 导入失败，错误信息: {str(e)}")


if __name__ == "__main__":
    DB_CONFIG = {
        "dbname": "postgres",     # 改成你的数据库名
        "user": "postgres",
        "password": "123456",
        "host": "localhost",
        "port": "5432",
        "options": "-c client_encoding=utf8"
    }

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        print("数据库连接成功！")
    except Exception as e:
        print("数据库连接失败！", str(e))
        exit(1)

    # CSV 文件路径
    root_path = './data/2025-03-04'
    files = os.listdir(root_path)

    for i, file in enumerate(files):
        table_name = file.split('-')[0]   # 文件名开头部分作为表名
        csv_file = os.path.join(root_path, file)

        print(f"\n[{i+1}/{len(files)}] 开始导入 {csv_file} -> {table_name}")
        insert_csv_to_table(conn, cursor, table_name, csv_file)

    if conn:
        cursor.close()
        conn.close()
