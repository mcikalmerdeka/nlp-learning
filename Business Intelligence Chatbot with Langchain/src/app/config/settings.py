"""Application settings and configuration"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Database Configuration
DB_HOST = "localhost"
DB_PORT = "5432"
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME_SINGLE = os.getenv("DB_NAME_1")  # For single table approach
DB_NAME_OLIST = os.getenv("DB_NAME_2")   # For Olist e-commerce database
DB_NAME_WRS = os.getenv("DB_NAME_3")     # For WRS EHR database

# Model Configuration
MODEL_OPTIONS = {
    "GPT-4.1 mini": "gpt-4.1-mini",
    "Claude Haiku 4.5": "claude-haiku-4-5-20251001"
}

# Embedding Model
EMBEDDING_MODEL = "text-embedding-3-large"

# Vector Store Configuration
FAISS_INDEX_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "faiss_index_store")

# Schema Paths (using relative paths from project root)
SCHEMA_PATH_MULTI = "datasets/dataset_multiple_tables/wrs_ehr_db/ehr_database_docs.md"

# App Configuration
SHOW_DEBUG_INFO = True  # Show SQL queries and results for debugging
