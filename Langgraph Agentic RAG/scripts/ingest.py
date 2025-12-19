"""Script to ingest documents into the vector store."""

import os
import sys

# Add project root to path for direct script execution
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ingestion import ingest_documents


def main() -> None:
    """Run document ingestion."""
    print("Starting document ingestion...")
    vectorstore = ingest_documents()
    print(f"Successfully ingested documents into: {vectorstore._persist_directory}")
    print("Done!")


if __name__ == "__main__":
    main()

