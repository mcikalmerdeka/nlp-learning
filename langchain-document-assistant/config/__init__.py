"""Configuration package for the RAG application"""

from .settings import (
    PDF_STORAGE_PATH,
    EMBEDDING_MODEL_NAME,
    MODEL_OPTIONS,
    DEFAULT_CHUNK_SIZE,
    DEFAULT_CHUNK_OVERLAP,
    DEFAULT_RETRIEVAL_K,
    CHROMA_PERSIST_DIR,
    CHROMA_COLLECTION_NAME
)

from .models import initialize_language_model

__all__ = [
    'PDF_STORAGE_PATH',
    'EMBEDDING_MODEL_NAME',
    'MODEL_OPTIONS',
    'DEFAULT_CHUNK_SIZE',
    'DEFAULT_CHUNK_OVERLAP',
    'DEFAULT_RETRIEVAL_K',
    'CHROMA_PERSIST_DIR',
    'CHROMA_COLLECTION_NAME',
    'initialize_language_model'
]
