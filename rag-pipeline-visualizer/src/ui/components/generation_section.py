"""Generation section component - shows LLM response"""

import streamlit as st
from src.core.llm import generate_response, get_openai_client


def render_generation_section():
    """Render the generation section showing LLM response"""
    st.header("✨ 3. Generation")
    st.markdown("Generate and view the LLM's response using the augmented prompt")
    
    if not st.session_state.get('augmented_prompt'):
        st.info("👆 Complete the Augmentation section first to proceed with generation")
        return
    
    st.divider()
    
    # Show what we're about to send
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Contexts Used", st.session_state.augmented_prompt['num_contexts'])
    with col2:
        st.metric("Model", "gpt-4o-mini")
    
    st.divider()
    
    # Generation controls
    col1, col2 = st.columns([3, 1])
    
    with col1:
        generate_button = st.button(
            "🤖 Generate Response",
            type="primary",
            use_container_width=True,
            disabled=st.session_state.get('generating', False)
        )
    
    with col2:
        if st.session_state.get('llm_response'):
            if st.button("🔄 Regenerate", use_container_width=True):
                st.session_state.llm_response = None
                st.rerun()
    
    # Generate response
    if generate_button:
        # Check API key
        try:
            get_openai_client()
        except ValueError as e:
            st.error("❌ OPENAI_API_KEY not found. Please configure it:")
            st.markdown("**For local development:** Add to `.env` file:")
            st.code("OPENAI_API_KEY=your_key_here", language="bash")
            st.markdown("**For Streamlit Cloud:** Add to Secrets (⚙️ Settings → Secrets):")
            st.code('OPENAI_API_KEY = "your_key_here"', language="toml")
            return
        
        st.session_state.generating = True
        
        with st.spinner("🧠 Generating response from GPT-4o-mini..."):
            try:
                # Get retrieved documents
                retrieved_docs = st.session_state.query_results['documents'][0]
                query = st.session_state.augmented_prompt['query']
                system_prompt = st.session_state.augmented_prompt['system_prompt']
                
                # Generate response
                result = generate_response(
                    query=query,
                    retrieved_chunks=retrieved_docs,
                    system_prompt=system_prompt,
                    model="gpt-4o-mini"
                )
                
                st.session_state.llm_response = result
                st.session_state.generating = False
                st.success("✅ Response generated successfully!")
                
            except Exception as e:
                st.error(f"❌ Error generating response: {str(e)}")
                st.session_state.generating = False
                return
    
    # Display response if available
    if st.session_state.get('llm_response'):
        st.divider()
        
        # Response content
        st.subheader("💡 LLM Response")
        st.markdown(st.session_state.llm_response['response'])
        
        st.divider()
        
        # Token usage and metadata
        st.subheader("📊 Generation Metadata")
        
        usage = st.session_state.llm_response['usage']
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Prompt Tokens", f"{usage['prompt_tokens']:,}")
        with col2:
            st.metric("Completion Tokens", f"{usage['completion_tokens']:,}")
        with col3:
            st.metric("Total Tokens", f"{usage['total_tokens']:,}")
        with col4:
            # Rough cost estimate for gpt-4o-mini
            cost = (usage['prompt_tokens'] * 0.150 / 1_000_000) + (usage['completion_tokens'] * 0.600 / 1_000_000)
            st.metric("Est. Cost", f"${cost:.6f}")
        
        st.caption("💰 Cost based on GPT-4o-mini pricing: $0.150/1M input tokens, $0.600/1M output tokens")
        
        # Show full conversation for debugging/inspection
        with st.expander("🔍 View Full API Call Details"):
            st.markdown("**Model Used:**")
            st.code(st.session_state.llm_response['model'])
            
            st.markdown("**System Prompt Sent:**")
            st.code(st.session_state.llm_response['prompt_data']['system_prompt'], language="text")
            
            st.markdown("**User Message Sent:**")
            st.code(st.session_state.llm_response['prompt_data']['full_user_message'], language="text")
            
            st.markdown("**Response Received:**")
            st.code(st.session_state.llm_response['response'], language="text")

