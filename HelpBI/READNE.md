# 执行语句
uvicorn main:app --reload --host 127.0.0.1 --port 8000 | cat
# 测试语句
curl -s -X POST 'http://127.0.0.1:8000/api/query?query=what%20is%20the%20MTD%20sales%20achievement%20for%20China%20FP%3F'

# API接口
主函数main.py中：
- /api/query：接收用户query返回右视图（树状图需要的json数据）
    - json数据格式会持续在format/structure.json中更新

# 数据库（2026.09.22还没写到，可不用进行这步骤）
1. 需要安装postgresql数据库
2. 密码设置为123456
3. 创建数据库后，手动依次执行db/create_table.txt中的创建表的语句
4. 使用python 执行insert.py 插入数据，偶然有几条输出表示插入语句失败可忽略。