# ./adk_agent_samples/mcp_client_agent/agent.py
import os
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters
from .system_prompt import task2_system_prompt 
# Paths to MCP servers
script_dir = os.path.dirname(os.path.abspath(__file__))
SUMMARIZATION_SERVER_PATH = os.path.join(script_dir, "summarization_server.py")
API_FETCHING_SERVER_PATH = os.path.join(script_dir, "api_fetching_server.py")
PYTHON_EXECUTABLE = os.path.join(script_dir, "..", "..", ".venv", "bin", "python3")
EVALUATION_SERVER_PATH = os.path.join(script_dir, "evaluation_server.py")



multi_tool_mcp_agent = LlmAgent(
    model='gemini-2.5-flash',
    name='multi_tool_mcp_agent',
    instruction=task2_system_prompt,
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
            tool_filter=['extract_pdf_text', 'detect_language', 'summarize_text', 'summarize_pdf']
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