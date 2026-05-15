import os
from typing import TypedDict, Annotated, Literal
from src.grader import grade_relevance
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from src.prompts import SYSTEM_PROMPT
from src.vectorstore import get_retriever

class SupportBotState(TypedDict):
    messages: Annotated[list, add_messages]
    question: str
    route: str
    retrieved_docs: list
    context: str
    answer: str
    confidence: str

# 1. Nodes
def extract_question(state: SupportBotState) -> SupportBotState:
    last_message = state["messages"][-1]
    return {"question": last_message.content}

def route_query(state: SupportBotState) -> SupportBotState:
    question = state["question"].lower()
    
    # Simple keyword-based routing for this MVP
    greetings = ["hi", "hello", "hey", "namaskara"]
    out_of_scope = ["cricket", "score", "weather", "virat", "kohli", "politics", "movies"]
    
    if any(question.startswith(g) or question == g for g in greetings):
        return {"route": "greeting"}
        
    if any(word in question for word in out_of_scope):
        return {"route": "out_of_scope"}
        
    return {"route": "support_query"}

def retrieve_context(state: SupportBotState) -> SupportBotState:
    retriever = get_retriever()
    if retriever is None:
        return {"retrieved_docs": [], "context": ""}
        
    docs = retriever.invoke(state["question"])
    context = "\n\n".join([doc.page_content for doc in docs])
    return {"retrieved_docs": docs, "context": context}

def grade_context(state: SupportBotState) -> SupportBotState:
    docs = state.get("retrieved_docs", [])
    if not docs:
        return {"confidence": "low"}
    
    question = state["question"]
    context = state["context"]
    
    score = grade_relevance(question, context)
    
    if score == "yes":
        return {"confidence": "high"}
    else:
        return {"confidence": "low"}

def generate_answer(state: SupportBotState) -> SupportBotState:
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    
    # Format memory
    memory_messages = [msg for msg in state["messages"] if isinstance(msg, (HumanMessage, AIMessage))]
    
    messages = [
        SystemMessage(content=SYSTEM_PROMPT + f"\n\nContext:\n{state['context']}")
    ] + memory_messages[:-1] + [
        HumanMessage(content=state["question"])
    ]
    
    response = llm.invoke(messages)
    return {"answer": response.content, "messages": [response]}

def fallback_answer(state: SupportBotState) -> SupportBotState:
    fallback = (
        "I could not find confirmed information about this in my MicroDegree knowledge base.\n"
        "Please contact MicroDegree directly for the latest and accurate details.\n\n"
        "Enquiry: 08047109999\n"
        "Email: hello@microdegree.work"
    )
    return {"answer": fallback, "messages": [AIMessage(content=fallback)]}

def greeting_response(state: SupportBotState) -> SupportBotState:
    greeting = (
        "Hi! I’m MicroDegree’s support assistant. I can help you with course details, "
        "certificates, Kannada learning, doubt clarification, MicroDegree Pro, and contact information."
    )
    return {"answer": greeting, "messages": [AIMessage(content=greeting)]}

def out_of_scope_response(state: SupportBotState) -> SupportBotState:
    out_of_scope = (
        "I’m designed to help with MicroDegree course and learner support queries. "
        "Please ask me about courses, certificates, learning support, MicroDegree Pro, or contact details."
    )
    return {"answer": out_of_scope, "messages": [AIMessage(content=out_of_scope)]}

# 2. Conditional Edges
def route_after_extract(state: SupportBotState) -> str:
    route = state["route"]
    if route == "greeting":
        return "greeting_response"
    elif route == "out_of_scope":
        return "out_of_scope_response"
    else:
        return "retrieve_context"

def route_after_grade(state: SupportBotState) -> str:
    if state["confidence"] == "low":
        return "fallback_answer"
    else:
        return "generate_answer"

# 3. Build Graph
workflow = StateGraph(SupportBotState)

# Add nodes
workflow.add_node("extract_question", extract_question)
workflow.add_node("route_query", route_query)
workflow.add_node("retrieve_context", retrieve_context)
workflow.add_node("grade_context", grade_context)
workflow.add_node("generate_answer", generate_answer)
workflow.add_node("fallback_answer", fallback_answer)
workflow.add_node("greeting_response", greeting_response)
workflow.add_node("out_of_scope_response", out_of_scope_response)

# Add edges
workflow.add_edge(START, "extract_question")
workflow.add_edge("extract_question", "route_query")

workflow.add_conditional_edges(
    "route_query",
    route_after_extract,
    {
        "greeting_response": "greeting_response",
        "out_of_scope_response": "out_of_scope_response",
        "retrieve_context": "retrieve_context"
    }
)

workflow.add_edge("retrieve_context", "grade_context")

workflow.add_conditional_edges(
    "grade_context",
    route_after_grade,
    {
        "generate_answer": "generate_answer",
        "fallback_answer": "fallback_answer"
    }
)

workflow.add_edge("generate_answer", END)
workflow.add_edge("fallback_answer", END)
workflow.add_edge("greeting_response", END)
workflow.add_edge("out_of_scope_response", END)

# Compile graph with memory
memory = InMemorySaver()
app = workflow.compile(checkpointer=memory)
