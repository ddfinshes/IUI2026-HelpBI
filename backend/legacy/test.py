from crag import CRAG
crag_instance = CRAG(
    path="/root/UIST2025/Ex-ChatBI/backend/knowledge-base/test.pdf",
    model="DeepSeek-Coder-V2-Lite-Instruct",
    max_tokens=1000,
    temperature=0.5,
    lower_threshold=0.3,
    upper_threshold=0.7
)
rag_response = crag_instance.run("查询某时间范围内的某些店铺的销售金额，并且计算去年同比/上月环比/上周环比/前日环比的数值")