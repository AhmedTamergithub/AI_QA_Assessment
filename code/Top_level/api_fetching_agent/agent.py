import datetime
from zoneinfo import ZoneInfo
from google.adk.agents import Agent
from .prompt import api_fetching_prompt
from .tools import fetch_weather, fetch_exchange_rate
api_fetching_agent = Agent(
    name="api_fetching_agent",
    model="gemini-2.5-flash",
    description=(
        "AI agent that fetches weather information and exchange rates using external APIs."   
    ),
    instruction=api_fetching_prompt,
    tools=[fetch_weather, fetch_exchange_rate]
)  