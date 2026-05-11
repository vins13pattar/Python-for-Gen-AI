"""
PII detection middleware: scans tool inputs for personally identifiable
information (API keys, tokens, emails, secrets) and logs warnings.
Applied via @wrap_tool_call on the create_agent middleware list.
"""
import re
import logging
from langchain.agents.middleware import wrap_tool_call

logger = logging.getLogger(__name__)

# Patterns that may indicate PII or secrets in tool inputs
_PII_PATTERNS = [
    (r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", "email address"),
    (r"(?:sk-|pk-)[A-Za-z0-9]{20,}", "API key (sk-/pk- prefix)"),
    (r"(?:ghp_|gho_|ghs_|ghr_)[A-Za-z0-9]{30,}", "GitHub token"),
    (r"xox[baprs]-[A-Za-z0-9\-]{10,}", "Slack token"),
    (r"AKIA[0-9A-Z]{16}", "AWS access key"),
    (r"-----BEGIN (?:RSA |EC |DSA )?PRIVATE KEY-----", "private key"),
    (r"(?:password|passwd|pwd)\s*[=:]\s*\S+", "password assignment"),
    (r"(?:secret|token|api_key|apikey)\s*[=:]\s*['\"]?\S{8,}", "secret/token assignment"),
    (r"\b\d{3}-\d{2}-\d{4}\b", "SSN-like pattern"),
]


@wrap_tool_call
async def pii_detection_middleware(request, handler):
    """Scan tool inputs for PII patterns and log warnings if detected."""
    tool_name = request.tool_call["name"]
    serialized = str(request.tool_call.get("args", {}))
    detected = []

    for pattern, description in _PII_PATTERNS:
        if re.search(pattern, serialized, re.IGNORECASE):
            detected.append(description)

    if detected:
        unique = list(dict.fromkeys(detected))
        logger.warning(
            f"[PIIDetectionMiddleware] Potential PII detected in tool '{tool_name}' input: "
            f"{', '.join(unique)}. Please review the submission for sensitive data."
        )

    return await handler(request)
