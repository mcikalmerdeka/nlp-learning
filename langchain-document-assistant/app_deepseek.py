"""
Streamlit application using DeepSeek R1 local LLM with Ollama
Uses InMemoryVectorStore and PDFPlumberLoader for better local processing
"""
import streamlit as st
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
from langchain_community.document_loaders import PDFPlumberLoader
from langchain_ollama import OllamaEmbeddings
from langchain_ollama.llms import OllamaLLM
from langchain_openai import OpenAIEmbeddings

# Import configuration
from config import DEFAULT_CHUNK_SIZE, DEFAULT_CHUNK_OVERLAP, PDF_STORAGE_PATH

# Import core functionality
from core import (
    chunk_documents,
    InMemoryVectorStoreWrapper,
    create_rag_chain,
    generate_enhanced_answer
)

# Import UI components
from styles import apply_custom_theme
from components import (
    render_app_header,
    render_app_info_expander,
    render_deepseek_flow_expander,
    render_external_search_toggle,
    render_clear_chat_button,
    render_file_uploader,
    display_chat_history,
    render_status_message
)

# Check external search availability
try:
    from agents.external_sources_lookup_agent import lookup
    EXTERNAL_SEARCH_AVAILABLE = True
except ImportError as e:
    st.warning(f"External search not available: {e}")
    EXTERNAL_SEARCH_AVAILABLE = False

# Load environment variables
load_dotenv()

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Apply custom theme
apply_custom_theme()

# DeepSeek-specific configurations
DEEPSEEK_MODEL = "deepseek-r1:1.5b"

# Choose embedding model (OpenAI recommended for better quality)
USE_OPENAI_EMBEDDINGS = True

if USE_OPENAI_EMBEDDINGS:
    EMBEDDING_MODEL = OpenAIEmbeddings(
        api_key=os.getenv("OPENAI_API_KEY"),
        model="text-embedding-3-large"
    )
else:
    EMBEDDING_MODEL = OllamaEmbeddings(model=DEEPSEEK_MODEL)

# Initialize vector store with chosen embeddings
if 'vector_store' not in st.session_state:
    from langchain_core.vectorstores import InMemoryVectorStore
    st.session_state.vector_store = InMemoryVectorStore(EMBEDDING_MODEL)

# Initialize DeepSeek language model
LANGUAGE_MODEL = OllamaLLM(model=DEEPSEEK_MODEL)


def save_uploaded_file(uploaded_file):
    """Save uploaded PDF file"""
    file_path = PDF_STORAGE_PATH + uploaded_file.name
    with open(file_path, "wb") as file:
        file.write(uploaded_file.getbuffer())
    return file_path


def load_pdf_documents(file_path):
    """Load PDF documents using PDFPlumberLoader (better for complex PDFs)"""
    document_loader = PDFPlumberLoader(file_path)
    return document_loader.load()


# Streamlit UI Configuration
render_app_header("📘 DocuChat AI - DeepSeek R1", "Local LLM with Ollama Integration")

# Render information expanders
render_app_info_expander()
render_deepseek_flow_expander()

# Sidebar components
render_clear_chat_button()
external_search_enabled = render_external_search_toggle(EXTERNAL_SEARCH_AVAILABLE)

# File Upload Section
uploaded_pdf = render_file_uploader()

# Main App Logic
if uploaded_pdf:
    saved_path = save_uploaded_file(uploaded_pdf)
    vector_store = st.session_state.vector_store
    
    # Always process (no duplicate check for InMemory store in DeepSeek version)
    raw_docs = load_pdf_documents(saved_path)
    processed_chunks = chunk_documents(raw_docs)
    vector_store.add_documents(processed_chunks)
    
    # Create the RAG chain
    retriever = vector_store.as_retriever(search_kwargs={"k": 5})
    rag_chain = create_rag_chain(LANGUAGE_MODEL, retriever, external_search_enabled)
    
    # Store in session state
    st.session_state.retriever = retriever
    st.session_state.rag_chain = rag_chain
    
    # Display success message
    mode_info = "with External Search" if external_search_enabled else "Document Only Mode"
    render_status_message("success", "Document processed successfully! Ask your questions below", 
                        model_name="DeepSeek R1", mode_info=mode_info)

    # Display existing chat history
    display_chat_history()
    
    # Handle new user input
    user_input = st.chat_input("Enter your question about the document...")
    
    if user_input:
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        # Dynamic spinner message based on mode
        spinner_message = "Analyzing document with DeepSeek R1 (external search enabled)..." if external_search_enabled else "Analyzing document with DeepSeek R1 (document only mode)..."
        
        with st.spinner(spinner_message):
            # Use the enhanced answer generation
            ai_response = generate_enhanced_answer(
                user_input, 
                st.session_state.rag_chain, 
                LANGUAGE_MODEL,
                st.session_state.retriever,
                external_search_enabled,
                EXTERNAL_SEARCH_AVAILABLE
            )
            
            # Add assistant response to chat history
            st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
        
        # Rerun to display the updated chat history
        st.rerun()
