"""
LCEL chain: Fix Generation
Produces corrected code and a list of changes made.
"""
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field
from typing import List

from app.prompts.debugger_prompt import GENERATE_FIX_PROMPT


class FixGeneration(BaseModel):
    fixed_code: str = Field(description="The corrected source code")
    changes_made: List[str] = Field(description="Descriptions of each change made")


def get_fix_generation_chain():
    """Return the fix generation LCEL chain (lazy, so .env is loaded first)."""
    model = init_chat_model("openai:gpt-4.1-mini", temperature=0.2)
    return GENERATE_FIX_PROMPT | model.with_structured_output(FixGeneration)
