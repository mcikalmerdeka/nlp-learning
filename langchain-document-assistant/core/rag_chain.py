"""
RAG chain creation and answer generation
"""
import streamlit as st
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from config.prompts import (
    PROMPT_TEMPLATE,
    DOCUMENT_ONLY_PROMPT_TEMPLATE,
    ENHANCED_PROMPT_TEMPLATE
)
from .document_processor import format_docs


def create_rag_chain(language_model, retriever, external_search_enabled: bool = True):
    """
    Create a comprehensive RAG chain using LangChain Expression Language
    
    Args:
        language_model: The LLM to use for generation
        retriever: Document retriever
        external_search_enabled: Whether external search is enabled
        
    Returns:
        RAG chain
    """
    # Choose prompt template based on external search setting
    if external_search_enabled:
        prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    else:
        prompt = ChatPromptTemplate.from_template(DOCUMENT_ONLY_PROMPT_TEMPLATE)
    
    # Create the RAG chain using LCEL syntax
    rag_chain = (
        {
            "document_context": retriever | RunnableLambda(format_docs),
            "user_query": RunnablePassthrough()
        }
        | prompt
        | language_model
        | StrOutputParser()
    )
    
    return rag_chain


def generate_enhanced_answer(user_query: str, rag_chain, language_model, 
                            retriever, external_search_enabled: bool = True,
                            external_search_available: bool = True):
    """
    Generate answer using RAG chain with optional external search fallback
    
    Args:
        user_query: User's question
        rag_chain: The RAG chain to use
        language_model: The LLM to use
        retriever: Document retriever
        external_search_enabled: Whether external search is enabled
        external_search_available: Whether external search is available
        
    Returns:
        str: Generated answer
    """
    try:
        # Step 1: Try to answer using document context first
        initial_response = rag_chain.invoke(user_query)
        
        # Step 2: Check if external search is needed and enabled
        if (external_search_enabled and 
            "[EXTERNAL_SEARCH_NEEDED]" in initial_response and 
            external_search_available):
            
            st.info("🔍 Document context insufficient. Searching external sources...")
            
            try:
                # Import here to avoid circular dependency
                from agents.external_sources_lookup_agent import lookup
                
                # Step 3: Perform external search
                external_results = lookup(user_query)
                
                # Step 4: Create enhanced prompt with both contexts
                enhanced_prompt = ChatPromptTemplate.from_template(ENHANCED_PROMPT_TEMPLATE)
                
                # Get document context again
                docs = retriever.invoke(user_query)
                document_context = format_docs(docs)
                
                # Step 5: Generate enhanced response
                enhanced_chain = enhanced_prompt | language_model | StrOutputParser()
                
                final_response = enhanced_chain.invoke({
                    "user_query": user_query,
                    "document_context": document_context,
                    "external_context": external_results
                })
                
                # Clean up and return enhanced response
                cleaned_response = final_response.strip()
                cleaned_response = '\n'.join(line.strip() for line in cleaned_response.split('\n') if line.strip())
                
                return cleaned_response
                
            except Exception as e:
                st.error(f"External search failed: {str(e)}")
                # Fall back to original response without the search indicator
                fallback_response = initial_response.replace("[EXTERNAL_SEARCH_NEEDED]", "").strip()
                return fallback_response if fallback_response else "I don't have sufficient information to answer this query."
        
        else:
            # Step 6: Return normal response (either external search disabled or not needed)
            if not external_search_enabled:
                # Clean response for document-only mode
                cleaned_response = initial_response.strip()
            else:
                # Clean response and remove external search indicator if present
                cleaned_response = initial_response.replace("[EXTERNAL_SEARCH_NEEDED]", "").strip()
            
            cleaned_response = '\n'.join(line.strip() for line in cleaned_response.split('\n') if line.strip())
            return cleaned_response if cleaned_response else "I don't have sufficient information to answer this query."
            
    except Exception as e:
        return f"Error generating response: {str(e)}"
