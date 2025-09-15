from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver

import os, json, uuid
import pandas as pd
from typing import Dict, Any
import json

class ModifyAgent:
    def __init__(self, model_name: str = "o3-mini"):
        self.llm = ChatOpenAI(
            model=model_name, 
            api_key="sk-dHMDhf5KdHlpA0XOE2Bd778f95C84431966d340fFdE56a26",
            base_url="https://ai-yyds.com/v1"
            )
        self.prompt = """
            Please act as a database expert, highly skilled in writing SQL code (especially PostgreSQL). You are now tasked with completing an SQL code modification assignment. The user will provide the following information:

            1. Complete Original SQL Code: The full SQL statement or code block that needs modification.
            2. Small Segment of SQL Code to Modify: A specific excerpt from the complete code that requires adjustment.
            3. Modification Instructions: Directions on how this small segment of SQL code should be modified. A natural language explanation that the modified small segment of SQL should conform to, i.e., the SQL modification instructions.

            You task to:
            - Understand the complete code and the target segment provided by the user.
            - Adjust the specified small segment of SQL code according to the modification instructions.
            - Ensure the modified code remains fully compatible with the original code and adheres to PostgreSQL syntax and best practices.
            - Finally, return the modified complete SQL code.
            - Please proceed with the task based on the user’s input!

            Output Format:
            ```sql
             select xxx ...
            ```
        """
        self.memory = MemorySaver()
        self.agent = create_react_agent(self.llm, tools=[], prompt=self.prompt, checkpointer=self.memory)

        self.config = {"configurable": {"thread_id": uuid.uuid4()}}

    def run(self, usr_input: Dict[str, Any]):
        # sql_query, sql_json, nl_ex, nl_sql
        sql_query = usr_input['sql_query']
        nl_ex = usr_input['nl_ex']
        nl_sql = usr_input['nl_sql']
        """Run the agent"""
        query = f"""
            Complete Original SQL Code:
            {sql_query}
            Small Segment of SQL Code to Modify:
            {nl_sql}
            Modification Instructions:
            {nl_ex}
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
        report = json.loads(state["messages"][-1].content.strip('```sql\n').strip('```'))
        return report

