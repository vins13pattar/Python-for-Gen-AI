"""
Shared utility: safe stream writer that works both inside a LangGraph
runtime (streaming) and outside (unit tests / direct invocation).
"""
from typing import Callable


def get_safe_writer() -> Callable[[str], None]:
    """Return a stream writer if inside a LangGraph runtime, else a no-op."""
    try:
        from langgraph.config import get_stream_writer
        return get_stream_writer()
    except Exception:
        # Outside graph runtime (e.g. unit tests) — silently ignore
        return lambda msg: None
