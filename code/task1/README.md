# Task 1: Multi-Agent Orchestration

This task implements a modular multi-agent system using the **Google-adk** framework. The system is orchestrated by a Root Agent that delegates tasks to specialized agents based on user intent.

## Architecture

The system consists of several specialized agents:

1.  **Root Orchestrator**: Analyzes user requests and delegates them to the appropriate workflow.
2.  **API Fetching Agent**: Handles weather queries and currency exchange rates.
3.  **Summarization Agent**: Processes PDF documents, performs summarization, and detects document language.
4.  **Evaluation Agent**: Performs quality assurance, validating outputs using semantic similarity checks and hallucination detection.

## Key Features

-   **Modular Design**: Each agent has its own specialized tools and prompt files.
-   **Automated Validation**: Each workflow includes a validation step through the evaluation agent before returning results to the user.
-   **Intent-Based Delegation**: The Root Orchestrator uses clear rules to route requests to the correct specialist.

## Directory Structure

- **Orchestrator/**
    - [agent.py](code/task1/Orchestrator/agent.py)
- **api_fetching_agent/**
    - [agent.py](code/task1/api_fetching_agent/agent.py)
    - [prompt.py](code/task1/api_fetching_agent/prompt.py)
    - [schemas.py](code/task1/api_fetching_agent/schemas.py)
    - [tools.py](code/task1/api_fetching_agent/tools.py)
- **evaluation_agent/**
    - [agent.py](code/task1/evaluation_agent/agent.py)
    - [prompt.py](code/task1/evaluation_agent/prompt.py)
    - [tools.py](code/task1/evaluation_agent/tools.py)
- **summarization_agent/**
    - [agent.py](code/task1/summarization_agent/agent.py)
    - [prompt.py](code/task1/summarization_agent/prompt.py)
    - [tools.py](code/task1/summarization_agent/tools.py)
    - **resources/**
        - [Ahmed_Tamer_Samir_CV.pdf](code/task1/summarization_agent/resources/Ahmed_Tamer_Samir_CV.pdf)
        - [Imagepdfonly.pdf](code/task1/summarization_agent/resources/Imagepdfonly.pdf)
        - [emptypdf.pdf](code/task1/summarization_agent/resources/emptypdf.pdf)
        - [zero_pages.pdf](code/task1/summarization_agent/resources/zero_pages.pdf)
