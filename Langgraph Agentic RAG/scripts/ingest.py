"""Script to ingest documents into the vector store."""

import os
import sys

# Add project root to path for direct script execution
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core import logger, setup_logging
from src.ingestion import ingest_documents

setup_logging("INFO")


def main() -> None:
    """Run document ingestion."""
    logger.info("Starting document ingestion...")
    vectorstore = ingest_documents()
    logger.info(f"Ingested documents into: {vectorstore._persist_directory}")
    logger.info("Done!")


if __name__ == "__main__":
    main()
