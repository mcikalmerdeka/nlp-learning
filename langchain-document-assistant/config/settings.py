"""
Application settings and constants
"""

# Storage paths
PDF_STORAGE_PATH = 'document_store/pdfs/'
CHROMA_PERSIST_DIR = './chroma_db'
CHROMA_COLLECTION_NAME = 'document_chunks'

# Embedding model configuration
EMBEDDING_MODEL_NAME = 'text-embedding-3-large'

# Document processing configuration
DEFAULT_CHUNK_SIZE = 1000
DEFAULT_CHUNK_OVERLAP = 200
DEFAULT_RETRIEVAL_K = 5

# Model options for UI
MODEL_OPTIONS = {
    "GPT-4o": "gpt-4o",
    "GPT-4.1": "gpt-4.1",
    "Claude Sonnet 4": "claude-sonnet-4-20250514"
}

# LLM configuration
LLM_TEMPERATURE = 0
LLM_MAX_TOKENS = 1024
