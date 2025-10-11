"""Stats section component"""

import streamlit as st


def render_stats_section(reduction_method: str):
    """Render statistics cards
    
    Args:
        reduction_method: The reduction method being used
    """
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <p class="stat-number">{len(st.session_state.chunks)}</p>
            <p class="stat-label">Total Chunks</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <p class="stat-number">{st.session_state.embeddings.shape[1]}</p>
            <p class="stat-label">Embedding Dimensions</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stat-card">
            <p class="stat-number">{reduction_method}</p>
            <p class="stat-label">Reduction Method</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="stat-card">
            <p class="stat-number">3D</p>
            <p class="stat-label">Visualization Space</p>
        </div>
        """, unsafe_allow_html=True)

