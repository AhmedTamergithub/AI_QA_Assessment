# ./adk_agent_samples/mcp_client_agent/agent.py
import os
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

# Paths to MCP servers
SUMMARIZATION_SERVER_PATH = "/home/ahmedubuntu/AI_EDA/code/task2/summarization_server.py"
API_FETCHING_SERVER_PATH = "/home/ahmedubuntu/AI_EDA/code/task2/api_fetching_server.py"
PYTHON_EXECUTABLE = "/home/ahmedubuntu/AI_EDA/.venv/bin/python3"
EVALUATION_SERVER_PATH = "/home/ahmedubuntu/AI_EDA/code/task2/evaluation_server.py"



multi_tool_mcp_agent = LlmAgent(
    model='gemini-2.5-flash',
    name='multi_tool_mcp_agent',
    instruction="""You are a helpful assistant with access to tools from THREE MCP servers:

=== SERVER 1: Summarization Server ===
Tools for PDF processing and text summarization:
- 'extract_pdf': Extract text content from a PDF file given its path. Returns the extracted text and number of pages.
- 'detect_language': Detect the language of a given text. Returns the ISO 639-1 language code (e.g., 'en', 'fr', 'es').
- 'summarize_text': Summarize text using Gemini LLM. Accepts text and optional max_length ('short', 'medium', 'long').
- 'summarize_pdf': Full PDF summarization pipeline - extracts text, performs semantic chunking, summarizes each chunk, and creates a combined summary.

=== SERVER 2: API Fetching Server ===
Tools for fetching real-time data from external APIs:
- 'fetch_weather': Fetch current weather for any city. Accepts city name and optional unit ('celsius' or 'fahrenheit'). Uses Open-Meteo API.
- 'fetch_exchange_rate': Fetch latest exchange rate between two currencies. Accepts base currency and target currency codes (e.g., 'USD', 'EUR').

=== SERVER 3: Evaluation Server ===
Tools for evaluating summarization quality:
- 'evaluate_summarization_agent': Complete evaluation of summarization output using both similarity and hallucination checks.
  - Performs semantic similarity evaluation using cosine similarity with embeddings
  - Performs hallucination detection using LLM-as-a-judge approach
  - Optional parameters: summary_file_path, raw_data_file_path, similarity_threshold (default: 0.7)
  - Returns overall_verdict (PASS/FAIL), similarity_evaluation, hallucination_evaluation, and recommendation

Use the appropriate tools based on the user's request:
- For PDF/document work → use summarization server tools
- For weather information → use fetch_weather
- For currency exchange rates → use fetch_exchange_rate
- For evaluating summarization quality → use evaluate_summarization_agent""",
    tools=[
        # Server 1: Summarization Server
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command=PYTHON_EXECUTABLE,
                    args=[SUMMARIZATION_SERVER_PATH],
                ),
                timeout=300  # 5 minutes timeout for long-running tools like summarize_pdf
            ),
            tool_filter=['extract_pdf', 'detect_language', 'summarize_text', 'summarize_pdf']
        ),
        # Server 2: API Fetching Server
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command=PYTHON_EXECUTABLE,
                    args=[API_FETCHING_SERVER_PATH],
                ),
                timeout=60  # 1 minute timeout for API calls
            ),
            tool_filter=['fetch_weather', 'fetch_exchange_rate']
        ),
        #Server 3: Output Evaluation Server (Adapted now only to evaluate summarization agent )
        
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command=PYTHON_EXECUTABLE,
                    args=[EVALUATION_SERVER_PATH],
        ),
        timeout=120  # 2 minutes for embedding model load + evaluation
    ),
    tool_filter=['evaluate_summarization_agent']
)
    ],
)


root_agent = multi_tool_mcp_agent