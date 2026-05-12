"""
LCEL chain: Final Report
Compiles all debugging findings into a structured DebugReport.
"""
from langchain.chat_models import init_chat_model

from app.prompts.debugger_prompt import FORMAT_REPORT_PROMPT
from app.schemas.response import DebugReport


def get_final_report_chain():
    """Return the final report LCEL chain (lazy, so .env is loaded first).

    This chain takes the collected debugging findings (language, issue,
    root cause, fixed code, changes, test cases) and produces a complete
    DebugReport with prevention tips and confidence score.
    """
    model = init_chat_model("openai:gpt-4.1-mini", temperature=0.2)
    chain = FORMAT_REPORT_PROMPT | model.with_structured_output(DebugReport)
    return chain.with_config(
        run_name="FinalReport-Chain",
        tags=["code-debugger", "chain", "final-report"],
        metadata={"chain": "final_report", "pipeline_step": "report_generation"},
    )
