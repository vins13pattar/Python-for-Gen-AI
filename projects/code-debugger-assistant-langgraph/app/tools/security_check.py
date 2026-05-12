import langsmith as ls
from langchain_core.tools import tool
from app.tools.utils import get_safe_writer

# Patterns that indicate an unsafe execution request
_UNSAFE_PATTERNS = [
    "os.system(",
    "subprocess.",
    "eval(",
    "exec(",
    "rm -rf",
    "drop table",
    "__import__",
    "shutil.rmtree",
    "open('/etc",
]


@tool
def security_check_tool(code: str, expected_behavior: str = "") -> str:
    """Check whether the submitted code or request contains unsafe execution patterns.

    Always call this tool FIRST before any other tool. It detects requests to
    execute shell commands, delete files, access secrets, or bypass system controls.

    Args:
        code: The source code to inspect.
        expected_behavior: The user's description of what they expect (optional).
    """
    # Attach LangSmith metadata to the current trace
    rt = ls.get_current_run_tree()
    if rt:
        rt.name = "SecurityCheck"
        rt.metadata.update({"pipeline_step": "security_check", "tool_type": "guardrail"})
        rt.tags = list(set((rt.tags or []) + ["code-debugger", "tool", "security"]))

    writer = get_safe_writer()
    writer("Running security check...")

    combined = (code + " " + expected_behavior).lower()
    flagged = [p for p in _UNSAFE_PATTERNS if p.lower() in combined]

    if flagged:
        writer(f"⚠️  Security warning — unsafe pattern(s) detected: {flagged}")
        return (
            f"SECURITY_WARNING: The submitted code contains potentially unsafe patterns: {flagged}. "
            "This assistant will analyze the code as text only and will NOT execute it."
        )

    writer("Security check passed ✓")
    return "SAFE: No unsafe execution patterns detected."
