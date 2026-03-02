import os
from dotenv import load_dotenv
load_dotenv()   # Load the environment variables from the .env file

from typing import Literal
from tavily import TavilyClient
from deepagents import create_deep_agent
from langchain.chat_models import init_chat_model

# Initialize the model and tavily client
model = init_chat_model(model="gpt-4.1-mini", api_key=os.getenv("OPENAI_API_KEY"))
tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

# Define the internet search tool of Tavily with enhanced capabilities
def internet_search(
    query: str,
    max_results: int = 4,
    topic: Literal["general", "news", "finance"] = "news",
    include_raw_content: bool = True,
    search_depth: Literal["basic", "advanced"] = "advanced",
):
    """Run a comprehensive web search for thorough research.
    
    Args:
        query: The search query string
        max_results: Maximum number of results to return (default 10 for thorough research)
        topic: The topic category - use 'news' for current events, 'geopolitics' for political analysis
        include_raw_content: Whether to include full article content (True for detailed research)
        search_depth: 'advanced' for more comprehensive results
    """
    return tavily_client.search(
        query,
        max_results=max_results,
        include_raw_content=include_raw_content,
        topic=topic,
        search_depth=search_depth,
    )

# System prompt to steer the agent to be an expert geopolitical researcher
research_instructions = """You are an expert geopolitical researcher and analyst specializing in Middle East affairs and US foreign policy. Your job is to conduct thorough, multi-faceted research and produce comprehensive, well-structured reports.

You have access to an internet search tool as your primary means of gathering information.

## Research Methodology

When researching a complex topic like US-Iran relations, you should:

1. **Search Multiple Angles**: Conduct several searches covering different aspects:
   - Current breaking news and recent developments
   - Historical context and background
   - Military and strategic analysis
   - Diplomatic efforts and negotiations
   - Economic sanctions and their impacts
   - Regional implications (Israel, Saudi Arabia, Gulf states)
   - International community responses

2. **Verify Information**: Cross-reference information from multiple sources when possible.

3. **Consider Multiple Perspectives**: Look for analysis from different viewpoints.

## `internet_search`

Use this to run an internet search for a given query. Parameters:
- `query`: Your search query (be specific and targeted)
- `max_results`: Number of results (use 10 for comprehensive research)
- `topic`: Use "news" for current events, "general" for broader search, "finance" for financial news
- `include_raw_content`: Set to True to get full article content
- `search_depth`: Use "advanced" for thorough results

## Report Structure

Your final report should include:
1. Executive Summary
2. Current Situation Overview
3. Key Recent Developments (with dates)
4. Historical Context
5. Key Players and Their Positions
6. Potential Scenarios and Implications
7. Sources Referenced
"""

agent = create_deep_agent(
    model=model,
    tools=[internet_search],
    system_prompt=research_instructions
)

# Define comprehensive research query for US-Iran situation
research_query = """Please conduct a thorough research on the US-Iran situation. I need a comprehensive report covering:

1. The latest news and developments in US-Iran relations
2. Any recent military tensions, strikes, or confrontations
3. Current status of nuclear negotiations and the JCPOA
4. Economic sanctions and their effects
5. Regional dynamics involving Israel, Saudi Arabia, and other Gulf states
6. Potential for escalation or de-escalation
7. Key statements from US and Iranian leadership

Please search multiple times with different queries to gather comprehensive information, then synthesize everything into a well-structured report."""

# Run the agent with the comprehensive research query
result = agent.invoke({"messages": [{"role": "user", "content": research_query}]})

# Print the agent's response
print("=" * 80)
print("US-IRAN SITUATION RESEARCH REPORT")
print("=" * 80)
print(result["messages"][-1].content)