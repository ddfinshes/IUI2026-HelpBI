def process_file_to_chunks(filename):
    # 初始化结果列表
    result = {}
    
    try:
        # 读取文件内容
        with open(filename, 'r', encoding='utf-8') as file:
            content = file.read()
            
        # 按### ID分割为chunks
        chunks = content.split('### ID')[1:]  # 第一个元素可能是空的，所以从[1:]开始
        
        for chunk in chunks:
            # 去除首尾空白
            chunk = chunk.strip()
            if not chunk:
                continue
                
            lines = chunk.split('\n')
            # 完整chunk文本用于查找
            chunk_text = '\n'.join(lines)
            
            # 找到第一个**的位置
            first_star_pos = chunk_text.find('**')
            if first_star_pos == -1:
                continue
                
            # ID值是### ID之后到第一个**之前的内容
            id_value = chunk_text[:first_star_pos].strip()
            
            # description值是**description**:之后的内容
            description_value = chunk_text[first_star_pos:].strip()
            
            # 创建字典并添加到结果列表
            key = 'ID' + id_value
            
            result[key] = description_value
            
        return result
        
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found")
        return []
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return []

def get_chunks(ids):
    filename = "knowledge-base/sql_sample_kb3.txt"  # 替换为你的文件名

    chunks = process_file_to_chunks(filename)
    print(chunks)
    sql_chunks = []
    for idd in ids:
        sql_chunk = chunks[idd]
        sql_chunks.append(sql_chunk)
    return sql_chunks