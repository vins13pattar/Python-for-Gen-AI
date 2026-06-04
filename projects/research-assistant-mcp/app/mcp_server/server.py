"""
MCP Server — FastMCP server exposing research tools and resources.

Exposes 5 tools and 4 resources following the MCP protocol.
Can be run standalone for integration with MCP-compatible hosts.

Usage:
    uv run python -m app.mcp_server.server

Or integrated via FastMCP in-process.
"""

import logging

logger = logging.getLogger(__name__)

try:
    from fastmcp import FastMCP

    mcp_server = FastMCP(
        name="research-assistant-mcp",
        description=(
            "MCP server for the Research Assistant System. "
            "Exposes tools and resources for multi-agent research collaboration."
        ),
    )

    # ── Register Tools ────────────────────────────────────────────────────────
    from app.mcp_server.tools import (
        save_context as _save_context,
        get_context as _get_context,
        save_embedding as _save_embedding,
        search_context as _search_context,
        log_agent_message as _log_agent_message,
    )

    @mcp_server.tool()
    def save_context(session_id: str, chunk: dict) -> dict:
        """Save a retrieved context chunk to the shared research state."""
        return _save_context(session_id, chunk)

    @mcp_server.tool()
    def get_context(session_id: str, question: str = None) -> dict:
        """Get context chunks from shared state, optionally filtered by question."""
        return _get_context(session_id, question)

    @mcp_server.tool()
    def save_embedding(session_id: str, embedding_record: dict) -> dict:
        """Store a vector embedding record in shared state."""
        return _save_embedding(session_id, embedding_record)

    @mcp_server.tool()
    def search_context(session_id: str, query: str, top_k: int = 3) -> dict:
        """Semantic search over stored embeddings using cosine similarity."""
        return _search_context(session_id, query, top_k)

    @mcp_server.tool()
    def log_agent_message(session_id: str, message: dict) -> dict:
        """Log a validated MCP-style agent message to shared state."""
        return _log_agent_message(session_id, message)

    # ── Register Resources ────────────────────────────────────────────────────
    from app.mcp_server.resources import (
        get_session_resource,
        get_context_resource,
        get_embeddings_resource,
        get_messages_resource,
    )

    @mcp_server.resource("research://session/{session_id}")
    def session_resource(session_id: str) -> dict:
        """Current research session metadata and status."""
        return get_session_resource(session_id)

    @mcp_server.resource("research://context/{session_id}")
    def context_resource(session_id: str) -> dict:
        """All retrieved context chunks for the session."""
        return get_context_resource(session_id)

    @mcp_server.resource("research://embeddings/{session_id}")
    def embeddings_resource(session_id: str) -> dict:
        """Vector embedding records (without raw vectors)."""
        return get_embeddings_resource(session_id)

    @mcp_server.resource("research://messages/{session_id}")
    def messages_resource(session_id: str) -> dict:
        """All MCP-style agent messages in this session."""
        return get_messages_resource(session_id)

    logger.info("✓ FastMCP server configured with 5 tools and 4 resources")
    MCP_AVAILABLE = True

except ImportError:
    logger.warning(
        "fastmcp not installed. MCP server features unavailable. "
        "Run: uv add fastmcp"
    )
    mcp_server = None
    MCP_AVAILABLE = False


def run_server():
    """Run the MCP server in standalone mode."""
    if not MCP_AVAILABLE or mcp_server is None:
        logger.error("FastMCP not available. Install with: uv add fastmcp")
        return

    logger.info("Starting MCP server...")
    mcp_server.run()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_server()
