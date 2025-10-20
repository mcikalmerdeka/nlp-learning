"""Network graph visualization for semantic relationships between chunks"""

import numpy as np
import plotly.graph_objects as go
import networkx as nx
from typing import List, Optional, Tuple
from sklearn.metrics.pairwise import cosine_similarity


def find_semantic_neighbors(
    embeddings: np.ndarray,
    n_neighbors: int = 5,
    similarity_threshold: float = 0.3
) -> dict:
    """Find semantic neighbors for each chunk based on embedding similarity
    
    Args:
        embeddings: Array of chunk embeddings
        n_neighbors: Number of neighbors to find for each chunk
        similarity_threshold: Minimum similarity score to consider as neighbor
        
    Returns:
        Dictionary mapping chunk index to list of (neighbor_index, similarity_score) tuples
    """
    # Compute cosine similarity matrix
    similarity_matrix = cosine_similarity(embeddings)
    
    neighbors_dict = {}
    
    for i in range(len(embeddings)):
        # Get similarities for this chunk (excluding itself)
        similarities = similarity_matrix[i].copy()
        similarities[i] = -1  # Exclude self
        
        # Get top N neighbors above threshold
        top_indices = np.argsort(similarities)[::-1][:n_neighbors]
        
        neighbors = []
        for idx in top_indices:
            score = similarities[idx]
            if score >= similarity_threshold:
                neighbors.append((int(idx), float(score)))
        
        neighbors_dict[i] = neighbors
    
    return neighbors_dict


def create_network_graph(
    embeddings: np.ndarray,
    chunks: List[str],
    neighbors_dict: dict,
    selected_indices: Optional[List[int]] = None,
    query_index: Optional[int] = None,
    layout_algorithm: str = "spring"
) -> go.Figure:
    """Create interactive network graph visualization
    
    Args:
        embeddings: Array of chunk embeddings
        chunks: List of text chunks
        neighbors_dict: Dictionary of semantic neighbors
        selected_indices: Indices of retrieved/selected chunks
        query_index: Index of query point (if added to embeddings)
        layout_algorithm: Graph layout algorithm ('spring', 'circular', 'kamada_kawai')
        
    Returns:
        Plotly figure object
    """
    # Create NetworkX graph
    G = nx.Graph()
    
    # Add nodes
    for i in range(len(chunks)):
        G.add_node(i)
    
    # Add edges based on semantic neighbors
    edge_weights = []
    for node, neighbors in neighbors_dict.items():
        for neighbor_idx, similarity in neighbors:
            if node < neighbor_idx:  # Avoid duplicate edges
                G.add_edge(node, neighbor_idx, weight=similarity)
                edge_weights.append(similarity)
    
    # Choose layout algorithm
    if layout_algorithm == "spring":
        pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
    elif layout_algorithm == "circular":
        pos = nx.circular_layout(G)
    elif layout_algorithm == "kamada_kawai":
        pos = nx.kamada_kawai_layout(G)
    else:
        pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
    
    # Scale positions for better visualization
    scale = 500
    for node in pos:
        pos[node] = (pos[node][0] * scale, pos[node][1] * scale)
    
    # Create edge traces
    edge_traces = []
    
    # Normalize edge weights for opacity
    if edge_weights:
        min_weight = min(edge_weights)
        max_weight = max(edge_weights)
        weight_range = max_weight - min_weight if max_weight > min_weight else 1
    else:
        min_weight = 0
        weight_range = 1
    
    for edge in G.edges(data=True):
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        weight = edge[2].get('weight', 0.5)
        
        # Calculate opacity based on similarity
        opacity = 0.2 + 0.6 * ((weight - min_weight) / weight_range)
        
        edge_trace = go.Scatter(
            x=[x0, x1, None],
            y=[y0, y1, None],
            mode='lines',
            line=dict(
                width=1 + 2 * ((weight - min_weight) / weight_range),
                color=f'rgba(150, 150, 150, {opacity})'
            ),
            hoverinfo='none',
            showlegend=False
        )
        edge_traces.append(edge_trace)
    
    # Prepare node data
    node_x = []
    node_y = []
    node_text = []
    node_colors = []
    node_sizes = []
    node_hover = []
    node_opacities = []
    
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        
        # Truncate chunk text for display
        chunk_preview = chunks[node][:60] + "..." if len(chunks[node]) > 60 else chunks[node]
        node_text.append(f"C{node}")
        
        # Get neighbor info for hover
        neighbor_info = []
        if node in neighbors_dict:
            for neighbor_idx, similarity in neighbors_dict[node][:3]:
                neighbor_preview = chunks[neighbor_idx][:40] + "..."
                neighbor_info.append(f"  • C{neighbor_idx} ({similarity:.2f}): {neighbor_preview}")
        
        neighbor_text = "<br>".join(neighbor_info) if neighbor_info else "No close neighbors"
        
        node_hover.append(
            f"<b>Chunk {node}</b><br>" +
            f"{chunk_preview}<br><br>" +
            f"<b>Similar chunks:</b><br>{neighbor_text}"
        )
        
        # Color and size based on selection
        if query_index is not None and node == query_index:
            node_colors.append('#ffd93d')  # Yellow for query
            node_sizes.append(20)
            node_opacities.append(1.0)
        elif selected_indices and node in selected_indices:
            node_colors.append('#ff6b6b')  # Red for retrieved
            node_sizes.append(16)
            node_opacities.append(0.9)
        else:
            node_colors.append('#667eea')  # Purple for regular
            node_sizes.append(12)
            node_opacities.append(0.7)
    
    # Create node trace
    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode='markers+text',
        text=node_text,
        textposition="top center",
        textfont=dict(size=10, color='white'),
        marker=dict(
            size=node_sizes,
            color=node_colors,
            opacity=node_opacities,
            line=dict(color='white', width=1.5)
        ),
        hovertemplate='%{hovertext}<extra></extra>',
        hovertext=node_hover,
        showlegend=False
    )
    
    # Create figure
    fig = go.Figure(data=edge_traces + [node_trace])
    
    # Update layout
    fig.update_layout(
        title=dict(
            text="Semantic Network: Chunks Connected by Similarity",
            font=dict(size=16, color='white')
        ),
        showlegend=False,
        hovermode='closest',
        paper_bgcolor='rgb(20, 24, 54)',
        plot_bgcolor='rgb(20, 24, 54)',
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            showline=False
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            showline=False,
            scaleanchor="x",
            scaleratio=1
        ),
        height=700,
        margin=dict(l=20, r=20, t=60, b=20)
    )
    
    return fig


def create_2d_scatter_with_neighbors(
    embeddings: np.ndarray,
    chunks: List[str],
    neighbors_dict: dict,
    selected_indices: Optional[List[int]] = None,
    query_point: Optional[np.ndarray] = None,
    reduction_method: str = "pca"
) -> go.Figure:
    """Create 2D scatter plot with neighbor connections
    
    Args:
        embeddings: Array of chunk embeddings (already reduced to 2D)
        chunks: List of text chunks
        neighbors_dict: Dictionary of semantic neighbors
        selected_indices: Indices of retrieved/selected chunks
        query_point: Query point coordinates in 2D space
        reduction_method: Method used for reduction (for title)
        
    Returns:
        Plotly figure object
    """
    fig = go.Figure()
    
    # Add connection lines for neighbors
    for node, neighbors in neighbors_dict.items():
        for neighbor_idx, similarity in neighbors:
            if node < neighbor_idx:  # Avoid duplicate lines
                opacity = 0.1 + 0.4 * similarity
                fig.add_trace(go.Scatter(
                    x=[embeddings[node, 0], embeddings[neighbor_idx, 0]],
                    y=[embeddings[node, 1], embeddings[neighbor_idx, 1]],
                    mode='lines',
                    line=dict(
                        width=0.5 + similarity,
                        color=f'rgba(150, 150, 150, {opacity})'
                    ),
                    hoverinfo='skip',
                    showlegend=False
                ))
    
    # Prepare node data
    colors = []
    sizes = []
    labels = []
    
    for i in range(len(chunks)):
        chunk_preview = chunks[i][:50] + "..." if len(chunks[i]) > 50 else chunks[i]
        labels.append(chunk_preview)
        
        if selected_indices and i in selected_indices:
            colors.append('#ff6b6b')
            sizes.append(12)
        else:
            colors.append('#667eea')
            sizes.append(8)
    
    # Add chunk points
    fig.add_trace(go.Scatter(
        x=embeddings[:, 0],
        y=embeddings[:, 1],
        mode='markers+text',
        text=[f"C{i}" for i in range(len(chunks))],
        textposition='top center',
        textfont=dict(size=8, color='white'),
        marker=dict(
            size=sizes,
            color=colors,
            opacity=0.8,
            line=dict(color='white', width=0.5)
        ),
        customdata=labels,
        hovertemplate='<b>Chunk %{text}</b><br>%{customdata}<extra></extra>',
        showlegend=False
    ))
    
    # Add query point if exists
    if query_point is not None:
        fig.add_trace(go.Scatter(
            x=[query_point[0]],
            y=[query_point[1]],
            mode='markers+text',
            text=['Q'],
            textposition='top center',
            marker=dict(
                size=15,
                color='#ffd93d',
                symbol='diamond',
                line=dict(color='white', width=2)
            ),
            name='Query',
            hovertemplate='<b>Query Point</b><extra></extra>',
            showlegend=False
        ))
    
    fig.update_layout(
        title=dict(
            text=f"2D Embedding Space ({reduction_method.upper()}) with Semantic Connections",
            font=dict(size=16, color='white')
        ),
        paper_bgcolor='rgb(20, 24, 54)',
        plot_bgcolor='rgb(20, 24, 54)',
        xaxis=dict(
            title='Dimension 1',
            showgrid=True,
            gridcolor='rgb(50, 54, 84)',
            zeroline=False,
            color='white'
        ),
        yaxis=dict(
            title='Dimension 2',
            showgrid=True,
            gridcolor='rgb(50, 54, 84)',
            zeroline=False,
            color='white',
            scaleanchor="x",
            scaleratio=1
        ),
        height=700,
        hovermode='closest'
    )
    
    return fig