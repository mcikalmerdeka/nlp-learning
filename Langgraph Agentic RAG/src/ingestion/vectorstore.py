"""Vector store ingestion and retrieval logic."""

from functools import lru_cache
from typing import List

from langchain_chroma import Chroma
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.config.settings import settings
from src.core.llm import get_embeddings

# Default URLs for the knowledge base
DEFAULT_URLS = [
    "https://lilianweng.github.io/posts/2023-06-23-agent/",
    "https://lilianweng.github.io/posts/2023-03-15-prompt-engineering/",
    "https://lilianweng.github.io/posts/2023-10-25-adv-attack-llm/",
]


def load_documents(urls: List[str] | None = None) -> List[Document]:
    """Load documents from URLs."""
    urls = urls or DEFAULT_URLS
    doc_batches = [WebBaseLoader(url).load() for url in urls]
    return [doc for batch in doc_batches for doc in batch]


def split_documents(docs: List[Document], chunk_size: int = 500, chunk_overlap: int = 100) -> List[Document]:
    """Split documents into chunks."""
    splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    return splitter.split_documents(docs)


def ingest_documents(urls: List[str] | None = None) -> Chroma:
    """
    Load, split, and store documents in ChromaDB.
    
    Args:
        urls: List of URLs to ingest. Uses DEFAULT_URLS if not provided.
        
    Returns:
        The ChromaDB vector store instance.
    """
    docs = load_documents(urls)
    docs_split = split_documents(docs)

    vectorstore = Chroma.from_documents(
        documents=docs_split,
        collection_name=settings.CHROMA_COLLECTION_NAME,
        embedding=get_embeddings(),
        persist_directory=settings.CHROMA_PERSIST_DIR,
    )
    return vectorstore


@lru_cache(maxsize=1)
def get_retriever() -> VectorStoreRetriever:
    """
    Get the retriever for similarity search (cached).
    
    Assumes documents have already been ingested.
    """
    vectorstore = Chroma(
        collection_name=settings.CHROMA_COLLECTION_NAME,
        embedding_function=get_embeddings(),
        persist_directory=settings.CHROMA_PERSIST_DIR,
    )
    return vectorstore.as_retriever()

