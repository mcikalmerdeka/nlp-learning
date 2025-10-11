"""Visualization and dimensionality reduction utilities"""

import numpy as np
import plotly.graph_objects as go
from sklearn.decomposition import PCA
import umap
from typing import List, Optional


def reduce_dimensions(embeddings: np.ndarray, method: str = "pca", n_components: int = 3):
    """Reduce embedding dimensions for visualization
    
    Args:
        embeddings: High-dimensional embeddings
        method: Reduction method ('pca' or 'umap')
        n_components: Number of dimensions to reduce to
        
    Returns:
        Reduced embeddings array
    """
    # Adjust n_components if we have fewer samples
    n_samples = embeddings.shape[0]
    actual_components = min(n_components, n_samples)
    
    if method == "pca":
        reducer = PCA(n_components=actual_components)
    elif method == "umap":
        # UMAP needs at least 2 samples
        if n_samples < 2:
            # If only 1 sample, pad with zeros for visualization
            reduced = np.zeros((n_samples, n_components))
            return reduced
        reducer = umap.UMAP(n_components=actual_components, random_state=42)
    else:
        raise ValueError("Method must be 'pca' or 'umap'")
    
    reduced = reducer.fit_transform(embeddings)
    
    # If we got fewer dimensions than requested, pad with zeros
    if reduced.shape[1] < n_components:
        padding = np.zeros((n_samples, n_components - reduced.shape[1]))
        reduced = np.hstack([reduced, padding])
    
    return reduced


def create_3d_plot(
    reduced_embeddings: np.ndarray, 
    chunks: List[str], 
    selected_indices: Optional[List[int]] = None, 
    query_point: Optional[np.ndarray] = None
):
    """Create interactive 3D scatter plot
    
    Args:
        reduced_embeddings: 3D embeddings to visualize
        chunks: Original text chunks
        selected_indices: Indices of selected/retrieved chunks
        query_point: Query point coordinates in 3D space
        
    Returns:
        Plotly figure object
    """
    # Ensure we have 3 dimensions for visualization
    if reduced_embeddings.shape[1] < 3:
        padding = np.zeros((reduced_embeddings.shape[0], 3 - reduced_embeddings.shape[1]))
        reduced_embeddings = np.hstack([reduced_embeddings, padding])
    
    # Truncate chunk labels for display
    labels = [chunk[:50] + "..." if len(chunk) > 50 else chunk for chunk in chunks]
    
    # Create colors based on selection
    colors = ['#667eea'] * len(chunks)
    sizes = [8] * len(chunks)
    
    if selected_indices:
        for idx in selected_indices:
            colors[idx] = '#ff6b6b'
            sizes[idx] = 12
    
    # Main scatter plot
    fig = go.Figure()
    
    # Add chunk points
    fig.add_trace(go.Scatter3d(
        x=reduced_embeddings[:, 0],
        y=reduced_embeddings[:, 1],
        z=reduced_embeddings[:, 2],
        mode='markers+text',
        marker=dict(
            size=sizes,
            color=colors,
            opacity=0.8,
            line=dict(color='white', width=0.5)
        ),
        text=[f"Chunk {i}" for i in range(len(chunks))],
        hovertemplate='<b>Chunk %{text}</b><br>' +
                      'X: %{x:.3f}<br>' +
                      'Y: %{y:.3f}<br>' +
                      'Z: %{z:.3f}<br>' +
                      '<extra></extra>',
        customdata=labels,
        name='Chunks'
    ))
    
    # Add query point if exists
    if query_point is not None:
        fig.add_trace(go.Scatter3d(
            x=[query_point[0]],
            y=[query_point[1]],
            z=[query_point[2]],
            mode='markers',
            marker=dict(
                size=15,
                color='#ffd93d',
                symbol='diamond',
                line=dict(color='white', width=2)
            ),
            name='Query',
            hovertemplate='<b>Query Point</b><br>' +
                          'X: %{x:.3f}<br>' +
                          'Y: %{y:.3f}<br>' +
                          'Z: %{z:.3f}<br>' +
                          '<extra></extra>'
        ))
    
    fig.update_layout(
        scene=dict(
            xaxis=dict(title='Dimension 1', backgroundcolor="rgb(20, 24, 54)", gridcolor="rgb(50, 54, 84)"),
            yaxis=dict(title='Dimension 2', backgroundcolor="rgb(20, 24, 54)", gridcolor="rgb(50, 54, 84)"),
            zaxis=dict(title='Dimension 3', backgroundcolor="rgb(20, 24, 54)", gridcolor="rgb(50, 54, 84)"),
            bgcolor="rgb(20, 24, 54)"
        ),
        paper_bgcolor="rgb(20, 24, 54)",
        plot_bgcolor="rgb(20, 24, 54)",
        font=dict(color="white"),
        height=700,
        showlegend=True,
        hovermode='closest'
    )
    
    return fig

