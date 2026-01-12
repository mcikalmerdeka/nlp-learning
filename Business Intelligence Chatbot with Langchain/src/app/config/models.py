"""Language model initialization"""

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from .settings import OPENAI_API_KEY, ANTHROPIC_API_KEY


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
            api_key=OPENAI_API_KEY,
            model="gpt-4o",
            temperature=0,
            max_tokens=4000
        )
    elif model_choice == "GPT-4.1":
        return ChatOpenAI(
            api_key=OPENAI_API_KEY,
            model="gpt-4.1",
            temperature=0,
            max_tokens=4000
        )
    elif model_choice == "Claude Sonnet 4":
        return ChatAnthropic(
            api_key=ANTHROPIC_API_KEY,
            model="claude-sonnet-4-20250514",
            temperature=0,
            max_tokens=4000
        )
    else:  # Claude 3.7 Sonnet
        return ChatAnthropic(
            api_key=ANTHROPIC_API_KEY,
            model="claude-3-7-sonnet-20250219",
            temperature=0,
            max_tokens=4000
        )
