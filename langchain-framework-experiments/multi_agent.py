import os
from dotenv import load_dotenv
load_dotenv()
from datetime import datetime

from langchain.agents import create_agent
from langchain_core.tools import tool  # Fixed import
from langchain_openai import ChatOpenAI

# Create specialized worker agents
llm = ChatOpenAI(
    model="gpt-4o-mini",  # Fixed model name (gpt-4.1-mini → gpt-4o-mini)
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0,
    max_tokens=500
)

# Setup database of emails
emails = {
    "Finance": "The sales today are not doing well",
    "Marketing": "The marketing campaign is not generating leads",
    "Sales": "The sales today are not doing well",
}

# Define calendar and email tools
@tool
def get_calendar():
    """Get the current calendar."""
    return "Today is " + datetime.now().strftime("%Y-%m-%d")

@tool
def get_email(department: str):
    """Get the current email."""
    return emails.get(department, "No emails")

calendar_agent = create_agent(llm, [get_calendar], system_prompt="You handle calendar tasks...")
email_agent = create_agent(llm, [get_email], system_prompt="You handle email tasks...")

# Wrap workers as tools for supervisor - FIXED
@tool
def call_calendar_agent(query: str):
    """Use for scheduling, availability, events. Route calendar tasks to specialist."""
    return calendar_agent.invoke({"messages": [{"role": "user", "content": query}]})

@tool
def call_email_agent(query: str):
    """Use for emails, drafts, notifications. Route email tasks to specialist."""
    return email_agent.invoke({"messages": [{"role": "user", "content": query}]})

# Supervisor sees only high-level tools
supervisor = create_agent(
    llm,
    tools=[call_calendar_agent, call_email_agent],
    system_prompt="Coordinate calendar and email agents for user requests."
)

# Run the model in a single invocation
result = supervisor.invoke({"messages": [{"role": "user", "content": "What's the email content from Finance and what's the calendar for today?"}]})
print(result["messages"][-1].content)

# from langchain_openai import ChatOpenAI
# from langchain_core.tools import tool
# from langchain.agents import create_agent
# import os
# from dotenv import load_dotenv
# load_dotenv()
# from typing import Dict, Any

# # Set your OpenAI API key (get from https://platform.openai.com/api-keys)
# os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# # Mock tools for demo (replace with real APIs)
# @tool
# def check_calendar(query: str) -> str:
#     """Check calendar availability or events."""
#     return f"Calendar check for '{query}': Free on Thursday 2pm."

# @tool
# def schedule_event(event: str) -> str:
#     """Schedule a calendar event."""
#     return f"✅ Scheduled: {event}"

# @tool
# def send_email(to: str, subject: str, body: str) -> str:
#     """Send an email."""
#     return f"📧 Email sent to {to}: '{subject}'"

# @tool
# def draft_email(subject: str, body: str) -> str:
#     """Draft an email for review."""
#     return f"Draft ready: '{subject}' - {body[:50]}..."

# # Create LLM
# model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# # Calendar agent - only sees calendar tools
# calendar_agent = create_agent(
#     model,
#     tools=[check_calendar, schedule_event],
#     system_prompt="You are a calendar assistant. ONLY handle scheduling and availability. Respond concisely."
# )

# # Email agent - only sees email tools
# email_agent = create_agent(
#     model,
#     tools=[send_email, draft_email],
#     system_prompt="You are an email assistant. ONLY handle emails and notifications. Respond concisely."
# )

# # Wrap workers as tools for supervisor (FIXED SYNTAX)
# @tool
# def call_calendar_agent(task: str) -> str:
#     """Use for ALL calendar/scheduling tasks. Send calendar tasks to specialist agent."""
#     result = calendar_agent.invoke({"messages": [{"role": "user", "content": task}]})
#     return result["messages"][-1].content

# @tool
# def call_email_agent(task: str) -> str:
#     """Use for ALL email/notification tasks. Send email tasks to specialist agent."""
#     result = email_agent.invoke({"messages": [{"role": "user", "content": task}]})
#     return result["messages"][-1].content

# # Supervisor coordinates both agents
# supervisor = create_agent(
#     model,
#     tools=[call_calendar_agent, call_email_agent],
#     system_prompt="""
# You are a personal assistant coordinating calendar and email specialists.
# Route tasks to the right agent based on the request:
# - Scheduling, availability → calendar_agent  
# - Emails, notifications → email_agent

# Break complex requests into multiple steps if needed.
# Always summarize final results for the user.
# """
# )

# if __name__ == "__main__":
#     # Test the multi-agent system
#     user_request = """
#     Check my availability Thursday afternoon and schedule a team meeting at 2pm.
#     Then email the team to confirm.
#     """
    
#     print("👤 User:", user_request)
#     print("\n🤖 Multi-Agent Response:")
#     print("-" * 50)
    
#     result = supervisor.invoke({
#         "messages": [{"role": "user", "content": user_request}]
#     })
    
#     print(result["messages"][-1].content)