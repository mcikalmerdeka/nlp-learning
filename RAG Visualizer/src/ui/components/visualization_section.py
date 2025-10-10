"""Visualization section component"""

import streamlit as st
import numpy as np
from src.core.visualization import reduce_dimensions, create_3d_plot
from src.core.models import load_model


def render_visualization_section(reduction_method: str, model_name: str):
    """Render the 3D visualization section
    
    Args:
        reduction_method: Method for dimensionality reduction
        model_name: Name of the model being used
    """
    st.subheader("🎨 3D Embedding Space")
    
    with st.spinner("Reducing dimensions and creating visualization..."):
        # Reduce dimensions
        reduced_embeddings = reduce_dimensions(
            st.session_state.embeddings,
            method=reduction_method.lower(),
            n_components=3
        )
        
        # Get selected indices and query point if available
        selected_indices = None
        query_point = None
        
        if hasattr(st.session_state, 'query_results') and hasattr(st.session_state, 'query_embedding'):
            # Get indices of retrieved chunks
            result_ids = st.session_state.query_results['ids'][0]
            selected_indices = [int(id.split('_')[1]) for id in result_ids]
            
            # Reduce query embedding dimensions
            model = load_model(model_name)
            combined = np.vstack([st.session_state.embeddings, 
                                 st.session_state.query_embedding.reshape(1, -1)])
            reduced_combined = reduce_dimensions(combined, method=reduction_method.lower(), n_components=3)
            query_point = reduced_combined[-1]
        
        # Create plot
        fig = create_3d_plot(
            reduced_embeddings, 
            st.session_state.chunks,
            selected_indices,
            query_point
        )
        
        st.plotly_chart(fig, use_container_width=True)

