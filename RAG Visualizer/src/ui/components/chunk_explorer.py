"""Chunk explorer component"""

import streamlit as st


def render_chunk_explorer():
    """Render the chunk explorer section for viewing individual chunks"""
    st.subheader("📋 Chunk Explorer")
    
    # Add informational box
    st.info(
        f"ℹ️ **Understanding Embeddings:** Each chunk has a **{st.session_state.embeddings.shape[1]}-dimensional** "
        f"embedding vector that captures its semantic meaning. The 3D visualization above uses **all {st.session_state.embeddings.shape[1]} dimensions** "
        f"(reduced via PCA/UMAP), not just the preview shown below. Dimensionality reduction preserves the most important "
        f"patterns so you can visualize high-dimensional relationships in 3D space."
    )
    
    chunk_idx = st.selectbox(
        "Select a chunk to view details:",
        range(len(st.session_state.chunks)),
        format_func=lambda x: f"Chunk {x}"
    )
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.text_area("Chunk Content", st.session_state.chunks[chunk_idx], height=150)
    
    with col2:
        st.write("**Embedding Vector (first 10 dims):**")
        st.caption(f"Preview of {st.session_state.embeddings.shape[1]}D vector")
        embedding_preview = st.session_state.embeddings[chunk_idx][:10]
        for i, val in enumerate(embedding_preview):
            st.text(f"[{i}]: {val:.4f}")

