"""
Configuration module for Research Assistant System.

Loads settings from environment variables and .env file.
Supports both mock mode (no API key) and real mode (OpenAI).
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root
_project_root = Path(__file__).parent.parent
load_dotenv(_project_root / ".env")


class Config:
    """Application configuration loaded from environment variables."""

    # OpenAI settings
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

    # Mock mode (set to True by default so demos work without API keys)
    USE_MOCK_LLM: bool = os.getenv("USE_MOCK_LLM", "true").lower() == "true"
    USE_MOCK_EMBEDDINGS: bool = os.getenv("USE_MOCK_EMBEDDINGS", "true").lower() == "true"

    # Research settings
    RESEARCH_TOPIC: str = os.getenv(
        "RESEARCH_TOPIC", "Impact of AI agents on software development"
    )
    MAX_CRITIC_RETRIES: int = int(os.getenv("MAX_CRITIC_RETRIES", "2"))
    SESSION_PREFIX: str = os.getenv("SESSION_PREFIX", "research")

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Paths
    PROJECT_ROOT: Path = _project_root
    APP_DIR: Path = _project_root / "app"
    SCHEMAS_DIR: Path = APP_DIR / "schemas"
    KNOWLEDGE_DIR: Path = APP_DIR / "knowledge"
    OUTPUTS_DIR: Path = APP_DIR / "outputs"

    @classmethod
    def validate(cls) -> None:
        """Validate required config. Raise if real mode needs missing API key."""
        if not cls.USE_MOCK_LLM and not cls.OPENAI_API_KEY:
            raise EnvironmentError(
                "OPENAI_API_KEY is required when USE_MOCK_LLM=false. "
                "Set it in .env or set USE_MOCK_LLM=true for demo mode."
            )
        if not cls.USE_MOCK_EMBEDDINGS and not cls.OPENAI_API_KEY:
            raise EnvironmentError(
                "OPENAI_API_KEY is required when USE_MOCK_EMBEDDINGS=false. "
                "Set it in .env or set USE_MOCK_EMBEDDINGS=true for demo mode."
            )
        # Ensure outputs directory exists
        cls.OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

    @classmethod
    def summary(cls) -> dict:
        """Return a human-readable config summary."""
        return {
            "openai_model": cls.OPENAI_MODEL,
            "embedding_model": cls.EMBEDDING_MODEL,
            "use_mock_llm": cls.USE_MOCK_LLM,
            "use_mock_embeddings": cls.USE_MOCK_EMBEDDINGS,
            "max_critic_retries": cls.MAX_CRITIC_RETRIES,
            "log_level": cls.LOG_LEVEL,
        }


# Singleton config instance
config = Config()
