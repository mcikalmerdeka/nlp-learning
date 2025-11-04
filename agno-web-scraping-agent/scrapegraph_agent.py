"""
Complete documentation for the following website: https://docs.agno.com/concepts/tools/toolkits/web_scrape/scrapegraph/
"""

import os
from dotenv import load_dotenv
load_dotenv()

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.scrapegraph import ScrapeGraphTools

agent_model = OpenAIChat(id="gpt-4.1-mini", api_key=os.getenv("OPENAI_API_KEY"))
scrapegraph_smartscraper = ScrapeGraphTools(api_key=os.getenv("SCRAPEGRAPH_API_KEY"), enable_smartscraper=True)

agent = Agent(
    model=agent_model,
    tools=[scrapegraph_smartscraper],
    markdown=True,
    stream=True
)

agent.print_response("""
Use smartscraper to extract the following from https://www.wired.com/category/science/:
- News articles
- Headlines
- Images
- Links
- Author
""")