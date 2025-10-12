"""RAG explanation component"""

import streamlit as st


def render_rag_explanation():
    """Render RAG explanation section with image and description"""
    
    with st.expander("📚 What is RAG? Learn the Basics", expanded=False):
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.image(
                "https://raw.githubusercontent.com/mcikalmerdeka/nlp-learning/refs/heads/main/rag-pipeline-visualizer/assets/Clearest%20RAG%20Diagram.jpg",
                width='stretch',
                caption="RAG Pipeline Architecture"
            )
        
        with col2:
            st.markdown("""
            ### What is RAG?
            
            **Retrieval-Augmented Generation (RAG)** is a powerful AI technique that enhances large language models (LLMs) by combining them with external knowledge retrieval systems.
            
            ### Why RAG?
            
            LLMs are trained on static datasets and can't access real-time or domain-specific information. RAG solves this by:
            - ✅ Providing up-to-date information
            - ✅ Reducing hallucinations
            - ✅ Adding domain-specific knowledge
            - ✅ Improving answer accuracy
            
            ### The Three Pipeline Stages:
            
            **🔎 1. Retrieval**
            - Documents are split into chunks
            - Chunks are converted to vector embeddings
            - User query is embedded and similar chunks are retrieved
            
            **🔗 2. Augmentation**
            - Retrieved chunks are combined with the user's query
            - Context is formatted into a prompt for the LLM
            
            **✨ 3. Generation**
            - LLM generates a response using the retrieved context
            - Answer is grounded in actual documents, not just model knowledge
            
            ---
            
            💡 **This tool lets you visualize each stage of the RAG pipeline in action!**
            """)

