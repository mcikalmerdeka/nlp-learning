"""Input section component"""

import streamlit as st
from src.core.models import load_model
from src.core.text_processing import chunk_text
from src.core.vector_store import create_chromadb_collection


def render_input_section(model_name: str, chunk_size: int, overlap: int, collection_name: str):
    """Render the input section for text upload and embedding generation
    
    Args:
        model_name: Name of the model to use
        chunk_size: Size of text chunks
        overlap: Overlap between chunks
        collection_name: Name of ChromaDB collection
    """
    st.subheader("📄 Input Text")
    
    # Text input
    text_input = st.text_area(
        "Enter your text or upload a file:",
        value=st.session_state.get('sample_text', ''),
        height=300,
        placeholder="Paste your text here or upload a .txt file below..."
    )
    
    # File upload
    uploaded_file = st.file_uploader("Or upload a text file", type=['txt'])
    
    if uploaded_file is not None:
        text_input = uploaded_file.read().decode('utf-8')
        st.success(f"Loaded {len(text_input)} characters from file!")
    
    # Generate embeddings button
    if st.button("🚀 Generate Embeddings", type="primary", use_container_width=True):
        if not text_input.strip():
            st.error("Please enter some text first!")
        else:
            with st.spinner("Loading model and generating embeddings..."):
                # Load model
                model = load_model(model_name)
                
                # Chunk text
                chunks = chunk_text(text_input, chunk_size, overlap)
                st.session_state.chunks = chunks
                
                # Generate embeddings
                embeddings = model.encode(chunks, show_progress_bar=False)
                st.session_state.embeddings = embeddings
                
                # Create ChromaDB collection
                collection = create_chromadb_collection(collection_name)
                
                # Add to ChromaDB
                collection.add(
                    embeddings=embeddings.tolist(),
                    documents=chunks,
                    ids=[f"chunk_{i}" for i in range(len(chunks))]
                )
                
                st.session_state.collection = collection
                st.session_state.embeddings_generated = True
                
            st.success(f"✅ Generated embeddings for {len(chunks)} chunks!")

