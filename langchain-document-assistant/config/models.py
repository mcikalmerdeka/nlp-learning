"""
Language model initialization
"""
import os
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from .settings import LLM_TEMPERATURE, LLM_MAX_TOKENS


def initialize_language_model(model_choice: str):
    """
    Initialize the chosen language model
    
    Args:
        model_choice: Model name from MODEL_OPTIONS keys
        
    Returns:
        Initialized language model instance
    """
    if model_choice == "GPT-4o":
        return ChatOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            model="gpt-4o",
            temperature=LLM_TEMPERATURE,
            max_tokens=LLM_MAX_TOKENS
        )
    elif model_choice == "GPT-4.1":
        return ChatOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            model="gpt-4.1",
            temperature=LLM_TEMPERATURE,
            max_tokens=LLM_MAX_TOKENS
        )
    else:  # Claude Sonnet 4
        return ChatAnthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            model="claude-sonnet-4-20250514",
            temperature=LLM_TEMPERATURE,
            max_tokens=LLM_MAX_TOKENS
        )
