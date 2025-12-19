import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    """Centralized configuration for the application."""

    # API Keys
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "")

    # Model Configuration
    LLM_MODEL: str = "gpt-4.1-mini"
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    LLM_TEMPERATURE: float = 0

    # Vector Store Configuration
    CHROMA_COLLECTION_NAME: str = "rag-chroma"
    CHROMA_PERSIST_DIR: str = ".chroma_db"

    # Web Search Configuration
    TAVILY_MAX_RESULTS: int = 2

    # Graph Output
    GRAPH_OUTPUT_PATH: str = "outputs/complete_rag_graph.png"


settings = Settings()

