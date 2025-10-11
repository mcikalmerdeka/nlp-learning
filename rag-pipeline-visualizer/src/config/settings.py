"""Configuration settings for RAG Visualizer"""

import os
from pathlib import Path

# Model options
MODEL_OPTIONS = {
    "all-MiniLM-L6-v2 (Fast)": "sentence-transformers/all-MiniLM-L6-v2",
    "all-mpnet-base-v2 (Accurate)": "sentence-transformers/all-mpnet-base-v2",
    "paraphrase-multilingual (Multilingual)": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
}

# Get the project root directory (assuming settings.py is in src/config/)
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"


def load_sample_text(filename: str) -> str:
    """Load sample text from data directory
    
    Args:
        filename: Name of the text file in data directory
        
    Returns:
        Content of the file as string
    """
    file_path = DATA_DIR / filename
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: File {filename} not found in data directory."
    except Exception as e:
        return f"Error loading {filename}: {str(e)}"


# Sample texts loaded from files
SAMPLE_TEXTS = {
    "AI & Machine Learning": load_sample_text("AI_Machine_Learning.txt"),
    "Climate & Environment": load_sample_text("Climate_Environment.txt"),
    "Space Exploration": load_sample_text("Space_Exploration.txt"),
    "Elon Musk Biography": load_sample_text("Elon_Musk_Overview.txt"),
    "LangGraph Framework": load_sample_text("LangGraph_Overview.txt")
}

# Default values
DEFAULT_CHUNK_SIZE = 100
DEFAULT_OVERLAP = 20
DEFAULT_COLLECTION_NAME = "rag_embeddings"
DEFAULT_N_RESULTS = 3
DEFAULT_REDUCTION_METHOD = "PCA"

