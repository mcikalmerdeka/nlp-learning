"""
Streamlit application using InMemoryVectorStore (for testing/development)
"""
import streamlit as st
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv

# Import configuration
from config import MODEL_OPTIONS, initialize_language_model

# Import core functionality
from core import (
    save_uploaded_file,
    load_pdf_documents,
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
    render_old_approach_flow_expander,
    render_model_selector,
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

"""
This uses InMemoryVectorStore instead of ChromaDB for document storage.
Suitable for development/testing or when persistence is not required.
"""

# Load environment variables
load_dotenv()

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'vector_store' not in st.session_state:
    st.session_state.vector_store = InMemoryVectorStoreWrapper()

# Apply custom theme
apply_custom_theme()

# Streamlit UI Configuration  
render_app_header("📘 DocuChat AI - InMemory", "InMemoryVectorStore Implementation")

# Render information expanders
render_app_info_expander()
render_old_approach_flow_expander()

# Sidebar components
render_clear_chat_button()
selected_model = render_model_selector(MODEL_OPTIONS)
external_search_enabled = render_external_search_toggle(EXTERNAL_SEARCH_AVAILABLE)

# Initialize the chosen language model
LANGUAGE_MODEL = initialize_language_model(selected_model)

# File Upload Section
uploaded_pdf = render_file_uploader()

# Main App Logic
if uploaded_pdf:
    saved_path = save_uploaded_file(uploaded_pdf)
    vector_store = st.session_state.vector_store
    
    # Check if document already exists before processing
    if not vector_store.document_exists(uploaded_pdf.name):
        raw_docs = load_pdf_documents(saved_path)
        processed_chunks = chunk_documents(raw_docs)
        vector_store.add_documents(processed_chunks)
        
        # Create the RAG chain
        retriever = vector_store.create_retriever(k=5)
        rag_chain = create_rag_chain(LANGUAGE_MODEL, retriever, external_search_enabled)
        
        # Store in session state
        st.session_state.retriever = retriever
        st.session_state.rag_chain = rag_chain
        
        # Display success message
        mode_info = "with External Search" if external_search_enabled else "Document Only Mode"
        render_status_message("success", "New document processed and added to vector store! Ask your questions below", 
                            model_name=selected_model, mode_info=mode_info)
    else:
        # Document already exists, just create retriever and chain
        retriever = vector_store.create_retriever(k=5)
        rag_chain = create_rag_chain(LANGUAGE_MODEL, retriever, external_search_enabled)
        
        # Store in session state
        st.session_state.retriever = retriever
        st.session_state.rag_chain = rag_chain
        
        # Display info message
        mode_info = "with External Search" if external_search_enabled else "Document Only Mode"
        render_status_message("info", f"Document '{uploaded_pdf.name}' already exists in vector store! You can ask questions about it", 
                            model_name=selected_model, mode_info=mode_info)

    # Display existing chat history
    display_chat_history()
    
    # Handle new user input
    user_input = st.chat_input("Enter your question about the document...")
    
    if user_input:
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        # Dynamic spinner message based on mode
        spinner_message = "Analyzing document with AI (external search enabled)..." if external_search_enabled else "Analyzing document with AI (document only mode)..."
        
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
