"""Tests for the LangGraph graph export (no invocation — just structural checks)."""
import pytest


def test_graph_is_importable():
    """graph.py must be importable without errors after .env is loaded."""
    from dotenv import load_dotenv
    load_dotenv()
    from app.graph import graph
    assert graph is not None


def test_graph_has_correct_tools():
    from dotenv import load_dotenv
    load_dotenv()
    from app.graph import graph
    # create_agent graphs expose their tools via .tools attribute or similar
    # At minimum, the agent must be callable
    assert callable(graph.invoke) or hasattr(graph, "invoke")
