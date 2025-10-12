"""RAG Embedding Visualizer - Main Application

A Streamlit application to visualize the complete RAG pipeline:
Retrieval, Augmentation, and Generation.
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
    render_chunk_explorer,
    render_augmentation_section,
    render_generation_section,
    render_rag_explanation
)


# Page config
st.set_page_config(
    page_title="RAG Pipeline Visualizer",
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
        '<h1 class="main-header">🔍 RAG Pipeline Visualizer</h1>', 
        unsafe_allow_html=True
    )
    st.markdown(
        '<p class="sub-header">Visualize the complete RAG pipeline: Retrieval → Augmentation → Generation</p>', 
        unsafe_allow_html=True
    )
    
    # RAG Explanation Section
    render_rag_explanation()
    
    # Sidebar configuration
    model_name, chunk_size, overlap, reduction_method, collection_name = render_sidebar()
    
    st.divider()
    
    # ========== SECTION 1: RETRIEVAL ==========
    st.header("🔎 1. Retrieval")
    st.markdown("Generate embeddings, store in vector database, and search for similar chunks")
    
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
    
    st.divider()
    
    # ========== SECTION 2: AUGMENTATION ==========
    render_augmentation_section()
    
    st.divider()
    
    # ========== SECTION 3: GENERATION ==========
    render_generation_section()


if __name__ == "__main__":
    main()