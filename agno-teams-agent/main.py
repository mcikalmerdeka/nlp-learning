import os
from dotenv import load_dotenv

from agno.team import Team
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.tavily import TavilyTools
from pydantic import BaseModel

# Load the environment variables and configure the OpenAI API key
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
tavily_api_key = os.getenv("TAVILY_API_KEY")

# Create the structured response format using pydantic
class StockAnalysis(BaseModel):
    symbol: str
    company_name: str
    stock_analysis: str

class CompanyAnalysis(BaseModel):
    company_name: str
    company_information: str

class StockReport(BaseModel):
    symbol: str
    company_name: str
    company_information: str
    stock_report: str

# Create specialized agents
stock_analysis_agent = Agent(
    id="stock-analysis-agent",
    name="Stock Analysis Agent",
    model=OpenAIChat(id="gpt-4.1-mini", api_key=openai_api_key),
    role="Analyze the stock market and provide analysis",
    tools=[TavilyTools(api_key=tavily_api_key)],
    output_schema=StockAnalysis,
    markdown=True
)

company_information_agent = Agent(
    id="company-information-agent",
    name="Company Information Agent", 
    model=OpenAIChat(id="gpt-4.1-mini", api_key=openai_api_key),
    role="Get company information and analysis",
    tools=[TavilyTools(api_key=tavily_api_key)],
    output_schema=CompanyAnalysis,
    markdown=True
)

# Create the team
team = Team(
    name="Stock Research Team",
    members=[stock_analysis_agent, company_information_agent],
    model=OpenAIChat(id="gpt-4.1-mini", api_key=openai_api_key),
    instructions="Coordinate with team members to provide comprehensive information. Delegate tasks based on the user's request.",
    output_schema=StockReport,
    markdown=True
)

team.print_response("What is the current stock price of NVDA? and what is the company information of NVDA?", stream=True)

# Output:
# (.venv) PS E:\NLP Learning\NLP-Learning\agno-teams-agent> uv run .\main.py
# ┏━ Message ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
# ┃                                                                                         ┃
# ┃ What is the current stock price of NVDA? and what is the company information of NVDA?   ┃
# ┃                                                                                         ┃
# ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
# ┏━ Stock Analysis Agent Tool Calls ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
# ┃                                                                                         ┃
# ┃ • web_search_using_tavily(query=NVDA stock price, max_results=3)                        ┃
# ┃                                                                                         ┃
# ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
# ┏━ Stock Analysis Agent Response ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
# ┃                                                                                         ┃
# ┃ {                                                                                       ┃
# ┃   "symbol": "NVDA",                                                                     ┃
# ┃   "company_name": "NVIDIA Corporation",                                                 ┃
# ┃   "stock_analysis": "The current stock price of NVIDIA Corporation (NVDA) is approximat ┃
# ┃ }                                                                                       ┃
# ┃                                                                                         ┃
# ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
# ┏━ Company Information Agent Tool Calls ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
# ┃                                                                                         ┃
# ┃ • web_search_using_tavily(query=NVIDIA Corporation company overview, industry, key      ┃
# ┃ products, recent                                                                        ┃
# ┃   developments, max_results=5)                                                          ┃
# ┃                                                                                         ┃
# ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
# ┏━ Company Information Agent Response ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
# ┃                                                                                         ┃
# ┃ {                                                                                       ┃
# ┃   "company_name": "NVIDIA Corporation",                                                 ┃
# ┃   "company_information": "NVIDIA Corporation, founded in 1993 and headquartered in Sant ┃
# ┃ }                                                                                       ┃
# ┃                                                                                         ┃
# ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
# ┏━ Team Tool Calls ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
# ┃                                                                                         ┃
# ┃ • delegate_task_to_member(member_id=stock-analysis-agent, task=Provide the current      ┃
# ┃ stock price of NVDA (NVIDIA                                                             ┃
# ┃   Corporation). Include the latest price and recent price trends if possible.)          ┃
# ┃                                                                                         ┃
# ┃ • delegate_task_to_member(member_id=company-information-agent, task=Provide detailed    ┃
# ┃ company information for                                                                 ┃
# ┃   NVDA (NVIDIA Corporation), including its business overview, industry, key products,   ┃
# ┃ and recent                                                                              ┃
# ┃   developments.)                                                                        ┃
# ┃                                                                                         ┃
# ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
# ┏━ Response (31.5s) ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
# ┃                                                                                         ┃
# ┃ {                                                                                       ┃
# ┃   "symbol": "NVDA",                                                                     ┃
# ┃   "company_name": "NVIDIA Corporation",                                                 ┃
# ┃   "company_information": "NVIDIA Corporation, founded in 1993 and headquartered in Sant ┃
# ┃   "stock_report": "The current stock price of NVIDIA Corporation (NVDA) is approximatel ┃
# ┃ }                                                                                       ┃
# ┃                                                                                         ┃
# ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
