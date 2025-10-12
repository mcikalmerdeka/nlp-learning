"""Sidebar component"""

import streamlit as st
from src.config import MODEL_OPTIONS, SAMPLE_TEXTS
from src.core.session_state import reset_embeddings_state


def render_sidebar():
    """Render the sidebar with configuration options
    
    Returns:
        Tuple of (model_name, chunk_size, overlap, reduction_method, collection_name)
    """
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Model selection
        selected_model = st.selectbox(
            "Embedding Model",
            options=list(MODEL_OPTIONS.keys()),
            help="Choose the sentence transformer model for embeddings"
        )
        
        model_name = MODEL_OPTIONS[selected_model]
        
        # Reset embeddings if model changed
        if st.session_state.current_model is not None and st.session_state.current_model != model_name:
            reset_embeddings_state()
            st.session_state.current_model = model_name
            st.rerun()
        
        st.session_state.current_model = model_name
        
        # Chunking parameters
        st.subheader("📝 Chunking Settings")
        chunk_size = st.slider("Chunk Size (words)", 50, 500, 100, 50)
        overlap = st.slider("Overlap (words)", 0, 100, 20, 10)
        
        # Dimensionality reduction
        st.subheader("📊 Visualization")
        reduction_method = st.selectbox(
            "Reduction Method",
            ["PCA", "UMAP"],
            help="Method to reduce embeddings to 3D"
        )
        
        # Collection name
        collection_name = st.text_input("ChromaDB Collection", "rag_embeddings")
        
        st.divider()
        
        # Sample texts
        st.subheader("📚 Sample Texts")
        sample_choice = st.selectbox("Choose sample:", list(SAMPLE_TEXTS.keys()))
        
        if st.button("Load Sample", use_container_width=True):
            st.session_state.sample_text = SAMPLE_TEXTS[sample_choice]
            st.rerun()
    
    return model_name, chunk_size, overlap, reduction_method, collection_name

