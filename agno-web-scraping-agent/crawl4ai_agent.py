"""
Complete documentation for the following website: https://docs.agno.com/concepts/tools/toolkits/web_scrape/crawl4ai
"""

import os
from dotenv import load_dotenv
load_dotenv()

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.crawl4ai import Crawl4aiTools

agent = Agent(
    tools=[Crawl4aiTools(max_length=None)],
    model=OpenAIChat(id="gpt-4.1-mini", api_key=os.getenv("OPENAI_API_KEY"))
)

website_url = "https://github.com/agno-agi/agno"
agent.print_response(f"Tell me about this website: {website_url}")