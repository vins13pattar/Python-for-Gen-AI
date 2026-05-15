import pytest
from unittest.mock import patch, MagicMock
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from src.graph import (
    extract_question,
    route_query,
    retrieve_context,
    grade_context,
    generate_answer,
    fallback_answer,
    greeting_response,
    out_of_scope_response,
    route_after_extract,
    route_after_grade,
    SupportBotState
)

def test_extract_question():
    state: SupportBotState = {"messages": [HumanMessage(content="Hello there!")]}
    result = extract_question(state)
    assert result == {"question": "Hello there!"}

def test_route_query_greeting():
    state: SupportBotState = {"question": "Hi, how are you?"}
    result = route_query(state)
    assert result == {"route": "greeting"}

def test_route_query_out_of_scope():
    state: SupportBotState = {"question": "What is the cricket score?"}
    result = route_query(state)
    assert result == {"route": "out_of_scope"}

def test_route_query_support():
    state: SupportBotState = {"question": "How to enroll in the python course?"}
    result = route_query(state)
    assert result == {"route": "support_query"}

@patch('src.graph.get_retriever')
def test_retrieve_context_no_retriever(mock_get_retriever):
    mock_get_retriever.return_value = None
    state: SupportBotState = {"question": "help"}
    result = retrieve_context(state)
    assert result == {"retrieved_docs": [], "context": ""}

@patch('src.graph.get_retriever')
def test_retrieve_context_success(mock_get_retriever):
    mock_retriever = MagicMock()
    mock_doc1 = MagicMock()
    mock_doc1.page_content = "context 1"
    mock_doc2 = MagicMock()
    mock_doc2.page_content = "context 2"
    mock_retriever.invoke.return_value = [mock_doc1, mock_doc2]
    mock_get_retriever.return_value = mock_retriever
    
    state: SupportBotState = {"question": "help"}
    result = retrieve_context(state)
    assert result["retrieved_docs"] == [mock_doc1, mock_doc2]
    assert result["context"] == "context 1\n\ncontext 2"

def test_grade_context_empty():
    state: SupportBotState = {"retrieved_docs": []}
    result = grade_context(state)
    assert result == {"confidence": "low"}

def test_grade_context_found():
    state: SupportBotState = {"retrieved_docs": ["doc1"]}
    result = grade_context(state)
    assert result == {"confidence": "high"}

@patch('src.graph.ChatOpenAI')
def test_generate_answer(mock_chat):
    mock_llm = MagicMock()
    mock_response = AIMessage(content="Here is the answer.")
    mock_llm.invoke.return_value = mock_response
    mock_chat.return_value = mock_llm
    
    state: SupportBotState = {
        "messages": [HumanMessage(content="What is python?")],
        "question": "What is python?",
        "context": "Python is a language."
    }
    
    result = generate_answer(state)
    assert result["answer"] == "Here is the answer."
    assert result["messages"] == [mock_response]

def test_fallback_answer():
    state: SupportBotState = {}
    result = fallback_answer(state)
    assert "I could not find confirmed information" in result["answer"]
    assert len(result["messages"]) == 1
    assert isinstance(result["messages"][0], AIMessage)

def test_greeting_response():
    state: SupportBotState = {}
    result = greeting_response(state)
    assert "Hi! I’m MicroDegree’s support assistant." in result["answer"]
    assert len(result["messages"]) == 1
    assert isinstance(result["messages"][0], AIMessage)

def test_out_of_scope_response():
    state: SupportBotState = {}
    result = out_of_scope_response(state)
    assert "I’m designed to help with MicroDegree course and learner support queries." in result["answer"]
    assert len(result["messages"]) == 1
    assert isinstance(result["messages"][0], AIMessage)

def test_route_after_extract():
    assert route_after_extract({"route": "greeting"}) == "greeting_response"
    assert route_after_extract({"route": "out_of_scope"}) == "out_of_scope_response"
    assert route_after_extract({"route": "support_query"}) == "retrieve_context"

def test_route_after_grade():
    assert route_after_grade({"confidence": "low"}) == "fallback_answer"
    assert route_after_grade({"confidence": "high"}) == "generate_answer"
