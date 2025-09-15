import openai
import requests
from decimal import Decimal
import http.client
import json
import re
def json_pattern(result_ans):
    result = re.sub(r'```json|```', '', result_ans).strip()
    return result

def deepseek(messages):
    model = "deepseek-r1:7b"
    payload = {"model": model, "prompt": messages, "stream": False}
    response = requests.post(
        "http://localhost:11434/api/generate",
        json=payload
    )
    return response.json()["response"]

def gpt_baicai(messages):
    conn = http.client.HTTPSConnection("api.baicaigpt.cn")
    payload = json.dumps({
    "model": "gpt-4o-mini",
    "messages": messages
    })
    headers = {
    'Authorization': 'Bearer sk-UnAxAzyzsl06tpp9d9LCi44C7X4IyWg8QU9DQeWI8wKK6',
    'Content-Type': 'application/json'
    }
    conn.request("POST", "/v1/chat/completions", payload, headers)
    res = conn.getresponse()
    data = res.read().decode("utf-8")
    print(data)
    return data

def gpt(messages):
    APIKEY = "sk-zRyfr0mCsjr3xuqNHmyNtZBFsilZVpeqm0ELZyDOkKfObOp7"
    BASEURL = "https://xiaoai.plus/v1"
    GPTSETTING = {
        "model": "o3-mini", # gpt-3.5-turbo
        "temperature": 0,
        "max_tokens": 5120, #4096+1024
    }
    MODEL_SET = "o3-mini"
    MAX_TOKENS = 5120

    client = openai.OpenAI(api_key=APIKEY, base_url=BASEURL)
    i = 0
    result_ans = None
    while i < 3:
        try:
            result = client.chat.completions.create(
                model = MODEL_SET,
                messages=messages,
                temperature=GPTSETTING["temperature"],
                max_tokens=MAX_TOKENS,
            )
            if result.choices is None:
                print(result.message)
                i += 1
            else:
                result_ans = result.choices[0].message.content
            
                result_ans = json_pattern(result_ans=result_ans)
                return result_ans
        except Exception as e:
            i += 1
            print("-------------------gpt error----------------: ", e)
    return result_ans

def llm(model_name='gpt', messages=""):
    # print(messages)
    if model_name == "gpt":
        return gpt(messages)
    elif model_name == 'deepseek':
        return deepseek(messages)
    elif model_name == "gpt_baicai":
        return gpt_baicai(messages)

