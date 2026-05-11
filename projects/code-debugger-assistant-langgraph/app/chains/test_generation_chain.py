"""
LCEL chain: Test Generation
Produces at least 3 test cases for the corrected code.
"""
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field
from typing import List

from app.prompts.debugger_prompt import TEST_GENERATOR_PROMPT


class TestGeneration(BaseModel):
    test_cases: List[str] = Field(description="List of test cases")


def get_test_generation_chain():
    """Return the test generation LCEL chain (lazy, so .env is loaded first)."""
    model = init_chat_model("openai:gpt-4.1-mini", temperature=0.3)
    return TEST_GENERATOR_PROMPT | model.with_structured_output(TestGeneration)
