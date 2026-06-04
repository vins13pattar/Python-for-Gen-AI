"""
State Store — in-memory singleton that persists research state.

Provides methods to:
- Get/update the current research state
- Export state to JSON files
- Log agent messages
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

from app.state.research_state import ResearchState
from app.config import config

logger = logging.getLogger(__name__)


class StateStore:
    """
    In-memory singleton state store.

    Holds the current ResearchState and provides
    thread-safe read/write access for all agents.
    """

    _instance: Optional["StateStore"] = None
    _state: Optional[ResearchState] = None

    def __new__(cls) -> "StateStore":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def initialize(self, session_id: str, topic: str, debug: bool = False) -> ResearchState:
        """Initialize a fresh research state for a new session."""
        self._state = ResearchState(
            session_id=session_id,
            topic=topic,
            research_questions=[],
            retrieved_context=[],
            embeddings=[],
            findings=[],
            critique=[],
            critique_status="pending",
            critic_retry_count=0,
            agent_messages=[],
            final_report="",
            debug=debug,
        )
        logger.info(f"State initialized for session: {session_id}")
        return self._state

    def get_state(self) -> ResearchState:
        """Return current research state."""
        if self._state is None:
            raise RuntimeError("State not initialized. Call initialize() first.")
        return self._state

    def update_state(self, updates: dict) -> ResearchState:
        """Merge updates into current state."""
        if self._state is None:
            raise RuntimeError("State not initialized. Call initialize() first.")
        self._state.update(updates)
        return self._state

    def log_message(self, message: dict) -> None:
        """Append a validated agent message to state."""
        if self._state is None:
            raise RuntimeError("State not initialized.")
        self._state["agent_messages"].append(message)
        if self._state.get("debug"):
            logger.debug(
                f"[{message['sender_agent']} → {message['receiver_agent']}] "
                f"{message['message_type']}"
            )

    def export_all(self) -> dict[str, Path]:
        """Export state, messages, and embeddings to output files."""
        if self._state is None:
            raise RuntimeError("State not initialized.")

        outputs_dir = config.OUTPUTS_DIR
        outputs_dir.mkdir(parents=True, exist_ok=True)

        exported: dict[str, Path] = {}

        # Export full state
        state_path = outputs_dir / "research_state.json"
        with open(state_path, "w", encoding="utf-8") as f:
            # Convert state to serializable dict (exclude non-serializable items)
            state_dict = dict(self._state)
            json.dump(state_dict, f, indent=2, default=str)
        exported["research_state"] = state_path
        logger.info(f"Exported research state → {state_path}")

        # Export agent messages
        messages_path = outputs_dir / "agent_messages.json"
        with open(messages_path, "w", encoding="utf-8") as f:
            json.dump(self._state["agent_messages"], f, indent=2, default=str)
        exported["agent_messages"] = messages_path
        logger.info(f"Exported agent messages → {messages_path}")

        # Export embeddings
        embeddings_path = outputs_dir / "embeddings.json"
        with open(embeddings_path, "w", encoding="utf-8") as f:
            json.dump(self._state["embeddings"], f, indent=2, default=str)
        exported["embeddings"] = embeddings_path
        logger.info(f"Exported embeddings → {embeddings_path}")

        # Export final report
        if self._state["final_report"]:
            report_path = outputs_dir / "final_report.md"
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(self._state["final_report"])
            exported["final_report"] = report_path
            logger.info(f"Exported final report → {report_path}")

        return exported

    def reset(self) -> None:
        """Clear current state (for testing)."""
        self._state = None


# Singleton instance
state_store = StateStore()
