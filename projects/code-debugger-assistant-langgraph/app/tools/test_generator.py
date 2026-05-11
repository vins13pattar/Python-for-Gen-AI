import json
from langchain_core.tools import tool
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field
from typing import List
from app.tools.utils import get_safe_writer

from app.prompts.debugger_prompt import TEST_GENERATOR_PROMPT


class TestGeneration(BaseModel):
    test_cases: List[str] = Field(
        description="List of test case strings (at least 3: happy path, edge case, error case)"
    )


@tool
def test_case_generator_tool(language: str, fixed_code: str) -> str:
    """Generate test cases for the corrected code.

    Call this tool after `fix_strategy_tool`. It generates at least 3 test
    cases covering a happy path, edge case, and error/invalid-input case.

    Args:
        language: Programming language of the code.
        fixed_code: The corrected source code to generate tests for.
    """
    writer = get_safe_writer()
    writer("Generating test cases...")

    model = init_chat_model("openai:gpt-4.1-mini", temperature=0.3)
    chain = TEST_GENERATOR_PROMPT | model.with_structured_output(TestGeneration)
    result: TestGeneration = chain.invoke({
        "language": language,
        "fixed_code": fixed_code,
    })

    writer(f"{len(result.test_cases)} test case(s) generated")
    return json.dumps(result.model_dump())
