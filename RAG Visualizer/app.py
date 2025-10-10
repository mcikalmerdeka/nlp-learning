"""RAG Embedding Visualizer - Main Application

A Streamlit application to visualize text embeddings and understand 
how Retrieval-Augmented Generation (RAG) systems work.
"""

import streamlit as st
from src.core import initialize_session_state
from src.ui import CUSTOM_CSS
from src.ui.components import (
    render_sidebar,
    render_input_section,
    render_query_section,
    render_stats_section,
    render_visualization_section,
    render_chunk_explorer
)


# Page config
st.set_page_config(
    page_title="RAG Embedding Visualizer",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Initialize session state
initialize_session_state()


def main():
    """Main application entry point"""
    # Header
    st.markdown(
        '<h1 class="main-header">🔍 RAG Embedding Visualizer</h1>', 
        unsafe_allow_html=True
    )
    st.markdown(
        '<p class="sub-header">Visualize text embeddings and vector similarity in 3D space with ChromaDB</p>', 
        unsafe_allow_html=True
    )
    
    # Sidebar configuration
    model_name, chunk_size, overlap, reduction_method, collection_name = render_sidebar()
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        render_input_section(model_name, chunk_size, overlap, collection_name)
    
    with col2:
        render_query_section(model_name)
    
    # Visualization section (only if embeddings are generated)
    if st.session_state.embeddings_generated:
        st.divider()
        render_stats_section(reduction_method)
        st.divider()
        render_visualization_section(reduction_method, model_name)
        st.divider()
        render_chunk_explorer()


if __name__ == "__main__":
    main()