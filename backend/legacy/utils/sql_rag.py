from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver

import os, json, uuid
import pandas as pd
from typing import Dict, Any
import json

class SQLRAGAgent:
    def __init__(self, model_name: str = "o3-mini"):
        self.llm = ChatOpenAI(
            model=model_name, 
            api_key="sk-rzf6y244hnAJPxUE5eA02e5bA4Dd4098A3C21f96CeCe7a6f",
            base_url="https://ai-yyds.com/v1"
            )
        self.prompt = """
            You are a highly skilled data analysis expert with extensive experience in categorizing and interpreting user queries. Your task is to classify a user’s input query into one or more predefined categories (labeled ID1 to ID52) based on its content and intent. Each category has a unique identifier (e.g., ID1, ID32.1, ID29), a description explaining the type of query it represents, and sample questions illustrating typical examples.

            Here’s an example of a category’s structure:
            ```text
            ### ID1  **Description**:  
            Query the achievement rate of sales within a certain period of time. The formula for the sales achievement rate is: sales amount / target sales amount - 1, displayed as a percentage with two decimal places.  

            **Question Sample**:  
            - "WTD / MTD / QTD / YTD sales vs Target?"  
            - "What is the MTD sales achievement for China FP?"  
            - "WTD / MTD / QTD / YTD sales vs F1 (target)?" (This means the target uses the F1 target.)"
            ```

            For any given user query, analyze its meaning and match it to the most relevant categories (up to the 4 closest matches). Return your classification in the following JSON format:
            ```json
            {
            "Align Data": [
                {
                "ID": "ID1",
                "Content": "### ID1  **Description**:  Query the achievement rate of sales within a certain period of time. The formula for the sales achievement rate is: sales amount / target sales amount - 1, displayed as a percentage with two decimal places.  **Question Sample**:  - "WTD / MTD / QTD / YTD sales vs Target?"  - "What is the MTD sales achievement for China FP?"   - "WTD / MTD / QTD / YTD sales vs F1 (target)?" (This means the target uses the F1 target.)""
                },
                {
                "ID": "ID32.1",
                "Content": "...ID32.1's Full text here",
                }
            ]
            }
            ```
        }\n
        """

        
        self.memory = MemorySaver()
        self.agent = create_react_agent(self.llm, tools=[], prompt=self.prompt, checkpointer=self.memory)

        self.config = {"configurable": {"thread_id": uuid.uuid4()}}

    def run(self, usr_input: str):
        """Run the agent"""
        query = f"""
            User Query:
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
