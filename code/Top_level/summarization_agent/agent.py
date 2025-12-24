import datetime
from zoneinfo import ZoneInfo
from google.adk.agents import Agent
from .prompt import system_prompt
from .tools import extract_pdf, detect_language, summarize_text, summarize_pdf

summarization_agent = Agent(
    name="summarization_agent",
    model="gemini-2.5-flash",
    description=(
        "AI Summarization agent that processes PDF documents by extracting text, performing semantic chunking using embeddings,summarizing each chunk individually, and generating a combined final summary. Also detects document language. "   
    ),
    instruction=system_prompt,
    tools=[extract_pdf, detect_language, summarize_text, summarize_pdf]
)  