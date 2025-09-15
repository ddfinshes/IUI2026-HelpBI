# from .get_llm_deepseek import LLM
from .get_llm import llm
import json
from decimal import Decimal
def convert_decimal(obj):
    if isinstance(obj, Decimal):
        return float(obj)  # 或者使用 str(obj) 转换为字符串
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

def get_vis_tag(user_query, excute_sql_output):
    prompt_system = """
        You are a seasoned business data analyst and need to process visualization recommendation requests according to the following rules:
    """
    prompt_user = """
            # Task Description
            1. The user will provide a question description and corresponding structured data (including column names and data rows).
            2. Based on the question and data, determine the most suitable visualization type from the following options:
            - **Bar chart**: Use for comparing categories (≤6 distinct categories) or discrete time series data.
            - **Line chart**: Use for showing trends over continuous time (≥3 time points) or continuous variable changes.
            - **Pie chart**: Use for displaying proportions of a whole (3-5 categories).
            3. Identify the appropriate data fields for:
            - **x-axis**: Data suitable as the horizontal axis (e.g., categories, time points).
            - **y-axis**: Data suitable as the vertical axis (e.g., numerical values).
            - **title**: A concise chart title derived from the question and data.
            - **x-legend**: Label for the x-axis.
            - **y-legend**: Label for the y-axis.
            - **tooltip**: Additional data to display on hover for context (e.g., related metrics or percentages).

            # Input Data Format
            The input will be a JSON object with:
            - `"question"`: A string describing the analysis goal.
            - `"data"`: An object with:
            - `"columns"`: List of column names (e.g., `["month_id", "sales_amt"]`).
            - `"data"`: List of tuples, each representing a row of data (e.g., `[(202502, -5235)]`).

            ### Example Input
            ```json
            {
            "question": "What is the sales MOM% \for APAC EC?",
            "data": {
                "columns": ["month_id", "sales_amt", "sales_notax", "sales_notax_mom_per"],
                "data": [[202502, -5235, -4634, -1.00029011188026305147]]
            }
            ```

            # Processing Requirements
            1. Select exactly one visualization type (bar-chart, line-chart, or pie-chart) based on the data and question:
                - Verify the data meets the conditions for the chosen type (e.g., number of categories, time points).
                - If no type is suitable, default to bar-chart.
            2. Assign data fields to:
                - "x": List of values or column names for the x-axis.
                - "y": List of numerical values for the y-axis.
                - "title": A string summarizing the chart's purpose.
                - "x-legend": A string describing the x-axis.
                - "y-legend": A string describing the y-axis.
                - "tooltip": A string with additional data (e.g., a column name and value).
            3. Output must be a pure JSON object with no additional text or explanations.
            # Output Format
            ```json
            {
                "vis_tag": "string", // One of: "bar-chart", "line-chart", "pie-chart"
                "x": [], // Array of x-axis data (values or column names)
                "y": [], // Array of y-axis numerical data
                "title": "string", // Chart title
                "x-legend": "string", // x-axis label
                "y-legend": "string", // y-axis label
                "tooltip": "string" // Additional data for hover display
            }
            ```
            ### Example Output
            ```json
            {
                "vis_tag": "bar-chart",
                "x": ["sales_amt", "sales_notax"],
                "y": [-5235, -4634],
                "title": "Sales for APAC EC in Month 202502",
                "x-legend": "Sales Type",
                "y-legend": "Amount",
                "tooltip": "sales_notax_mom_per: -1.000290111880263"
            }
            ```
        }\n
        """
    user_inpt = {
        "question": user_query,
        "data": json.dumps(excute_sql_output, default=convert_decimal)
    }
    prompt_user += "# User Input\n"
    prompt_user += f"""
            ```json
            {user_inpt}
            ```
    """   
    prompt = [
        {"role": "system", "content": prompt_system},
        # {"role": "assistant", "content": prompt_assistant},
        {"role": "user", "content": prompt_user}
    ]
    response = llm(model_name="gpt", messages=prompt)
    response = json.loads(response)
    print(type(response))
    if response is None:
        print("===============================LLM GET VIS TAG ==============================",response)
    print("==========================Chart Data==================", response)
    return response
user_query = "What is the sales MOM% for APAC EC?"
sql_code = {'column': ['month_id', 'sales_amt', 'sales_notax', 'sales_notax_mom_per'], 'data': [[202502, '-5235', '-4634', '-1.00029011188026305147']]}
get_vis_tag(user_query=user_query, excute_sql_output=sql_code)