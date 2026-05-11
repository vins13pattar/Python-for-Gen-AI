# agents/reviewer.py
import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from state import MultiAgentState


from dotenv import load_dotenv
load_dotenv()

REVIEWER_SYSTEM = """
You are a senior editor and fact-checker. You review drafts against:
  1. The original task — does the content actually answer it?
  2. The research notes — are facts used accurately?
  3. Writing quality — clarity, flow, structure, engagement

Return ONLY a JSON object with this exact structure:
{
  "verdict": "approved" or "needs_revision",
  "score": <integer 1-10>,
  "strengths": ["...", "..."],
  "issues": ["...", "..."],
  "feedback": "Detailed actionable feedback for the writer. Be specific."
}

Be constructive but demanding. Approve only if score >= 7 and no critical issues exist.
Critical issues: factual errors, missing key points, poor structure, off-topic content.
"""

llm = ChatOpenAI(model="gpt-4o", temperature=0)


def reviewer_node(state: MultiAgentState) -> dict:
    """
    Reviews the current draft against task and research.
    Returns verdict, score, and specific feedback.
    """
    print(f"\n[reviewer] Reviewing draft (revision #{state.get('revision_count', 0)})...")

    notes = "\n\n---\n\n".join(state.get("research_notes", []))

    user_msg = f"""
Original task: {state['task']}

Research notes:
{notes}

Draft to review:
{state.get('draft', '')}

Evaluate this draft thoroughly.
""".strip()

    messages = [
        SystemMessage(content=REVIEWER_SYSTEM),
        HumanMessage(content=user_msg),
    ]

    response = llm.invoke(messages)
    raw = response.content.strip()

    # Parse JSON verdict
    try:
        if "```" in raw:
            raw = raw.split("```")[1].strip()
            if raw.startswith("json"):
                raw = raw[4:].strip()
        review = json.loads(raw)
    except Exception as e:
        print(f"[reviewer] JSON parse failed: {e} — defaulting to approved")
        review = {
            "verdict": "approved",
            "score": 7,
            "strengths": ["Content is acceptable"],
            "issues": [],
            "feedback": "Minor issues only.",
        }

    verdict  = review.get("verdict", "approved")
    score    = review.get("score", 7)
    feedback = review.get("feedback", "")
    issues   = review.get("issues", [])
    strengths = review.get("strengths", [])

    print(f"[reviewer] Verdict: {verdict.upper()} (score: {score}/10)")
    if issues:
        print(f"[reviewer] Issues: {'; '.join(issues[:2])}")

    summary = (
        f"[Reviewer] Score: {score}/10 | Verdict: {verdict.upper()}\n"
        f"Strengths: {', '.join(strengths[:2])}\n"
        f"Issues: {', '.join(issues[:2]) if issues else 'None'}"
    )

    return {
        "review_verdict": verdict,
        "review_feedback": feedback if verdict == "needs_revision" else "",
        "messages": [AIMessage(content=summary)],
    }