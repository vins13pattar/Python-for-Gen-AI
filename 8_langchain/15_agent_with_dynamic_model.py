from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain.agents.middleware import wrap_model_call, ModelRequest, ModelResponse
from langchain_core.messages import HumanMessage, AIMessage

import os
from dotenv import load_dotenv
load_dotenv()

basic_model = ChatOpenAI(model="gpt-5.4-mini")
advanced_model = ChatOpenAI(model="gpt-5.4")

@wrap_model_call
def dynamic_model_selection(request: ModelRequest, handler) -> ModelResponse:
    """Choose model based on conversation complexity."""
    message_count = len(request.state["messages"])

    print(f"Message count: {message_count}")

    if message_count > 1:
        # Use an advanced model for longer conversations
        model = advanced_model
    else:
        model = basic_model

    return handler(request.override(model=model))

agent = create_agent(
    model=basic_model,  # Default model
    middleware=[dynamic_model_selection]
)

result = agent.invoke({"messages": [HumanMessage(content="My name is [name]."), AIMessage(content="Hello, [name]. How can I help you today?"), HumanMessage(content="What is my name?")]})
print(result["messages"][-1].content)
print(result)

result = agent.invoke({"messages": [HumanMessage(content="What is 2 + 2?")]})
print(result["messages"][-1].content)
print(result)