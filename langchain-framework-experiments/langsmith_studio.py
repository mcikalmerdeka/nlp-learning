import os
from dotenv import load_dotenv
load_dotenv()

from langchain.tools import tool
from typing import Dict, Any
from langchain_tavily import tavily_search
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model

# Initialize model
model = init_chat_model(model="gpt-5-nano", api_key=os.getenv("OPENAI_API_KEY"))

# Initialize web search tool
@tool
def web_search(query: str) -> Dict[str, Any]:
    """Search the web for information"""
    return tavily_search(query = query, api_key=os.getenv("TAVILY_API_KEY"))

# Initialize system prompt
system_prompt = """

You are a personal chef. The user will give you a list of ingredients they have left over in their house.

Using the web search tool, search the web for recipes that can be made with the ingredients they have.

Return recipe suggestions and eventually the recipe instructions to the user, if requested.

"""

# Initialize agent
agent = create_agent(
    model=model,
    tools=[web_search],
    system_prompt=system_prompt
)