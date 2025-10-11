"""Augmentation section component - shows prompt construction"""

import streamlit as st


def render_augmentation_section():
    """Render the augmentation section showing prompt construction"""
    st.header("🔧 2. Augmentation")
    st.markdown("View how retrieved context is integrated into the prompt sent to the LLM")
    
    if not st.session_state.get('query_results'):
        st.info("👆 Perform a query in the Retrieval section first to see augmentation")
        return
    
    st.divider()
    
    # System Prompt Section
    st.subheader("📋 System Prompt")
    st.markdown("*This instructs the LLM on how to behave and use the context*")
    
    # Allow custom system prompt
    default_system_prompt = """You are a helpful AI assistant. Use the provided context to answer the user's question accurately and comprehensively. 
If the context doesn't contain relevant information, acknowledge this and provide the best answer you can based on your knowledge.
Always cite which parts of the context you used in your answer."""
    
    if 'custom_system_prompt' not in st.session_state:
        st.session_state.custom_system_prompt = default_system_prompt
    
    use_custom = st.checkbox("Customize system prompt", value=False)
    
    if use_custom:
        st.session_state.custom_system_prompt = st.text_area(
            "Edit system prompt:",
            value=st.session_state.custom_system_prompt,
            height=150,
            key="system_prompt_input"
        )
    else:
        st.code(default_system_prompt, language="text")
        st.session_state.custom_system_prompt = default_system_prompt
    
    st.divider()
    
    # Retrieved Context Section
    st.subheader("📚 Retrieved Context")
    st.markdown(f"*{len(st.session_state.query_results['documents'][0])} chunks retrieved from vector database*")
    
    with st.expander("View Retrieved Contexts", expanded=True):
        for i, (doc, distance, chunk_id) in enumerate(zip(
            st.session_state.query_results['documents'][0],
            st.session_state.query_results['distances'][0],
            st.session_state.query_results['ids'][0]
        )):
            similarity = 1 - distance
            chunk_number = int(chunk_id.split('_')[1])
            
            st.markdown(f"**[Context {i+1}] - Chunk {chunk_number} - Similarity: {similarity:.3f}**")
            st.text_area(
                f"context_{i}",
                value=doc,
                height=100,
                disabled=True,
                label_visibility="collapsed"
            )
            if i < len(st.session_state.query_results['documents'][0]) - 1:
                st.markdown("---")
    
    st.divider()
    
    # Augmented User Message Section
    st.subheader("💬 Augmented User Message")
    st.markdown("*This is the final message sent to the LLM (System Prompt + Context + Query)*")
    
    # Construct the augmented message
    query_text = st.session_state.get('last_query', '')
    retrieved_docs = st.session_state.query_results['documents'][0]
    
    context_text = "\n\n".join([
        f"[Context {i+1}]:\n{doc}" 
        for i, doc in enumerate(retrieved_docs)
    ])
    
    augmented_message = f"""Context Information:
{'='*80}
{context_text}
{'='*80}

User Question: {query_text}

Please answer the question based on the context provided above."""
    
    # Store for generation
    st.session_state.augmented_prompt = {
        "system_prompt": st.session_state.custom_system_prompt,
        "user_message": augmented_message,
        "query": query_text,
        "num_contexts": len(retrieved_docs)
    }
    
    # Display in code block for clarity
    with st.expander("View Full Augmented Prompt", expanded=False):
        st.code(augmented_message, language="text")
    
    # Show token estimate
    estimated_tokens = len(augmented_message.split()) + len(st.session_state.custom_system_prompt.split())
    st.caption(f"📊 Estimated tokens: ~{estimated_tokens * 1.3:.0f} (prompt)")
    
    st.divider()
    
    # Action button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Proceed to Generation →", type="primary", use_container_width=True):
            st.session_state.ready_for_generation = True
            st.success("✅ Ready for generation! Scroll to Generation section below.")

