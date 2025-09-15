# llm_wrapper.py
from openai import OpenAI

class LLM:
    def __init__(self, api_key="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", base_url="https://openrouter.ai/api/v1", model="deepseek/deepseek-r1:free"):
        self.client = OpenAI(base_url=base_url, api_key=api_key)
        self.model = model
 

    def __call__(self, query):
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": query
                }
            ]
        )
        # return completion.choices[0].message.content
        try:
            print(completion.choices[0].message.content)
            return completion.choices[0].message.content
        except Exception as e:
            print(e)
            # print("Time out")
# llm = LLM()
# print(llm("What is the meaning of life?"))