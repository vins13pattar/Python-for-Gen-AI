"""
Prompt template for fix generation.

Re-exports from the central debugger_prompt module for discoverability
per the PRD §13 folder structure.
"""
from app.prompts.debugger_prompt import GENERATE_FIX_PROMPT

__all__ = ["GENERATE_FIX_PROMPT"]
