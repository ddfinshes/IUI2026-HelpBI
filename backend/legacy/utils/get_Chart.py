from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver

import os, json, uuid
import pandas as pd
from typing import Dict, Any
import json

class VisAgent:
    def __init__(self, model_name: str = "o3-mini"):
        self.llm = ChatOpenAI(
            model=model_name, 
            api_key="sk-rzf6y244hnAJPxUE5eA02e5bA4Dd4098A3C21f96CeCe7a6f",
            base_url="https://ai-yyds.com/v1"
            )
        self.prompt = """
            You are a seasoned business data analyst and need to process visualization recommendation requests according to the following rules:
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
            4. Outlier handling, if there is a value in the x or y axis data that cannot be visualized, please handle it as a value that can be visualized normally, e.g. for 'None' please handle the value as 0.

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

        
        self.memory = MemorySaver()
        self.agent = create_react_agent(self.llm, tools=[], prompt=self.prompt, checkpointer=self.memory)

        self.config = {"configurable": {"thread_id": uuid.uuid4()}}

    def run(self, usr_input: Dict[str, Any]):
        """Run the agent"""
        query = f"""
            User Input:
            {usr_input}
            """

        input_message = HumanMessage(content=query)
            
        for event in self.agent.stream({"messages": [input_message]}, self.config, stream_mode="values"):
            if (event["messages"][-1].type == "human"):
                continue
            event["messages"][-1].pretty_print()
    def getHistory(self):
        """Get the conversation history"""
        state = self.agent.get_state(self.config).values

        for message in state["messages"]:
            message.pretty_print()
    def getLeastAnalysisReport(self):
        """Get the last visual design report"""
        
        state = self.agent.get_state(self.config).values
        report = json.loads(state["messages"][-1].content.strip('```json\n').strip('```'))
        
        return report
