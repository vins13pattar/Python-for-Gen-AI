"""
Critic Agent — Research Quality Review

Responsibilities:
- Reviews all findings for completeness, evidence quality, and gaps
- Determines if findings are sufficient ('approved') or need improvement ('needs_improvement')
- Identifies specific issues and suggests actions
- Sends a validated MCP-style 'critique_created' message
- Updates shared state with critique and critique_status
- Can trigger another retrieval cycle (up to MAX_CRITIC_RETRIES)
"""

import logging
import uuid

from app.config import config
from app.state.research_state import ResearchState
from app.validation.message_validator import create_message

logger = logging.getLogger(__name__)


def _mock_critique(findings: list[dict], retry_count: int) -> dict:
    """
    Generate a mock critique based on finding confidence levels.

    First pass: more likely to find issues.
    Second pass: approve if findings exist.
    """
    if retry_count >= config.MAX_CRITIC_RETRIES:
        # Force approval after max retries
        return {
            "status": "approved",
            "issues": [],
            "recommended_next_action": "write_report",
            "overall_quality": "acceptable",
        }

    low_confidence = [f for f in findings if f["confidence"] == "low"]
    high_confidence = [f for f in findings if f["confidence"] == "high"]

    issues = []

    if not findings:
        issues.append("No findings were generated — research failed to produce insights.")

    if low_confidence and retry_count == 0:
        for f in low_confidence[:2]:
            issues.append(
                f"Finding for '{f['question'][:50]}...' has low confidence "
                f"— more specific context is needed."
            )

    if len(high_confidence) < len(findings) // 2 and retry_count == 0:
        issues.append(
            "Less than half of the findings have high confidence. "
            "Consider retrieving more targeted context."
        )

    if not any("risk" in f["question"].lower() or "challenge" in f["question"].lower()
               for f in findings):
        issues.append(
            "No finding addresses risks or challenges — this is an important dimension."
        )

    # Decision
    if issues and retry_count == 0:
        status = "needs_improvement"
        next_action = "retrieve_more_context"
    else:
        status = "approved"
        next_action = "write_report"
        issues = []  # Clear issues on approval

    quality_map = {
        "approved": "good" if high_confidence else "acceptable",
        "needs_improvement": "weak" if len(issues) > 2 else "partial",
    }

    return {
        "status": status,
        "issues": issues,
        "recommended_next_action": next_action,
        "overall_quality": quality_map[status],
    }


def _llm_critique(findings: list[dict]) -> dict:
    """Generate critique using OpenAI LLM."""
    try:
        from openai import OpenAI
        import json as _json

        client = OpenAI(api_key=config.OPENAI_API_KEY)

        findings_summary = "\n".join(
            f"- Q: {f['question']}\n  Insight: {f['insight']}\n  Confidence: {f['confidence']}"
            for f in findings
        )

        prompt = f"""You are a critical research reviewer.

Review these research findings and evaluate their quality:

{findings_summary}

Provide a JSON response with:
- "status": "approved" or "needs_improvement"
- "issues": list of specific quality issues (empty if approved)
- "recommended_next_action": "write_report" or "retrieve_more_context"
- "overall_quality": "excellent", "good", "acceptable", "partial", or "weak"

Be critical but fair. Approve if findings are substantive and cover the questions well.
Return only valid JSON."""

        response = client.chat.completions.create(
            model=config.OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.2,
        )

        parsed = _json.loads(response.choices[0].message.content)
        return parsed

    except Exception as e:
        logger.warning(f"LLM critic failed, using mock critique: {e}")
        return _mock_critique(findings, retry_count=0)


# ─────────────────────────────────────────────
# LangGraph node function
# ─────────────────────────────────────────────

def critic_node(state: ResearchState) -> dict:
    """
    LangGraph node for the Critic Agent.

    Reads: state['findings'], state['critic_retry_count']
    Writes: state['critique'], state['critique_status'], state['critic_retry_count'], state['agent_messages']
    """
    findings = state["findings"]
    retry_count = state.get("critic_retry_count", 0)
    session_id = state["session_id"]

    logger.info(
        f"[Critic Agent] Reviewing {len(findings)} findings "
        f"(retry #{retry_count})"
    )

    # Generate critique
    if config.USE_MOCK_LLM:
        critique_result = _mock_critique(findings, retry_count)
    else:
        critique_result = _llm_critique(findings)

    status = critique_result.get("status", "approved")
    issues = critique_result.get("issues", [])
    next_action = critique_result.get("recommended_next_action", "write_report")
    quality = critique_result.get("overall_quality", "unknown")

    # Log issues if any
    if issues:
        logger.warning(f"[Critic Agent] Issues found ({len(issues)}):")
        for issue in issues:
            logger.warning(f"  ⚠ {issue}")
    else:
        logger.info(f"[Critic Agent] ✓ Findings approved (quality: {quality})")

    # Create MCP-style message
    receiver = "retriever_agent" if status == "needs_improvement" else "writer_agent"
    message = create_message(
        message_id=f"msg_{uuid.uuid4().hex[:8]}",
        session_id=session_id,
        sender_agent="critic_agent",
        receiver_agent=receiver,
        message_type="critique_created",
        payload={
            "status": status,
            "overall_quality": quality,
            "issues": issues,
            "recommended_next_action": next_action,
            "finding_count_reviewed": len(findings),
        },
        metadata={
            "retry_count": retry_count,
            "max_retries": config.MAX_CRITIC_RETRIES,
        },
    )

    new_retry_count = retry_count + 1 if status == "needs_improvement" else retry_count

    return {
        "critique": issues,
        "critique_status": status,
        "critic_retry_count": new_retry_count,
        "agent_messages": state["agent_messages"] + [message],
    }


def should_retry(state: ResearchState) -> str:
    """
    LangGraph conditional edge function.

    Returns:
        "retry" → route back to retriever
        "write" → proceed to writer
    """
    status = state.get("critique_status", "approved")
    retry_count = state.get("critic_retry_count", 0)

    if status == "needs_improvement" and retry_count <= config.MAX_CRITIC_RETRIES:
        logger.info(
            f"[Critic] Routing → RETRIEVER (retry #{retry_count})"
        )
        return "retry"
    else:
        logger.info("[Critic] Routing → WRITER")
        return "write"
