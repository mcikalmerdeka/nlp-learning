"""LLM integration for RAG generation"""

import os
from openai import OpenAI
from typing import List, Dict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def get_openai_client():
    """Get OpenAI client instance"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")
    return OpenAI(api_key=api_key)


def construct_rag_prompt(query: str, retrieved_chunks: List[str], system_prompt: str = None) -> Dict[str, any]:
    """Construct augmented prompt with retrieved context
    
    Args:
        query: User query
        retrieved_chunks: List of retrieved text chunks
        system_prompt: Optional custom system prompt
        
    Returns:
        Dictionary with system_prompt, context, user_query, and full_prompt
    """
    if system_prompt is None:
        system_prompt = """You are a helpful AI assistant. Use the provided context to answer the user's question accurately and comprehensively. 
If the context doesn't contain relevant information, acknowledge this and provide the best answer you can based on your knowledge.
Always cite which parts of the context you used in your answer."""
    
    # Format retrieved context
    context_text = "\n\n".join([
        f"[Context {i+1}]:\n{chunk}" 
        for i, chunk in enumerate(retrieved_chunks)
    ])
    
    # Construct full prompt
    user_message = f"""Context Information:
{'='*80}
{context_text}
{'='*80}

User Question: {query}

Please answer the question based on the context provided above."""
    
    return {
        "system_prompt": system_prompt,
        "context": context_text,
        "user_query": query,
        "full_user_message": user_message,
        "num_chunks": len(retrieved_chunks)
    }


def generate_response(query: str, retrieved_chunks: List[str], system_prompt: str = None, model: str = "gpt-4o-mini") -> Dict[str, any]:
    """Generate response using OpenAI with retrieved context
    
    Args:
        query: User query
        retrieved_chunks: List of retrieved text chunks
        system_prompt: Optional custom system prompt
        model: OpenAI model to use
        
    Returns:
        Dictionary with prompt_data and response
    """
    client = get_openai_client()
    
    # Construct augmented prompt
    prompt_data = construct_rag_prompt(query, retrieved_chunks, system_prompt)
    
    # Call OpenAI API
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": prompt_data["system_prompt"]},
            {"role": "user", "content": prompt_data["full_user_message"]}
        ],
        temperature=0.7,
        max_tokens=1000
    )
    
    return {
        "prompt_data": prompt_data,
        "response": response.choices[0].message.content,
        "model": model,
        "usage": {
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens
        }
    }

