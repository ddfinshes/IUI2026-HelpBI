from openai import OpenAI
def analyze_relation(understanding : str, knowledge_base : list):
    client = OpenAI(
        # base_url='https://api.nuwaapi.com/v1',
        # api_key='sk-3El3h3N2q539ah6ofrqA1vQTm8iudtnQUQzhp9SsTltxeFNk'
        base_url = 'https://ai-yyds.com/v1',
        api_key = 'sk-rzf6y244hnAJPxUE5eA02e5bA4Dd4098A3C21f96CeCe7a6f'
    )

    result = []
    for i in range(len(knowledge_base)):
        result.append([])
        for j in range(len(knowledge_base[i])):
            # print(knowledge_base[i][j])
            kb = knowledge_base[i][j]
            
            # if j == 0:
            #     kb = knowledge_base[i][j].split("**SQL query sample**:")[0]
            # else:
            #     kb = knowledge_base[i][j]
            # if kb == '':
            #     result[i].append('none')
            #     continue
            prompt = f'''
            You need to complete a data statement matching and alignment task.

            I will provide you with two sentences. Please follow the process below to evaluate the two sentences:

            Identify and label which word or words in the first sentence are specialized terms that need explanation.

            Determine whether the second sentence provides an explanation for the terms in the first sentence.

            If an explanation is provided, label which parts of the second sentence contain the explanation.(you may label only a few words)
            Your response should follow the format below:
            - If there is no relevance, answer "none".
            - If there is relevance, first state the term(s), and in the next line, provide the part of the sentence that explains it. Do not include any additional content in your response!
            Please notice that, only when there's strong relation between two sentences should you reply content, or you reply none!!!!! 
            To support subsequent string matching tasks, the output matching content must be consistent with the input text content, and no modifications to punctuation, capitalization, or any other content are allowed.
            
            first sentence: {understanding}
            second sentence: {kb}'''
            response = client.chat.completions.create(
                # model="deepseek-chat",
                model = 'o3-mini', 
                messages=[
                    {"role": "system", "content": "You are an expert in data analysis"},
                    {"role": "user", "content": prompt},
                ],
                stream=False
            )
            result[i].append(response.choices[0].message.content)
    return result


# def analyze_relation(understanding : str, knowledge_base : list):
#     client = OpenAI(
#         # base_url='https://api.nuwaapi.com/v1',
#         # api_key='sk-3El3h3N2q539ah6ofrqA1vQTm8iudtnQUQzhp9SsTltxeFNk'
#         base_url = 'https://ai-yyds.com/v1',
#         api_key = 'sk-rzf6y244hnAJPxUE5eA02e5bA4Dd4098A3C21f96CeCe7a6f'
#     )
#     nknowledge_base = [[] for i in range(len(knowledge_base))]
#     for i in range(len(knowledge_base)):
#         for j in range(2):
#             # print(knowledge_base[i][j])
            
#             if j == 0:
#                 kb = knowledge_base[i][j].split("**SQL query sample**:")[0]
#             else:
#                 kb = knowledge_base[i][j]
#             nknowledge_base[i].append(kb)


#     result = ''
#     prompt = """
#             You are tasked with a text-matching assignment. The user will provide you with two inputs:
#             1. A piece of text called "first sentence" (a single string).
#             2. An array called "knowledge-base" (a list of text elements).

#             Your task:
#             - Match "first sentence" and "knowledge-base"'s each elements (i.e. knowledge-base[i][j]). Identify and label which word or words in "first sentence" are specialized terms that need explanation. Determine whether the "knowledge-base"'s word or words provides an explanation for the terms in the "first sentence".
#             - The output must be the subtexts of the "first sentence" and the "knowledge-base", and cannot be modified in any way.

#             Your response must follow this format:
#             - If no matches are found, return the word "None" (without quotes).
#             - If matches are found, return a JSON object in the following structure:
#             ```json
#                     {
#                     "pair": [
#                         {
#                         "mu": "weekly comp growth % for sales",
#                         "kb": "Query the sales growth in a certain week" ////It’s not the entire content of `knowledge-base[i][j]`, but a small portion that closely matches “weekly comp growth % for sales”.
#                         "index": 1 //// text in the i-th array in knowledge-base (knowledge_base[i][j]).
#                         },
#                         {
#                         "mu": "weekly comp growth % for sales",
#                         "kb": "The comparison formula is: sales amount of this week / sales amount of last week - 1, and it is displayed as a percentage with two decimal places."
#                         "index": 1 //// text in the i-th array in knowledge-base (knowledge_base[i][j]).
#                         },
#                         {
#                         "mu": "WTd",
#                         "kb": "WTD: From the first day (Sunday) of the current week to yesterday."
#                         "index": 3
#                         },
#                         {
#                         "mu": "<text from first sentence>",
#                         "kb": "<matching text from knowledge-base>",
#                         "index": 2
#                         },
#                         ...
#                         ]
#                     }
#             ```
#             - Each "mu" field should contain the relevant word or words from "first sentence."
#             - Each "kb" field should contain the corresponding matching text from "knowledge-base."
#             - Include as many pairs as necessary to reflect all identified matches.
#             Ensure your analysis is based on semantic similarity or conceptual explanation, not just exact word matches, unless the context implies otherwise.
#         """
#     user_input = f"""\nUser's Input:
#             moder-understanding: {understanding},
#             knowledge-base: {nknowledge_base}
#     """
#     prompt = prompt + user_input

#     response = client.chat.completions.create(
#         # model="deepseek-chat",
#         model = 'o3-mini', 
#         messages=[
#             {"role": "system", "content": "You are an expert in data analysis"},
#             {"role": "user", "content": prompt},
#         ],
#         stream=False
#     )
#     result = response.choices[0].message.content
    
#     return result
