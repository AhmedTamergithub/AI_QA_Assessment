# Task 1: Multi-Agent Orchestration

This task implements a modular multi-agent system using the **Google-adk** framework. The system is orchestrated by a Root Agent that delegates tasks to specialized agents based on user intent.

## Architecture

The system consists of several specialized agents:

1.  **Root Orchestrator**: Analyzes user requests and delegates them to the appropriate workflow.
2.  **API Fetching Agent**: Handles weather queries and currency exchange rates.
3.  **Summarization Agent**: Processes PDF documents, performs summarization, and detects document language.
4.  **Evaluation Agent**: Performs quality assurance, validating outputs using semantic similarity checks and hallucination detection.

## Technologies & Models Used

| Category | Technology/Model | Purpose/Usage |
|----------|------------------|---------------|
| **Framework** | Google-adk (Agent Development Kit) | Core framework for building and orchestrating agents |
| **LLM Models** | Gemini 2.5 Flash | Backend LLM used across all agents in Task1 for core processing |
| | Gemini 2.5 Flash Lite | Used in the `summarize_text` tool within the summarization agent |
| | Gemini 3 Flash Preview | Judge LLM used in the `hallucination_checker` tool within the evaluation agent |
| **Embedding Models** | Sentence Transformers (all-MiniLM-L6-v2) | - Semantic chunking in the `summarize_pdf` tool (summarization agent)<br>- Semantic similarity calculation in the `evaluate_llm_responses` tool (evaluation agent) |
| **External APIs** | Weather API | For weather queries |
| | Currency Exchange API | For exchange rate conversions |
| **Document Processing** | PyMuPDF (fitz) | PDF text extraction |
| **Programming Language** | Python 3.x | Primary development language |

## Key Features

-   **Modular Design**: Each agent has its own specialized tools and prompt files;
    - Any agent directory has under it `agent.py` for agent building and putting model for it, `tools.py` has Python functions for agent execution, and `prompt.py` for the system instructions for the agent and determining its execution flow.



-   **Automated Evaluated**: Each workflow includes a validation step through the evaluation agent before returning results to the user.
    - Sequential agent for summarization agent then evaluation agent.
    - Sequential agent for api fetching agent then evaluation agent.



## Directory Structure

- **Orchestrator/**
    - [agent.py](code/task1/Orchestrator/agent.py)
- **api_fetching_agent/**
    - [agent.py](code/task1/api_fetching_agent/agent.py)
    - [prompt.py](code/task1/api_fetching_agent/prompt.py)
    - [schemas.py](code/task1/api_fetching_agent/schemas.py)
    Defined a certain output json schema for Api_fetching_agent , to be compared against the ground truth api calling in Evaluation agent (the validation step for output of api fetching agent )
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
        A valid PDF file utilized by the extract_text function.
        - [Imagepdfonly.pdf](code/task1/summarization_agent/resources/Imagepdfonly.pdf)
        Triggers an error: ValueError(f"PDF has {num_pages} page(s) but no extractable text (might be scanned images, binary data, or images without OCR)")
        - [emptypdf.pdf](code/task1/summarization_agent/resources/emptypdf.pdf)
        Triggers an error: ValueError("PDF file is empty (0 pages)")
        - [zero_pages.pdf](code/task1/summarization_agent/resources/zero_pages.pdf)
        Triggers an error: ValueError("PDF file is empty (0 pages)")

## How to Run

### Dependencies
1. Create virtual environment
2. Install [requirements.txt](../../requirements.txt)

### API KEY Configuration
1. Use the existing [`.env` file](../../.env)


2. Go to [Google AI Studio](https://aistudio.google.com/) and create your Gemini API key
![Navigate to Google AI Studio](../../images/navigate_to_google_ai_studio.PNG)



4. Add your Gemini API key to the `.env` file

### Running the Entire Task 1 System
1. Execute `configure_root.py` and select the orchestrator option.
2. Change to the `code/task1` directory.
3. Execute `adk web` (if port 8000 is occupied, use `adk web --port 8001` or another available port).
4. Follow the provided link.
5. Begin interacting with the agent through the adk web interface.

### Running an Individual Specialized Agent
1. Execute `configure_root.py` and select either `api_fetching` or `summarization`.
2. Move to the `code/task1` directory.
3. Launch `adk web` in the terminal(if  default port 8000 is occupied, use `adk web --port 8001` or another available port).
4. Engage in conversation with the specialized agent via the adk web UI.



## Important Note on Evaluating Sub-Agents (API Fetching Agent and Summarization Agent)

Evaluating the API FETCHING AGENT:

I established a schema for the API fetching agent's output. This agent utilizes the fetch_exchange_rate and fetch_weather tools, then feeds them into an agent that generates a final JSON output schema (making the final output agent-driven).

For evaluating the API fetching agent, we extract this JSON and use the parameters within it (city for weather fetching and base/target for currency exchange) to re-query the APIs and verify if the API responses match the agent's responses using the evaluate_api_fetching_agent tool found in evaluation agent

Evaluating the SUMMARIZATION AGENT:

The summarization agent generates a final summarization output JSON employing the LLM in summarize_text (gemini-2.5-flash-lite).

Subsequently, the evaluation agent features the evaluate_summarization_agent tool, which incorporates both evaluate_llm_responses and hallucination_checker with an LLM judge (gemini-3-flash-preview) to conduct the assessment.

No schema was defined for the summarization agent 


**, so evaluation criteria for both sub-agents is different.**