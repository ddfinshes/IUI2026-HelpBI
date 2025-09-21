import sys
import os
import ast

# 添加backend目录到Python路径
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from tools.my_model import ChatModel
from tools.prompt import query_write_prompt, hightlight_extract, keywords_extract_prompt


def query_write(query):
    chat_model = ChatModel()
    prompt = query_write_prompt(query)
    response = chat_model.chat_with_system(
            system_prompt="You are a helpful assistant.",
            user_message=prompt
        )
    return response

def query_hightlight(query):
    chat_model = ChatModel()
    prompt = hightlight_extract(query)
    response = chat_model.chat_with_system(
        system_prompt="You are a helpful assistant.",
        user_message=prompt
    )
    # print(type(response))
    response = ast.literal_eval(response)
    if not isinstance(response, list):
        response = [str(response)]
    return response

def keyword_extract(query):
    chat_model = ChatModel()
    prompt = keywords_extract_prompt(query)
    response = chat_model.chat_with_system(
        system_prompt="You are a helpful assistant.",
        user_message=prompt
    )
    response = ast.literal_eval(response)
    if not isinstance(response, list):
        response = [str(response)]
    return response

if __name__ == '__main__':
    query = 'what is the MTD sales achievement for China FP?'
    # response = query_write(query)
    response = keyword_extract(query)
    print(response)