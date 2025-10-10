"""Query section component"""

import streamlit as st
from src.core.models import load_model


def render_query_section(model_name: str):
    """Render the query section for semantic search
    
    Args:
        model_name: Name of the model to use for query encoding
    """
    st.subheader("🔎 Query & Search")
    
    # Query input
    query_text = st.text_input(
        "Enter a query to find similar chunks:",
        placeholder="e.g., 'What is machine learning?'"
    )
    
    n_results = st.slider("Number of results", 1, 10, 3)
    
    query_button = st.button("Search Similar Chunks", use_container_width=True)
    
    # Display results
    if query_button and st.session_state.embeddings_generated:
        if not query_text.strip():
            st.warning("Please enter a query!")
        else:
            with st.spinner("Searching..."):
                model = load_model(model_name)
                query_embedding = model.encode([query_text])[0]
                
                # Query ChromaDB
                results = st.session_state.collection.query(
                    query_embeddings=[query_embedding.tolist()],
                    n_results=n_results
                )
                
                st.session_state.query_results = results
                st.session_state.query_embedding = query_embedding
                
            st.success(f"Found {len(results['documents'][0])} similar chunks!")
            
            # Display results
            for i, (doc, distance, chunk_id) in enumerate(zip(
                results['documents'][0], 
                results['distances'][0],
                results['ids'][0]
            )):
                similarity = 1 - distance
                # Extract chunk number from ID (e.g., "chunk_5" -> 5)
                chunk_number = int(chunk_id.split('_')[1])
                
                with st.expander(f"Result {i+1} - Chunk {chunk_number} - Similarity: {similarity:.3f}"):
                    st.write(doc)

