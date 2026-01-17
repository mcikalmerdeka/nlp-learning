"""RAG (Retrieval-Augmented Generation) functionality"""

import os
import streamlit as st
from typing import List
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from config import EMBEDDING_MODEL, FAISS_INDEX_PATH, SCHEMA_PATH_MULTI


def load_schema_description() -> str:
    """
    Load database schema description from local file
        
    Returns:
        Schema description text
    """
    try:
        with open(SCHEMA_PATH_MULTI, "r", encoding="utf-8") as file:
            return file.read()
    except Exception as e:
        st.error(f"Error reading schema file: {e}")
        return ""


def chunk_schema_text(content: str) -> List[str]:
    """
    Split schema text into meaningful chunks
    
    Args:
        content: Full schema text
        
    Returns:
        List of text chunks
    """
    # Split by major headings
    major_sections = content.split('\n#')
    
    chunks = []
    if major_sections[0]:
        chunks.append(major_sections[0])
    
    for section in major_sections[1:]:
        section = '#' + section
        
        # Further split table collection sections
        if "table collections" in section.lower():
            table_sections = section.split('\n ')
            for t_section in table_sections:
                if t_section.strip() and len(t_section) > 50:
                    chunks.append(t_section.strip())
        else:
            chunks.append(section.strip())
    
    return [chunk for chunk in chunks if chunk and len(chunk) > 50]


class RAGEngine:
    """Handle RAG operations for schema retrieval"""
    
    def __init__(self, recreate_index: bool = False):
        """
        Initialize RAG engine
        
        Args:
            recreate_index: Whether to recreate the FAISS index
        """
        self.embedding_model = OpenAIEmbeddings(model=EMBEDDING_MODEL)
        self.vector_store = self._load_or_create_index(recreate_index)
    
    def _load_or_create_index(self, recreate: bool = False) -> FAISS:
        """Load existing or create new FAISS index"""
        if recreate and os.path.exists(FAISS_INDEX_PATH):
            import shutil
            try:
                shutil.rmtree(FAISS_INDEX_PATH)
                st.info("Recreating vector index with proper text chunking...")
            except Exception as e:
                st.warning(f"Could not remove old index: {e}")
        
        # Load schema and create chunks
        schema_content = load_schema_description()
        if not schema_content:
            st.error("Failed to load schema description!")
            return None
        
        chunks = chunk_schema_text(schema_content)
        if not chunks:
            st.error("No valid chunks created from schema!")
            return None
        
        # Create FAISS index
        vector_store = FAISS.from_texts(chunks, embedding=self.embedding_model)
        vector_store.save_local(FAISS_INDEX_PATH)
        
        return vector_store
    
    def retrieve_relevant_schema(self, query: str, k: int = 5) -> List[Document]:
        """
        Retrieve relevant schema chunks for a query
        
        Args:
            query: User question
            k: Number of chunks to retrieve
            
        Returns:
            List of relevant document chunks
        """
        if not self.vector_store:
            st.error("Vector store not initialized!")
            return []
        
        return self.vector_store.similarity_search(query, k=k)
    
    def get_retrieved_schema_text(self, query: str, k: int = 5) -> str:
        """
        Get retrieved schema as concatenated text
        
        Args:
            query: User question
            k: Number of chunks to retrieve
            
        Returns:
            Concatenated schema text
        """
        docs = self.retrieve_relevant_schema(query, k)
        return "\n".join([doc.page_content for doc in docs])
