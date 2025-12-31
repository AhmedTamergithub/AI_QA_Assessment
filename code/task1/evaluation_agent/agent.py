import datetime
from zoneinfo import ZoneInfo
from google.adk.agents import Agent

#from code.Top_level.summarization_agent.tools import summarize_pdf, summarize_text
from .prompt import EVALUATION_AGENT_PROMPT
from .tools import evaluate_llm_responses, hallucination_checker, load_summarization_data, evaluate_summarization_agent, evaluate_api_fetching_agent

evaluation_agent = Agent(
    name="evaluation_agent",
    model="gemini-2.5-flash-lite",
    description=(
        "Quality assurance agent that validates outputs from summarization and API fetching agents using semantic similarity checks and hallucination detection to ensure factual accuracy and completeness."
    ),
    instruction=EVALUATION_AGENT_PROMPT,
    tools=[evaluate_llm_responses, hallucination_checker, load_summarization_data, evaluate_summarization_agent, evaluate_api_fetching_agent],
    #output_key="evaluation_report.json",
)  