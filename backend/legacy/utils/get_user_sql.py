from typing import Dict, Any
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
import os, json, uuid
import re
import pandas as pd
class SQLExtractAgent:
    def __init__(self, model_name: str = "o3-mini", temperature: float = 0.3):
        self.llm = ChatOpenAI(
            model=model_name, 
            temperature=temperature,
            api_key="sk-dHMDhf5KdHlpA0XOE2Bd778f95C84431966d340fFdE56a26",
            base_url="https://ai-yyds.com/v1"
            )
        self.prompt = """
            ## Task Description
            You are tasked with extracting a subset of SQL code from a provided original SQL query. The goal is to create a new SQL query that retrieves specific data based on user interaction in a frontend interface. The user will provide:
            1. Original SQL Query: A complete SQL query (which may include Common Table Expressions, or CTEs) that generates a dataset.
            2. Query Output Data: The resulting data from the SQL query, presented as a table (e.g., in JSON format with column names and rows).
            3.User Click Information: Details about what the user clicked in the frontend interface, which will be one of the following:
                    - Cell Click: {value: cellValue, rowIndex: rowIndex, columnName: columnName} (e.g., a specific value in a row and column).
                    - Row Click: {rowData: row, rowIndex: rowIndex} (e.g., an entire row of data).
                    - Column Click: {columnName: column, columnIndex: columnIndex} (e.g., an entire column)
                Your task is to generate a new SQL query by only deleting parts of the original SQL code—no modifications or additions to the existing statements are allowed. The extracted SQL must be valid and capable of querying the data the user has selected.
                ## User Input
                You will receive the following inputs:
                1. Original SQL Code: A complete SQL query (e.g., containing SELECT, FROM, WHERE, GROUP BY, etc.). Sometimes the SQL code contains CTE sql code. CTE 
                Your goal is to extract a subset of the original SQL query that corresponds to the user's clicked data. The extracted SQL must:
                    - Be derived solely by deleting parts of the original SQL (no modifications or additions allowed).
                    - Remain syntactically correct and executable.
                    - Return data relevant to the user's click (e.g., the specific cell, row, or column).
            ## Input Details
            1.Original SQL Query: A valid SQL statement (e.g., containing SELECT, FROM, WHERE, GROUP BY, and possibly CTEs).
            2.Query Output Data: A table-like structure showing the results (e.g., JSON with "column" for column names and "data" for rows).
            3.User Click Information: One of the following:
                - Cell Click: {value: <clicked_value>, rowIndex: <row_number>, columnName: <column_name>}
                - Row Click: {rowData: <entire_row_data>, rowIndex: <row_number>}
                - Column Click: {columnName: <column_name>, columnIndex: <column_number>}
            ## Requirements
            1. Understand the User Click:
                - Cell Click: Extract SQL related to the specific row and column of the clicked cell.
                - Row Click: Extract SQL that retrieves data for the entire clicked row.
                - Column Click: Extract SQL that retrieves data for the entire clicked column.
            2. Handle CTEs (if present):
                - Retain only the CTEs necessary for the extracted SQL to function.
                - Delete any CTEs that are unrelated to the clicked data.
            3. Extraction Rules:
                - Only delete parts of the original SQL—no edits or additions are allowed.
                - Retain essential clauses (SELECT, FROM, WHERE, GROUP BY, etc.) to ensure the extracted SQL is valid and retrieves the relevant data.
                - For cell or row clicks, include filters (e.g., WHERE conditions) that isolate the specific row’s data.
                -For column clicks, include only the clicked column’s definition or computation from the SELECT clause.
            4. Output Format:
                - Provide the extracted SQL as a standalone, executable query.
                - Ensure proper SQL syntax and formatting (e.g., end with a semicolon if present in the original).
            ## Steps to Complete the Task
            1. Parse the User Click Information:
                - Identify whether the click is on a cell, row, or column.
                - Extract the clicked value, row index, or column name as provided.
            2. Analyze the Original SQL Query:
                - Break down the SQL into its components: WITH (CTEs), SELECT, FROM, WHERE, GROUP BY, etc.
                - If CTEs exist, determine their dependencies and usage in the main query.
            3. Determine Relevant SQL Parts:
                - Cell Click: Identify the row’s filtering condition (e.g., WHERE column = value) and the clicked column in SELECT.
                - Row Click: Identify the row’s filtering condition and retain all columns in SELECT relevant to that row.
                - Column Click: Identify the clicked column’s definition in SELECT and retain necessary supporting clauses.
            4. Extract the SQL:
                - Delete irrelevant columns from SELECT (except for grouping keys if applicable).
                - Delete unrelated WHERE conditions or CTEs not required for the clicked data.
                - Retain necessary structural elements (e.g., FROM, GROUP BY) for the query to run.
            5. Validate the Output:
                - Confirm the extracted SQL is syntactically correct.
                - Verify it produces data matching the user’s click (e.g., the cell value, row, or column).
            ## Example
            ***input***
            1. Original SQL Query:
            ```sql
            WITH sales_data AS (
                SELECT month_id, amt, amt_notax, lm_amt_notax
                FROM dm_fact_sales_chatbi
                WHERE date_code BETWEEN '2025-02-01' AND '2025-02-10'
            )
            SELECT 
                month_id,
                SUM(amt) AS sales_amt,  
                SUM(amt_notax) AS sales_notax, 
                SUM(amt_notax) / SUM(lm_amt_notax) - 1 AS sales_notax_mom_per   
            FROM 
                sales_data
            GROUP BY 
                month_id;
            ```
            2. Query Output Data:
            ```json
            {
            "column": ["month_id", "sales_amt", "sales_notax", "sales_notax_mom_per"],
            "data": [[202502, -5235, -4634, -1.00029011188026305147]]
            }
            ```
            3. User Click Information:
            ```json
            {
            "value": 202502,
            "rowIndex": 0,
            "columnName": "month_id"
            }
            ```
            Task: Extract SQL for the clicked cell (month_id = 202502).
            ***Output (Extracted SQL):***
            ```sql
            WITH sales_data AS (
                SELECT month_id
                FROM dm_fact_sales_chatbi
                WHERE date_code BETWEEN '2025-02-01' AND '2025-02-10'
            )
            SELECT 
                month_id
            FROM 
                sales_data
            GROUP BY 
                month_id;
            ```
            ### Explanation:
            - The click targets the month_id column in row 0 (value 202502).
            - Retained month_id in SELECT and the CTE, deleted other columns (amt, amt_notax, etc.).
            - Kept the WHERE condition and GROUP BY to ensure the query isolates the relevant row.
            ## Additional Notes
            - CTEs: If multiple CTEs exist, retain only those referenced by the extracted main query.
            - Row Clicks: May require keeping all SELECT columns unless specified otherwise, but filter to the clicked row.
            - Column Clicks: Focus solely on the clicked column’s logic, deleting other computations.
        """

        self.memory = MemorySaver()
        self.agent = create_react_agent(self.llm, tools=[], prompt=self.prompt, checkpointer=self.memory)
        self.config = {"configurable": {"thread_id": uuid.uuid4()}}
    
    def run(self, sql_query: Dict[str, Any], query_out: Dict[str, Any], click_info: Dict[str, Any]):
        query = f"""
            Original SQL Query:
            {sql_query}
            Query Output Data:
            {query_out}
            User Click Information:
            {click_info}
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
        """Get the last analysis report"""
        state = self.agent.get_state(self.config).values
        print("state: ",state)

        report = state["messages"][-1].content.strip('```sql\n').strip('```')

        return report

