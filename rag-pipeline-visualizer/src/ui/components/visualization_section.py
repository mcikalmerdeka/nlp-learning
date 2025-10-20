"""Visualization section component"""

import streamlit as st
import numpy as np
from src.core.visualization import reduce_dimensions, create_3d_plot
from src.core.network_visualization import (
    find_semantic_neighbors,
    create_network_graph,
    create_2d_scatter_with_neighbors
)
from src.core.models import load_model


def render_visualization_section(reduction_method: str, model_name: str):
    """Render the visualization section with multiple view options
    
    Args:
        reduction_method: Method for dimensionality reduction
        model_name: Name of the model being used
    """
    st.subheader("🎨 Embedding Space Visualization")
    
    # Add explanation about visualization modes
    st.markdown("""
    <div style='background-color: rgba(102, 126, 234, 0.1); padding: 15px; border-radius: 10px; margin-bottom: 20px;'>
        <h4 style='margin-top: 0; color: #667eea;'>📊 Understanding Visualization Modes</h4>
        <ul style='margin-bottom: 0;'>
            <li><b>3D Scatter Plot</b>: Shows chunks as points in 3D space. Best for seeing overall distribution and spatial relationships.</li>
            <li><b>2D Network Graph</b>: Displays chunks as connected nodes. Best for discovering semantic clusters and relationships.</li>
            <li><b>2D Scatter with Connections</b>: Combines spatial layout with similarity connections. Best for understanding both position and relationships.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Visualization mode selector
    viz_mode = st.radio(
        "Visualization Mode",
        options=["3D Scatter Plot", "2D Network Graph", "2D Scatter with Connections"],
        horizontal=True,
        help="Choose how to visualize the embedding space"
    )
    
    # Advanced settings in expander
    with st.expander("⚙️ Visualization Settings", expanded=False):
        st.markdown("""
        <div style='background-color: rgba(255, 193, 7, 0.1); padding: 10px; border-radius: 5px; margin-bottom: 15px;'>
            <small><b>💡 Tip:</b> Adjust these settings to control how semantic relationships are displayed.</small>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Semantic Neighbors**")
            st.caption("How many similar chunks to connect for each chunk")
            n_neighbors = st.slider(
                "Number of neighbors",
                min_value=2,
                max_value=10,
                value=5,
                help="Higher values show more connections but may clutter the visualization",
                label_visibility="collapsed"
            )
            st.markdown("""
            <small>
            • <b>Low (2-3)</b>: Only strongest relationships<br>
            • <b>Medium (4-6)</b>: Balanced view (recommended)<br>
            • <b>High (7-10)</b>: Comprehensive network
            </small>
            """, unsafe_allow_html=True)
            
        with col2:
            st.markdown("**Similarity Threshold**")
            st.caption("Minimum similarity score to show a connection")
            similarity_threshold = st.slider(
                "Threshold value",
                min_value=0.0,
                max_value=1.0,
                value=0.3,
                step=0.05,
                help="Higher values show only very similar chunks",
                label_visibility="collapsed"
            )
            st.markdown("""
            <small>
            • <b>Low (0.2-0.4)</b>: More connections, broader view<br>
            • <b>Medium (0.4-0.6)</b>: Balanced (recommended)<br>
            • <b>High (0.6-0.8)</b>: Only very similar chunks
            </small>
            """, unsafe_allow_html=True)
        
        if viz_mode == "2D Network Graph":
            st.markdown("---")
            st.markdown("**Graph Layout Algorithm**")
            st.caption("How to position nodes in the network")
            layout_algo = st.selectbox(
                "Layout algorithm",
                options=["spring", "circular", "kamada_kawai"],
                help="Different algorithms reveal different patterns",
                label_visibility="collapsed"
            )
            st.markdown("""
            <small>
            • <b>Spring</b>: Natural clustering, nodes repel/attract (recommended)<br>
            • <b>Circular</b>: Organized in a circle, good for small datasets<br>
            • <b>Kamada-Kawai</b>: Balanced energy layout, minimizes edge crossings
            </small>
            """, unsafe_allow_html=True)
    
    with st.spinner("Creating visualization..."):
        # Get selected indices and query info
        selected_indices = None
        query_point = None
        
        if (hasattr(st.session_state, 'query_results') and
            hasattr(st.session_state, 'query_embedding') and
            st.session_state.query_results is not None and
            st.session_state.query_embedding is not None):
            result_ids = st.session_state.query_results['ids'][0]
            selected_indices = [int(id.split('_')[1]) for id in result_ids]
        
        # Create visualization based on mode
        if viz_mode == "3D Scatter Plot":
            # Original 3D visualization
            reduced_embeddings = reduce_dimensions(
                st.session_state.embeddings,
                method=reduction_method.lower(),
                n_components=3
            )
            
            if selected_indices and st.session_state.query_embedding is not None:
                model = load_model(model_name)
                combined = np.vstack([st.session_state.embeddings,
                                     st.session_state.query_embedding.reshape(1, -1)])
                reduced_combined = reduce_dimensions(combined, method=reduction_method.lower(), n_components=3)
                query_point = reduced_combined[-1]
            
            fig = create_3d_plot(
                reduced_embeddings,
                st.session_state.chunks,
                selected_indices,
                query_point
            )
            
        elif viz_mode == "2D Network Graph":
            # Network graph visualization
            neighbors_dict = find_semantic_neighbors(
                st.session_state.embeddings,
                n_neighbors=n_neighbors,
                similarity_threshold=similarity_threshold
            )
            
            fig = create_network_graph(
                st.session_state.embeddings,
                st.session_state.chunks,
                neighbors_dict,
                selected_indices=selected_indices,
                layout_algorithm=layout_algo
            )
            
        else:  # 2D Scatter with Connections
            # 2D scatter with neighbor connections
            reduced_embeddings = reduce_dimensions(
                st.session_state.embeddings,
                method=reduction_method.lower(),
                n_components=2
            )
            
            neighbors_dict = find_semantic_neighbors(
                st.session_state.embeddings,
                n_neighbors=n_neighbors,
                similarity_threshold=similarity_threshold
            )
            
            if selected_indices and st.session_state.query_embedding is not None:
                model = load_model(model_name)
                combined = np.vstack([st.session_state.embeddings,
                                     st.session_state.query_embedding.reshape(1, -1)])
                reduced_combined = reduce_dimensions(combined, method=reduction_method.lower(), n_components=2)
                query_point = reduced_combined[-1]
            
            fig = create_2d_scatter_with_neighbors(
                reduced_embeddings,
                st.session_state.chunks,
                neighbors_dict,
                selected_indices=selected_indices,
                query_point=query_point,
                reduction_method=reduction_method
            )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Add detailed explanation based on visualization mode
        st.markdown("---")
        if viz_mode == "2D Network Graph":
            st.markdown("""
            <div style='background-color: rgba(102, 126, 234, 0.1); padding: 15px; border-radius: 10px;'>
                <h4 style='margin-top: 0; color: #667eea;'>🕸️ How to Read the Network Graph</h4>
                <ul style='margin-bottom: 0;'>
                    <li><b>Nodes (circles)</b>: Each represents a text chunk</li>
                    <li><b>Lines (edges)</b>: Connect semantically similar chunks</li>
                    <li><b>Line thickness</b>: Thicker = higher similarity</li>
                    <li><b>Node clusters</b>: Groups of related content</li>
                    <li><b>Colors</b>: 🟣 Regular chunks | 🔴 Retrieved chunks | 🟡 Query</li>
                    <li><b>Hover</b>: See chunk content and its similar neighbors</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        elif viz_mode == "2D Scatter with Connections":
            st.markdown("""
            <div style='background-color: rgba(102, 126, 234, 0.1); padding: 15px; border-radius: 10px;'>
                <h4 style='margin-top: 0; color: #667eea;'>📍 How to Read the 2D Scatter Plot</h4>
                <ul style='margin-bottom: 0;'>
                    <li><b>Position</b>: Shows embedding space after dimensionality reduction</li>
                    <li><b>Proximity</b>: Closer points = more semantically similar</li>
                    <li><b>Lines</b>: Connect chunks above similarity threshold</li>
                    <li><b>Line opacity</b>: More opaque = higher similarity</li>
                    <li><b>Colors</b>: 🟣 Regular chunks | 🔴 Retrieved chunks | 🟡 Query</li>
                    <li><b>Axes</b>: Principal components from PCA/UMAP reduction</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style='background-color: rgba(102, 126, 234, 0.1); padding: 15px; border-radius: 10px;'>
                <h4 style='margin-top: 0; color: #667eea;'>🎯 How to Read the 3D Scatter Plot</h4>
                <ul style='margin-bottom: 0;'>
                    <li><b>Each point</b>: Represents one text chunk in 3D space</li>
                    <li><b>Position</b>: Determined by embedding similarity (closer = more similar)</li>
                    <li><b>Colors</b>: 🟣 Regular chunks | 🔴 Retrieved chunks | 🟡 Query point</li>
                    <li><b>Interaction</b>: Rotate, zoom, and hover to explore</li>
                    <li><b>Axes</b>: Three principal components from dimensionality reduction</li>
                    <li><b>Clusters</b>: Groups of points indicate related content</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

