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
DB_NAME_MULTI = os.getenv("DB_NAME_2")   # For multiple tables approach

# Model Configuration
MODEL_OPTIONS = {
    "GPT-4o": "gpt-4o",
    "GPT-4.1": "gpt-4.1",
    "Claude 3.7 Sonnet": "claude-3-7-sonnet-20250219",
    "Claude Sonnet 4": "claude-sonnet-4-20250514"
}

# Embedding Model
EMBEDDING_MODEL = "text-embedding-3-large"

# Vector Store Configuration
FAISS_INDEX_PATH = "faiss_index_store"

# Schema Paths
SCHEMA_PATH_SINGLE = r"E:\NLP Learning\NLP-Learning\Business Intelligence Chatbot with Langchain\datasets\dataset_single_table"
SCHEMA_PATH_MULTI = r"E:\NLP Learning\NLP-Learning\Business Intelligence Chatbot with Langchain\datasets\dataset_multiple_tables\database_schema_description.doc"
SCHEMA_URL_MULTI = "https://raw.githubusercontent.com/mcikalmerdeka/NLP-Learning/main/Business%20Intelligence%20Chatbot%20with%20Langchain/datasets/dataset_multiple_tables/database_schema_description.doc"

# App Configuration
SHOW_DEBUG_INFO = True  # Show SQL queries and results for debugging
