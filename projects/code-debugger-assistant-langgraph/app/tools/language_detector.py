from langchain_core.tools import tool
from langchain_core.output_parsers import StrOutputParser
from langchain.chat_models import init_chat_model
from app.tools.utils import get_safe_writer

from app.prompts.debugger_prompt import DETECT_LANGUAGE_PROMPT


@tool
def detect_language_tool(code: str) -> str:
    """Detect the programming language of the submitted code.

    Call this tool when the user has not specified a language, or when
    the language is unclear from context.

    Args:
        code: The source code snippet to analyze.
    """
    writer = get_safe_writer()
    writer("Detecting programming language...")

    model = init_chat_model("openai:gpt-4.1-mini", temperature=0.0)
    chain = DETECT_LANGUAGE_PROMPT | model | StrOutputParser()
    result = chain.invoke({"code": code})
    language = result.strip().lower()

    writer(f"Language detected: {language}")
    return language
