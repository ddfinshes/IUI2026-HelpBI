# langchain_deepseek_coder.ipynb [1]
from langchain.llms.base import LLM
from typing import Any, List, Optional
from langchain.callbacks.manager import CallbackManagerForLLMRun
from transformers import AutoTokenizer, AutoModelForCausalLM, GenerationConfig, LlamaTokenizerFast
import torch

class DeepSeek_Coder_LLM(LLM):  # 定义一个继承自LLM的DeepSeek_Coder_LLM类
    # 类变量，初始化为None，将在初始化方法中被赋值
    tokenizer: AutoTokenizer = None
    model: AutoModelForCausalLM = None
        
    def __init__(self, mode_name_or_path: str):  # 初始化方法，接受模型路径或名称作为参数

        super().__init__()  # 调用父类的初始化方法
        print("正在从本地加载模型...")  # 打印加载模型的提示信息
        # 使用AutoTokenizer从预训练模型加载分词器
        self.tokenizer = AutoTokenizer.from_pretrained(mode_name_or_path, use_fast=False, trust_remote_code=True)
        # 使用AutoModelForCausalLM从预训练模型加载语言模型
        self.model = AutoModelForCausalLM.from_pretrained(
            mode_name_or_path,
            torch_dtype=torch.bfloat16,  # 设置PyTorch数据类型为bfloat16
            device_map="auto",  # 让模型自动选择设备
            trust_remote_code=True  # 信任远程代码
        )
        # 从预训练模型加载生成配置
        self.model.generation_config = GenerationConfig.from_pretrained(mode_name_or_path)
        print("完成本地模型的加载")  # 打印模型加载完成的提示信息
        
    def _call(self, prompt: str, stop: Optional[List[str]] = None,
               run_manager: Optional[CallbackManagerForLLMRun] = None,
               **kwargs: Any):  # 定义_call方法，用于生成文本

        messages = [{"role": "user", "content": prompt }]  # 定义消息列表，包含用户的角色和内容
        # 应用聊天模板，生成输入ID
        input_ids = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        # 将输入ID转换为模型需要的输入格式，并转换为PyTorch张量
        model_inputs = self.tokenizer([input_ids], return_tensors="pt").to('cuda')
        # 使用模型生成文本，设置生成参数
        generated_ids = self.model.generate(
            model_inputs.input_ids,
            max_new_tokens=512,  # 最大新生成的token数
            top_k=5,  # 每次采样的token数
            top_p=0.8,  # 按概率分布采样
            temperature=0.3,  # 温度参数，影响生成文本的随机性
            repetition_penalty=1.1,  # 重复惩罚，避免重复生成相同的文本
            do_sample=True  # 是否使用采样
        )
        # 从生成的ID中提取实际生成的文本ID
        generated_ids = [
            output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]
        # 将生成的ID解码为文本，并跳过特殊token
        response = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
        return response  # 返回生成的文本

    @property
    def _llm_type(self) -> str:  # 定义一个属性，返回模型的类型
        return "DeepSeek_Coder_LLM"