from math import dist
import os
from openai import OpenAI
from typing import List, Dict, Any, Optional


class ChatModel:
    """大模型聊天接口封装类"""
    
    def __init__(self, api_key: str = None, base_url: str = None):
        """
        初始化聊天模型客户端
        
        Args:
            api_key: API密钥，如果不提供则使用默认值
            base_url: API基础URL，如果不提供则使用默认值
        """
        self.api_key = api_key or "sk-de225921dd58479887c1f14d8249b337"
        self.base_url = base_url or "https://dashscope.aliyuncs.com/compatible-mode/v1"
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
        )
    
    def chat(self,  messages: List[Dict[str, Any]], model: str="qwen3-235b-a22b",
             enable_thinking: bool = False, **kwargs) -> str:
        """
        调用大模型进行聊天
        
        Args:
            model: 模型名称
            messages: 消息列表，格式为 [{'role': 'user', 'content': '...'}, ...]
            enable_thinking: 是否开启思考模式
            **kwargs: 其他参数
            
        Returns:
            str: 模型返回的文本内容
            
        Raises:
            Exception: 当API调用失败时抛出异常
        """
        try:
            completion = self.client.chat.completions.create(
                model=model,
                messages=messages,
                # 显式关闭思考模式并使用非流式，兼容部分兼容模式服务
                extra_body={"enable_thinking": False},
                stream=False,
                **kwargs
            )
            return completion.choices[0].message.content
        except Exception as e:
            raise Exception(f"大模型调用失败: {str(e)}")
    
    def chat_with_system(self, system_prompt: str, user_message: str, model: str="qwen3-235b-a22b", 
                        enable_thinking: bool = False, **kwargs) -> str:
        """
        带系统提示的聊天方法
        
        Args:
            model: 模型名称
            system_prompt: 系统提示词
            user_message: 用户消息
            enable_thinking: 是否开启思考模式
            **kwargs: 其他参数
            
        Returns:
            str: 模型返回的文本内容
        """
        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_message}
        ]
        return self.chat(messages, model, enable_thinking, **kwargs)


    def my_embedding(self, input: List[str], model: str="text-embedding-v4"):
        completion = self.client.embeddings.create(
            model=model,
            input=input,
            dimensions=1024,
            encoding_format="float"
        )
        return completion.model_dump_json()

# 使用示例
if __name__ == "__main__":
    # 创建聊天模型实例
    chat_model = ChatModel()
    
    # 方式1：直接使用chat方法
    messages = [
        {'role': 'system', 'content': 'You are a helpful assistant.'},
        {'role': 'user', 'content': '你是谁？'}
    ]
    response = chat_model.chat(messages)
    print("方式1响应:", response)
    
    # 方式2：使用chat_with_system方法
    response2 = chat_model.chat_with_system(
        system_prompt="You are a helpful assistant.",
        user_message="你是谁？"
    )
    print("方式2响应:", response2)