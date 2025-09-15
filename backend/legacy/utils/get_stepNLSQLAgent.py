from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver

import os, json, uuid
import pandas as pd
from typing import Dict, Any
import json

class StepNLAgent:
    def __init__(self, model_name: str = "o3-mini"):
        self.llm = ChatOpenAI(
            model=model_name, 
            api_key="sk-rzf6y244hnAJPxUE5eA02e5bA4Dd4098A3C21f96CeCe7a6f",
            base_url="https://ai-yyds.com/v1"
            )
        self.prompt = """
            You are a skilled data analysis expert with deep knowledge of SQL (PostgreSQL) logic and its application in business contexts. Your task is to explain SQL code in simple, clear natural language for business users who don’t understand SQL, helping them grasp the processing logic step-by-step.
            ## Input
            You will receive:
            1. sql_code: A string of SQL code to explain.
            2. sql_json: A JSON string containing parsed SQL details, including a 'NL Explain' field paired with sub-SQL code snippets.

            ## Processing Logic
            1. Extract the 'NL Explain' text and its corresponding sub-SQL code from sql_json (e.g., { "SUM(amt_notax) AS curr_sales": "calculates the sum of the amt_notax column as current sales" }).
            2. Break down the sql_code into logical steps using a step-by-step format.
            3. For each step related to an 'NL Explain' entry, reference the sub-SQL code using the format ref: {'sub-SQL code'}.
            4. End with a concise 'Simple Logic' summary in plain language.

            ## Output Format
            Output in JSON with:
            - 'data': A list of steps, each with:
                - 'descripe': A clear step description.
                - 'ref': A list of sub-SQL snippets (if applicable, else empty).
            - 'Simple Logic': One to three sentences summary of the SQL’s purpose.

            ## Input Example
            sql_code:
                "SELECT 
                    SUM(amt_notax) AS curr_sales
                FROM 
                    dm_fact_sales_chatbi
                WHERE 
                    date_code BETWEEN '2025-02-16' AND '2025-02-19'
                    AND comp_flag = 'Y'"
            sql_json:
                {
                "sql_content": [
                    {
                    "keywords": "Select",
                    "scratched_content": [
                        {
                        "column_name": "curr_sales",
                        "column_processing": "SUM(amt_notax) AS curr_sales",
                        "NL Explain": "calculates the sum of the amt_notax column as current sales"
                        }
                    ]
                    },
                    ...
                ]
                }

            ## Output Example
            ```json
            {
            "data": [
                {
                "descripe": "1. Pick the Data Source: Use a table called dm_fact_sales_chatbi, like a spreadsheet of sales data.",
                "ref": ["FROM dm_fact_sales_chatbi"]
                },
                {
                "descripe": "2. Calculate the Total: Add up all values in the amt_notax column (sales without tax) and name the result curr_sales.",
                "ref": ["SUM(amt_notax) AS curr_sales"]
                },
                {
                "descripe": "3. Filter by Date: Only include sales from February 16 to February 19, 2025.",
                "ref": ["date_code BETWEEN '2025-02-16' AND '2025-02-19'"]
                },
                {
                "descripe": "4. Filter by Status: Only include sales marked as completed (comp_flag = 'Y').",
                "ref": ["comp_flag = 'Y'"]
                },
                ...
            ],
            "Simple Logic": "From the sales table, sum the sales amounts without tax for completed sales between Feb 16-19, 2025, and show the total as curr_sales."
            }
            ```
            """
        self.memory = MemorySaver()
        self.agent = create_react_agent(self.llm, tools=[], prompt=self.prompt, checkpointer=self.memory)

        self.config = {"configurable": {"thread_id": uuid.uuid4()}}

    def run(self, usr_input: Dict[str, Any]):
        # sql_query, sql_json, nl_ex, nl_sql
        sql_query = usr_input['sql_code']
        sql_json = usr_input['sql_json']
        """Run the agent"""
        query = f"""
            sql_code:
            {sql_query}
            
            sql_json:
            {sql_json}
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


        