"""Session state initialization"""

import streamlit as st


def initialize_session_state():
    """Initialize all session state variables"""
    # Retrieval section
    if 'embeddings_generated' not in st.session_state:
        st.session_state.embeddings_generated = False
    if 'collection' not in st.session_state:
        st.session_state.collection = None
    if 'chunks' not in st.session_state:
        st.session_state.chunks = []
    if 'embeddings' not in st.session_state:
        st.session_state.embeddings = []
    if 'query_results' not in st.session_state:
        st.session_state.query_results = None
    if 'query_embedding' not in st.session_state:
        st.session_state.query_embedding = None
    if 'last_query' not in st.session_state:
        st.session_state.last_query = ""
    
    # Augmentation section
    if 'augmented_prompt' not in st.session_state:
        st.session_state.augmented_prompt = None
    if 'custom_system_prompt' not in st.session_state:
        st.session_state.custom_system_prompt = None
    if 'ready_for_generation' not in st.session_state:
        st.session_state.ready_for_generation = False
    
    # Generation section
    if 'llm_response' not in st.session_state:
        st.session_state.llm_response = None
    if 'generating' not in st.session_state:
        st.session_state.generating = False

