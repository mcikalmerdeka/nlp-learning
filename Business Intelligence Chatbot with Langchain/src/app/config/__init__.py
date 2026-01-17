"""Configuration package for the Business Intelligence Chatbot"""

from .settings import (
    DB_HOST,
    DB_PORT,
    DB_USER,
    DB_PASSWORD,
    DB_NAME_SINGLE,
    DB_NAME_OLIST,
    DB_NAME_WRS,
    OPENAI_API_KEY,
    ANTHROPIC_API_KEY,
    MODEL_OPTIONS,
    EMBEDDING_MODEL,
    FAISS_INDEX_PATH,
    SCHEMA_PATH_MULTI,
    SHOW_DEBUG_INFO,
)
from .models import initialize_language_model

__all__ = [
    "DB_HOST",
    "DB_PORT",
    "DB_USER",
    "DB_PASSWORD",
    "DB_NAME_SINGLE",
    "DB_NAME_OLIST",
    "DB_NAME_WRS",
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "MODEL_OPTIONS",
    "EMBEDDING_MODEL",
    "FAISS_INDEX_PATH",
    "SCHEMA_PATH_MULTI",
    "SHOW_DEBUG_INFO",
    "initialize_language_model",
]
