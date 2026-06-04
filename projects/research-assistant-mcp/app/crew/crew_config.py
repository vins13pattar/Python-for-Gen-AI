"""
CrewAI Configuration — Role-Based Agent Definitions

Defines 6 CrewAI agents, each with a clear role, goal, and backstory.
These agents mirror the LangGraph nodes but model the "human team" aspect
of multi-agent collaboration.

CrewAI Agents:
1. Research Planner        — Designs the research strategy
2. Context Retriever       — Hunts for relevant information
3. Embedding Specialist    — Creates semantic representations
4. Research Analyst        — Extracts insights from evidence
5. Research Critic         — Reviews and quality-controls findings
6. Research Writer         — Composes the final report
"""

import logging
from app.config import config

logger = logging.getLogger(__name__)


def _get_llm():
    """Get the LLM instance for CrewAI agents."""
    if config.USE_MOCK_LLM or not config.OPENAI_API_KEY:
        logger.info("CrewAI: Using mock LLM (no API key or mock mode enabled)")
        return None
    try:
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=config.OPENAI_MODEL,
            api_key=config.OPENAI_API_KEY,
            temperature=0.3,
        )
    except Exception as e:
        logger.warning(f"Could not initialize LLM for CrewAI: {e}")
        return None


def get_crew_agents() -> dict:
    """
    Return all CrewAI agent definitions as a dictionary.

    Returns:
        Dict mapping agent_name → Agent configuration dict
        (use these dicts to inspect agent properties without importing crewai)
    """
    llm = _get_llm()

    agents_config = {
        "research_planner": {
            "role": "Research Planner",
            "goal": (
                "Transform a broad research topic into a structured set of focused, "
                "prioritized research questions that will guide a comprehensive investigation."
            ),
            "backstory": (
                "You are an expert research strategist with 15 years of experience in "
                "academic and industry research. You know how to break complex topics "
                "into well-scoped, answerable questions. Your plans are always focused, "
                "prioritized, and actionable."
            ),
            "verbose": True,
            "allow_delegation": False,
            "llm": llm,
        },
        "context_retriever": {
            "role": "Context Retriever",
            "goal": (
                "Find the most relevant and high-quality context for each research question "
                "by searching available knowledge sources."
            ),
            "backstory": (
                "You are a skilled research librarian and information specialist. You know "
                "exactly where to look for information and how to evaluate source quality. "
                "You never return empty-handed — if primary sources are unavailable, "
                "you synthesize the best available context."
            ),
            "verbose": True,
            "allow_delegation": False,
            "llm": llm,
        },
        "embedding_specialist": {
            "role": "Embedding Specialist",
            "goal": (
                "Convert retrieved text into high-quality vector embeddings that enable "
                "semantic search and context reuse across agents."
            ),
            "backstory": (
                "You are a machine learning engineer specialized in natural language "
                "processing and vector representations. You understand how embeddings "
                "capture semantic meaning and how to make them useful for downstream "
                "AI tasks. You ensure every piece of retrieved content is properly "
                "vectorized for the analyst team."
            ),
            "verbose": True,
            "allow_delegation": False,
            "llm": llm,
        },
        "research_analyst": {
            "role": "Research Analyst",
            "goal": (
                "Extract meaningful insights from retrieved context using semantic search "
                "and analytical reasoning, producing structured findings with confidence levels."
            ),
            "backstory": (
                "You are a senior research analyst with expertise in synthesizing complex "
                "information into clear, actionable insights. You use both quantitative "
                "embedding-based search and qualitative reasoning to identify patterns, "
                "draw conclusions, and assess confidence in your findings."
            ),
            "verbose": True,
            "allow_delegation": False,
            "llm": llm,
        },
        "research_critic": {
            "role": "Research Critic",
            "goal": (
                "Evaluate the quality, completeness, and accuracy of research findings, "
                "identifying gaps and determining whether the research is ready for publication."
            ),
            "backstory": (
                "You are a rigorous peer reviewer and quality assurance expert. You have "
                "a reputation for catching gaps, weak evidence, and logical inconsistencies. "
                "Your feedback is specific, constructive, and actionable. You approve only "
                "when findings genuinely answer the research questions with sufficient evidence."
            ),
            "verbose": True,
            "allow_delegation": False,
            "llm": llm,
        },
        "research_writer": {
            "role": "Research Writer",
            "goal": (
                "Synthesize all research findings into a comprehensive, well-structured, "
                "and reader-friendly research report in Markdown format."
            ),
            "backstory": (
                "You are an expert technical writer and research communicator. You can "
                "transform complex findings into clear, compelling narratives. Your reports "
                "are always well-structured, properly cited, and accessible to both technical "
                "and non-technical audiences. You incorporate critic feedback to produce "
                "polished final reports."
            ),
            "verbose": True,
            "allow_delegation": False,
            "llm": llm,
        },
    }

    return agents_config


def get_crew_agents_crewai():
    """
    Return instantiated CrewAI Agent objects.

    Requires: crewai package installed.
    Returns list of Agent objects ready for use in a Crew.
    """
    try:
        from crewai import Agent

        agents_config = get_crew_agents()
        crewai_agents = {}

        for name, cfg in agents_config.items():
            agent_kwargs = {
                "role": cfg["role"],
                "goal": cfg["goal"],
                "backstory": cfg["backstory"],
                "verbose": cfg["verbose"],
                "allow_delegation": cfg["allow_delegation"],
            }
            if cfg["llm"] is not None:
                agent_kwargs["llm"] = cfg["llm"]

            crewai_agents[name] = Agent(**agent_kwargs)
            logger.debug(f"CrewAI agent created: {cfg['role']}")

        return crewai_agents

    except ImportError:
        logger.error("crewai package not installed. Run: uv add crewai[tools]")
        return {}
    except Exception as e:
        logger.error(f"Failed to create CrewAI agents: {e}")
        return {}
