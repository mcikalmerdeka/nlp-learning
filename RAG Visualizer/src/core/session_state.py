"""Session state initialization"""

import streamlit as st


def initialize_session_state():
    """Initialize all session state variables"""
    if 'embeddings_generated' not in st.session_state:
        st.session_state.embeddings_generated = False
    if 'collection' not in st.session_state:
        st.session_state.collection = None
    if 'chunks' not in st.session_state:
        st.session_state.chunks = []
    if 'embeddings' not in st.session_state:
        st.session_state.embeddings = []

