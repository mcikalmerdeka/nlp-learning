"""
Complete documentation for the following website: https://docs.agno.com/concepts/tools/toolkits/web_scrape/firecrawl
"""

import os
from dotenv import load_dotenv
load_dotenv()

from agno.agent import Agent
from agno.tools.firecrawl import FirecrawlTools
from agno.models.openai import OpenAIChat

agent = Agent(
    model=OpenAIChat(id="gpt-4.1-mini", api_key=os.getenv("OPENAI_API_KEY")),
    tools=[FirecrawlTools(enable_scrape=False, enable_crawl=True)],
    markdown=True
)

website_url = "https://finance.yahoo.com/"
agent.print_response(f"Summarize this website: {website_url}")