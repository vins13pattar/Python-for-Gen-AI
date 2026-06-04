"""
Planner Agent — Research Planning

Responsibilities:
- Takes the research topic from shared state
- Generates 4-6 prioritized research questions
- Uses real LLM (OpenAI) or mock responses based on config
- Sends a validated MCP-style 'research_plan_created' message
- Updates shared state with research_questions
"""

import logging
import uuid
from datetime import datetime, timezone

from app.config import config
from app.state.research_state import ResearchState
from app.validation.message_validator import create_message

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# Mock response for demo / testing without LLM
# ─────────────────────────────────────────────

def _mock_questions(topic: str) -> list[dict]:
    """Generate mock research questions based on topic keywords."""
    base_questions = [
        {
            "question": f"What is '{topic}' and why does it matter?",
            "priority": "high",
        },
        {
            "question": f"What are the key components or concepts of {topic}?",
            "priority": "high",
        },
        {
            "question": f"What are the main benefits and applications of {topic}?",
            "priority": "high",
        },
        {
            "question": f"What are the risks, limitations, or challenges of {topic}?",
            "priority": "medium",
        },
        {
            "question": f"How does {topic} compare to existing alternatives?",
            "priority": "medium",
        },
        {
            "question": f"What is the future outlook and emerging trends for {topic}?",
            "priority": "low",
        },
    ]
    return base_questions


def _llm_questions(topic: str) -> list[dict]:
    """Generate research questions using OpenAI LLM."""
    try:
        from openai import OpenAI
        import json as _json

        client = OpenAI(api_key=config.OPENAI_API_KEY)

        prompt = f"""You are a research planning assistant.
Given the research topic: "{topic}"

Generate exactly 5 focused research questions that would help produce a comprehensive research report.
Return a JSON array with objects having "question" (string) and "priority" ("high", "medium", or "low") fields.
Order them from most important to least important.

Return only the JSON array, no other text."""

        response = client.chat.completions.create(
            model=config.OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.7,
        )

        content = response.choices[0].message.content
        parsed = _json.loads(content)

        # Handle both {"questions": [...]} and [...] formats
        if isinstance(parsed, list):
            questions = parsed
        elif isinstance(parsed, dict):
            questions = parsed.get("questions", parsed.get("items", list(parsed.values())[0]))
        else:
            questions = _mock_questions(topic)

        return questions

    except Exception as e:
        logger.warning(f"LLM planner failed, using mock: {e}")
        return _mock_questions(topic)


# ─────────────────────────────────────────────
# LangGraph node function
# ─────────────────────────────────────────────

def planner_node(state: ResearchState) -> dict:
    """
    LangGraph node for the Planner Agent.

    Reads: state['topic']
    Writes: state['research_questions'], state['agent_messages']
    """
    topic = state["topic"]
    session_id = state["session_id"]

    logger.info(f"[Planner Agent] Starting research planning for: '{topic}'")

    # Generate research questions
    if config.USE_MOCK_LLM:
        logger.info("[Planner Agent] Using mock LLM responses")
        questions = _mock_questions(topic)
    else:
        logger.info("[Planner Agent] Using OpenAI to generate questions")
        questions = _llm_questions(topic)

    logger.info(f"[Planner Agent] Generated {len(questions)} research questions")

    if state.get("debug"):
        for i, q in enumerate(questions, 1):
            logger.debug(f"  Q{i} [{q['priority']}]: {q['question']}")

    # Create MCP-style message
    message = create_message(
        message_id=f"msg_{uuid.uuid4().hex[:8]}",
        session_id=session_id,
        sender_agent="planner_agent",
        receiver_agent="retriever_agent",
        message_type="research_plan_created",
        payload={
            "topic": topic,
            "questions": questions,
            "question_count": len(questions),
        },
        metadata={
            "priority": "high",
            "requires_response": True,
            "mock_mode": config.USE_MOCK_LLM,
        },
    )

    logger.info("[Planner Agent] ✓ Research plan created and validated")

    return {
        "research_questions": questions,
        "agent_messages": state["agent_messages"] + [message],
    }
