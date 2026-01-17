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
    if model_choice == "GPT-4.1 mini":
        return ChatOpenAI(
            api_key=OPENAI_API_KEY,
            model="gpt-4.1-mini",
            temperature=0,
            max_tokens=4000
        )
    else:  # Claude Haiku 4.5
        return ChatAnthropic(
            api_key=ANTHROPIC_API_KEY,
            model="claude-haiku-4-5-20251001",
            temperature=0,
            max_tokens=4000
        )
