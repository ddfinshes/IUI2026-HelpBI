from models.llm_deepseck import DeepSeek_Coder_LLM

def get_llm():
    llm = DeepSeek_Coder_LLM(mode_name_or_path = "/root/UIST2025/Ex-ChatBI/deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct")
    # llm = get_llm()
    return llm

# 
# print(llm("你是谁？"))

# line_template = '\t"{name}": {type} '