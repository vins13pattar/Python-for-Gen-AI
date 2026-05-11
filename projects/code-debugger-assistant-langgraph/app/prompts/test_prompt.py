"""
Prompt template for test case generation.

Re-exports from the central debugger_prompt module for discoverability
per the PRD §13 folder structure.
"""
from app.prompts.debugger_prompt import TEST_GENERATOR_PROMPT

__all__ = ["TEST_GENERATOR_PROMPT"]
