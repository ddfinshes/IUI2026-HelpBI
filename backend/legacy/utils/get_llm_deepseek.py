# get_llm_deepseek.py
import requests
from decimal import Decimal
# deepseek-r1:7b
def LLM(prompt, model="deepseek-r1:7b"):
    

    payload = {"model": model, "prompt": prompt, "stream": False}
    response = requests.post(
        "http://localhost:11434/api/generate",
        json=payload
    )
    return response.json()["response"]
print(LLM("你是谁？"))