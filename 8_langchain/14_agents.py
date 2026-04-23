from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser

import os
from dotenv import load_dotenv
load_dotenv()


@tool
def calculator(operation: str, num1: int, num2: int) -> str:
    """Perform a mathematical operation on two numbers. Input: operation (add, subtract, multiply, divide), num1, num2."""
    print(f"Performing {operation} on {num1} and {num2}")
    if operation == "add":
        sum = num1 + num2
        print(f"The result of {operation} is {sum}")
        return f"The result of {operation} is {sum}"
    elif operation == "subtract":
        difference = num1 - num2
        print(f"The result of {operation} is {difference}")
        return f"The result of {operation} is {difference}"
    elif operation == "multiply":
        product = num1 * num2
        print(f"The result of {operation} is {product}")
        return f"The result of {operation} is {product}"
    elif operation == "divide":
        quotient = num1 / num2
        print(f"The result of {operation} is {quotient}")
        return f"The result of {operation} is {quotient}"
    else:
        return "Invalid operation"

tools = [calculator]

model = ChatOpenAI(model="gpt-5.4-mini", temperature=0)

agent = create_agent(model, tools, system_prompt="You are a helpful assistant that can perform mathematical operations step by step. Solve the problem using tools provided to you.")

while True:
    question = input("Enter a question: ")
    if question.lower() in ["exit", "quit"]:
        break
    result = agent.invoke({"messages": [HumanMessage(content=question)]})
    print(result["messages"][-1].content)
    print(result)