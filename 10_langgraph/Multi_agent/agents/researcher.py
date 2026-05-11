# agents/researcher.py
import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults
from state import MultiAgentState


from dotenv import load_dotenv
load_dotenv()

RESEARCHER_SYSTEM = """
You are a research specialist. Your job is to gather accurate, relevant facts,
statistics, expert quotes, and sources for the given topic.

Use the search tool multiple times to cover different angles:
1. Core facts and background
2. Recent developments or statistics
3. Expert opinions or studies

Return a structured research summary with clear bullet points grouped by theme.
Be specific — include numbers, dates, names, and URLs when found.
"""

# Tavily is purpose-built for LLM agents — much better than raw Google
search_tool = TavilySearchResults(
    max_results=4,
    api_key=os.getenv("TAVILY_API_KEY"),
)

llm = ChatOpenAI(model="gpt-4o", temperature=0.1)
llm_with_tools = llm.bind_tools([search_tool])


def researcher_node(state: MultiAgentState) -> dict:
    """
    Performs multi-step web research on the task.
    Loops internally until the LLM stops calling search tools.
    """
    print(f"\n[researcher] Starting research on: {state['task'][:80]}...")

    messages = [
        SystemMessage(content=RESEARCHER_SYSTEM),
        HumanMessage(content=f"Research this topic thoroughly: {state['task']}"),
    ]

    research_results = []
    iteration = 0
    max_iterations = 5  # Safety cap to avoid infinite loops

    while iteration < max_iterations:
        iteration += 1
        response = llm_with_tools.invoke(messages)
        messages.append(response)

        # No more tool calls → LLM has finished researching
        if not getattr(response, "tool_calls", None):
            # Final response is the structured research summary
            research_results.append(response.content)
            print(f"[researcher] Done after {iteration} search round(s).")
            break

        # Execute each search tool call
        from langchain_core.messages import ToolMessage
        for tc in response.tool_calls:
            print(f"[researcher] Searching: {tc['args'].get('query', '')[:60]}...")
            result = search_tool.invoke(tc["args"])
            messages.append(
                ToolMessage(content=str(result), tool_call_id=tc["id"])
            )

    summary = "\n\n".join(research_results) if research_results else "No results found."

    return {
        "research_notes": [summary],
        "messages": [AIMessage(content=f"[Researcher] Gathered research:\n{summary[:300]}...")],
    }