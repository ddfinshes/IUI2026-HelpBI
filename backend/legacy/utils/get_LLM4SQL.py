from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver

import os, json, uuid
import pandas as pd
from typing import Dict, Any
import json

class SQLCodeAgent:
    def __init__(self, model_name: str = "o3-mini"):
        self.llm = ChatOpenAI(
            model=model_name, 
            api_key="sk-rzf6y244hnAJPxUE5eA02e5bA4Dd4098A3C21f96CeCe7a6f",
            base_url="https://ai-yyds.com/v1"
            )
        self.prompt = """
            You are a data analysis expert highly skilled in writing correct SQL code (PostgreSQL) based on user questions. You will be provided with the user's question, a library of business concepts (business_chunks), a library of SQL examples (sql_chunks), and possibly database schema information for relevant tables.

            ### Your Task:
            1. Understand the User's Question and Align with Business Concepts:
            - Analyze the user's question to identify key terms or phrases that need clarification or definitions.
            - Search the provided business concept library (business_chunks) for the exact definitions or explanations of these terms.

            2. Learn from Similar SQL Examples:
            - Examine the provided SQL example library (sql_chunks) to locate examples that closely resemble the user's question.
            - Extract the parts of these examples that are relevant to solving the user's question.
            
            3. Generate Executable SQL Code:
            - Using the insights from Steps 1 and 2, and referencing the provided database schema information, write a clear, executable PostgreSQL query that precisely answers the user's question.
            - Ensure the SQL code is syntactically correct, logically accurate, and tailored to the schema.
            
            ### Important Date Handling Instructions:
            - Assume today is Thursday, February 20, 2025, and the current weekid is 202545 (week 45).
            - For week-based date restrictions (e.g., "WTD" or "last week"), excluding specific weekids (e.g., "week 45"), convert these terms into explicit date ranges based on the current date. Do not use PostgreSQL built-in date functions for these conversions.
                - Example: If the user asks for "WTD: From Sunday of this week to yesterday," use the date range February 16, 2025, to February 19, 2025.
            - For specific weekids (e.g., "week 45"), include the condition weekid = 202545 directly in the SQL query.
            
            ### Output Format:
            - Your response must be a JSON object with the following structure:]
            ```json
            "Give User Answer": {
                "Model Understanding": "Your detailed understanding of the user's question and the step-by-step analysis flow to solve it.",
                "SQL Code": "```sql\n-- Your executable PostgreSQL code here\n```",
                "Explanation": "A clear explanation of the SQL output to help business users understand the results and why this SQL was generated."
            }
            ```

            **Additional Instructions:**

            - In the "Model Understanding Align" section, map the exact phrases or terms from the "Model Understanding" to their corresponding definitions in business_chunks and relevant text in sql_chunks.
            - Ensure the text in this section is identical to what appears in "Model Understanding" (no modifications) to enable exact string matching for further processing.
            - All text extracted from business_chunks and sql_chunks must remain unchanged in the output.


            ### Example:

            #### User Input Example:
            "This month's weekly comp growth % for sales."

            #### Output Example:
            ```json
            {
                
                "Give User Answer": {
                    "Model Understanding": "The user wants to calculate the weekly comparable growth percentage for sales during the current month, February 2025. This requires comparing this year's sales to last year's sales for the same weeks, aggregating the data by week, and restricting the data to the month of February 2025.",
                    "SQL Code": "```sql\nSELECT \n    week_id,\n    SUM(amt) as sales_amt,\n    SUM(amt_notax) as sales_notax,\n    SUM(amt_notax) / SUM(lyd_amt_notax) - 1 as sales_comp_per\nFROM \n    dm_fact_sales_chatbi\nWHERE \n    date_code BETWEEN '2025-02-01' AND '2025-02-28'\n    AND comp_flag = 'Y' -- The store participating in the comp.\nGROUP BY \n    week_id;\n```",
                    "Explanation": "This SQL query computes the weekly comparable sales growth percentage for February 2025. It groups sales data by week_id, sums the sales amounts (with and without tax), and calculates the growth percentage by comparing this year's non-tax sales (amt_notax) to last year's non-tax sales (lyd_amt_notax) for comparable stores (comp_flag = 'Y'). The date range limits the data to February 2025."
                },
                
            }
            ```
        """

        
        self.memory = MemorySaver()
        self.agent = create_react_agent(self.llm, tools=[], prompt=self.prompt, checkpointer=self.memory)

        self.config = {"configurable": {"thread_id": uuid.uuid4()}}

    def run(self, usr_input: Dict[str, Any]):
        """Run the agent"""
        query = f"""
            User Qestion:
            {usr_input['user_question']}

            Business_Chunks:
            {usr_input['business_chunks']}
            SQL_Chunks:
            {usr_input['sql_chunks']}
            DB Schema:
            {usr_input['db_schema']}
            Conversation History:
            {usr_input['history']}
            {usr_input['revised_knowledge']}
            {usr_input['revised_understanding']}
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

"""
"Question Align": 
{
    "business_chunks_align": [
    {
        "keywords": "WTD",
        "explain": "WTD: From the first day (Sunday) of the current week to yesterday."
    },
    {
        "keywords": "CN",
        "explain": "CN: Refers to mainland China, country=mainland in Database."
    }
    ],
    "sql_chunks_align": [
    {
        "question text": "weekly comp growth % for sales",
        "close information": "Weekly comp growth % for sales / traffic / CR / AOV / ASP / UPT."
    }
    ]
},
"Model Understanding Align": {
    "business_chunks_align": [
    {
        "words": "weekly comparable growth percentage",
        "explain": "Weekly comp growth % for sales / traffic / CR / AOV / ASP / UPT."
    }
    ],
    "sql_chunks_align": [
    {
        "question text": "weekly comp growth % for sales",
        "close information": "Weekly comp growth % for sales / traffic / CR / AOV / ASP / UPT."
    }
    ]
}

"""