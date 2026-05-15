from pydantic import BaseModel, Field
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI

class GradeResult(BaseModel):
    """Binary score for relevance check on retrieved documents."""
    binary_score: str = Field(description="Documents are relevant to the question, 'yes' or 'no'")

def grade_relevance(question: str, context: str) -> str:
    """
    Grades the relevance of the retrieved context against the user question.
    Returns 'yes' if relevant, 'no' otherwise.
    """
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    structured_llm = llm.with_structured_output(GradeResult, method="function_calling")
    
    system_msg = (
        "You are a grader assessing relevance of a retrieved document to a user question. "
        "If the document contains keyword(s) or semantic meaning related to the user question, grade it as relevant. "
        "It does not need to be a stringent test. The goal is to filter out erroneous retrievals. "
        "Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question."
    )
                 
    messages = [
        SystemMessage(content=system_msg),
        HumanMessage(content=f"Retrieved document: \n\n {context} \n\n User question: {question}")
    ]
    
    try:
        result = structured_llm.invoke(messages)
        return result.binary_score.lower()
    except Exception as e:
        # Fallback in case of parsing error
        print(f"Grader error: {e}")
        return "yes"
