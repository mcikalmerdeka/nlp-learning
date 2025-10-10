"""ChromaDB vector store operations"""

import chromadb
import tempfile


def create_chromadb_collection(collection_name: str = "rag_embeddings"):
    """Create or get ChromaDB collection
    
    Args:
        collection_name: Name of the collection to create
        
    Returns:
        ChromaDB collection instance
    """
    # Use the new EphemeralClient for in-memory storage
    # or PersistentClient for disk storage
    client = chromadb.EphemeralClient()
    
    # Delete existing collection if it exists
    try:
        client.delete_collection(collection_name)
    except:
        pass
    
    collection = client.create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"}
    )
    
    return collection

