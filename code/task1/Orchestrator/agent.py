
import sys
import os
from google.adk.agents import Agent,SequentialAgent
# Import the sub-agents
from api_fetching_agent.agent import api_fetching_agent
from summarization_agent.agent import summarization_agent
# Import evaluation agent components to create separate instances
from evaluation_agent.prompt import EVALUATION_AGENT_PROMPT
from evaluation_agent.tools import evaluate_llm_responses, hallucination_checker, load_summarization_data, evaluate_summarization_agent,evaluate_api_fetching_agent


# # Add parent directory to path to import sibling modules
# current_dir = os.path.dirname(os.path.abspath(__file__))
# parent_dir = os.path.dirname(current_dir)
# if parent_dir not in sys.path:
#     sys.path.insert(0, parent_dir)


# Define the root agent instruction
ROOT_AGENT_INSTRUCTION = """
You are the Root Orchestrator agent for my Agentic AI  system.

Your role is to analyze user requests and delegate them to the appropriate specialized agent workflow:

**Delegation Rules:**
- For weather queries or currency exchange rates → Delegate to 'api_fetching_with_validation'
- For PDF document processing, summarization, or language detection → Delegate to 'summarization_with_validation'

**When to Delegate:**
- If the user asks about weather in any city → transfer to api_fetching_with_validation
- If the user asks about exchange rates or currency conversion → transfer to api_fetching_with_validation
- If the user asks to summarize a PDF or document → transfer to summarization_with_validation
- If the user asks about document language detection → transfer to summarization_with_validation

**Important:**
- Analyze the user's intent carefully before delegating
- If the request is unclear, ask the user for clarification before delegating
- If the request doesn't match any specialist agent, politely explain available capabilities
- Once you identify the appropriate agent workflow, use transfer_to_agent to delegate the request
- Each workflow automatically includes validation through the evaluation agent before returning results
"""


# Evaluation agent Instance for summarization workflow
evaluation_agent_for_summarization = Agent(
    name="evaluation_agent_summarization",
    model="gemini-2.5-flash-lite",
    description="Quality assurance agent that validates summarization outputs using semantic similarity checks and hallucination detection.",
    instruction=EVALUATION_AGENT_PROMPT,
    tools=[evaluate_llm_responses, hallucination_checker, load_summarization_data, evaluate_summarization_agent],
)

# Evaluation agent  Instance for API fetching workflow
evaluation_agent_for_api = Agent(
    name="evaluation_agent_api",
    model="gemini-2.5-flash-lite",
    description="Quality assurance agent that validates API fetching outputs by comparing agent output with ground truth real-time API response.",
    instruction=EVALUATION_AGENT_PROMPT,
    tools=[evaluate_api_fetching_agent],
)

summarization_with_validation = SequentialAgent(
    name="summarization_with_validation",
    description="Sequential workflow for PDF summarization followed by automatic validation",
    sub_agents=[summarization_agent, evaluation_agent_for_summarization]
)

api_fetching_with_validation = SequentialAgent(
    name="api_fetching_with_validation",
    description="Sequential workflow for API data fetching followed by automatic validation",
    sub_agents=[api_fetching_agent, evaluation_agent_for_api]
)

# the Root agent with LLM-Driven Delegation to validated workflows
root_orchestrator = Agent(
    name="RootOrchestrator",
    model="gemini-2.5-flash",
    description="Main coordinator that routes requests to specialized agent workflows with built-in validation.",
    instruction=ROOT_AGENT_INSTRUCTION,
    sub_agents=[summarization_with_validation, api_fetching_with_validation]  # LLM-Driven Delegation to validated workflows
)

root_agent = root_orchestrator
