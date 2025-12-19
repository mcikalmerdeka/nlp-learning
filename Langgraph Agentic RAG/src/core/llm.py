"""Centralized LLM and embedding model instances."""

from functools import lru_cache

from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from src.config.settings import settings


@lru_cache(maxsize=1)
def get_llm() -> ChatOpenAI:
    """Get the default LLM instance (cached)."""
    return ChatOpenAI(
        model=settings.LLM_MODEL,
        temperature=settings.LLM_TEMPERATURE,
        api_key=settings.OPENAI_API_KEY,
    )


@lru_cache(maxsize=1)
def get_embeddings() -> OpenAIEmbeddings:
    """Get the embedding model instance (cached)."""
    return OpenAIEmbeddings(
        model=settings.EMBEDDING_MODEL,
        api_key=settings.OPENAI_API_KEY,
    )

