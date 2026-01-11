"""
Vector store management for document retrieval
"""
import os
from langchain_chroma import Chroma
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings
from config.settings import (
    EMBEDDING_MODEL_NAME,
    CHROMA_PERSIST_DIR,
    CHROMA_COLLECTION_NAME,
    DEFAULT_RETRIEVAL_K
)


def get_embedding_model():
    """Get the configured embedding model"""
    return OpenAIEmbeddings(
        api_key=os.getenv("OPENAI_API_KEY"),
        model=EMBEDDING_MODEL_NAME
    )


class ChromaVectorStore:
    """Wrapper for ChromaDB vector store operations"""
    
    def __init__(self):
        self.embedding_model = get_embedding_model()
        self.vector_db = Chroma(
            embedding_function=self.embedding_model,
            collection_name=CHROMA_COLLECTION_NAME,
            persist_directory=CHROMA_PERSIST_DIR
        )
    
    def add_documents(self, document_chunks):
        """Add document chunks to the vector store"""
        if not document_chunks:
            raise ValueError("No document chunks to index. The document may be empty or failed to load.")
        self.vector_db.add_documents(document_chunks)
    
    def document_exists(self, file_name: str) -> bool:
        """Check if document already exists in vector store"""
        try:
            existing_docs = self.vector_db.get()
            if existing_docs and 'metadatas' in existing_docs:
                existing_files = [doc.get('source', '') for doc in existing_docs['metadatas'] if doc]
                return any(file_name in file_path for file_path in existing_files)
        except:
            pass
        return False
    
    def create_retriever(self, k: int = DEFAULT_RETRIEVAL_K):
        """Create a retriever from the vector store"""
        return self.vector_db.as_retriever(search_kwargs={"k": k})
    
    def reset(self):
        """Reset or initialize vector store"""
        try:
            self.vector_db.delete_collection()
        except:
            pass
        self.vector_db = Chroma(
            embedding_function=self.embedding_model,
            collection_name=CHROMA_COLLECTION_NAME,
            persist_directory=CHROMA_PERSIST_DIR
        )
        return self.vector_db


class InMemoryVectorStoreWrapper:
    """Wrapper for InMemoryVectorStore operations"""
    
    def __init__(self):
        self.embedding_model = get_embedding_model()
        self.vector_db = InMemoryVectorStore(self.embedding_model)
    
    def add_documents(self, document_chunks):
        """Add document chunks to the vector store"""
        self.vector_db.add_documents(document_chunks)
    
    def document_exists(self, file_name: str) -> bool:
        """Check if document already exists in vector store"""
        try:
            stored_docs = self.vector_db.similarity_search("", k=1000)
            if stored_docs:
                existing_files = [doc.metadata.get('source', '') for doc in stored_docs if hasattr(doc, 'metadata')]
                return any(file_name in file_path for file_path in existing_files)
        except:
            pass
        return False
    
    def create_retriever(self, k: int = DEFAULT_RETRIEVAL_K):
        """Create a retriever from the vector store"""
        return self.vector_db.as_retriever(search_kwargs={"k": k})
