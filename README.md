# AI EDA Project

## Tasks Block Diagrams

### Task 1: Multi-Agent Orchestration
[Task 1 README](code/task1/README.md)
![Task 1 System Diagram](images/task1_system_diagram.png)

For Task 1, we developed a modular multi-agent system where each specific responsibility is handled by a dedicated agent. This architecture ensures clear separation of concerns:
- **Modular Design**: Each agent (API Fetching, Summarization, and Evaluation) is equipped with its own set of specialized **tools** and a dedicated **prompt file** for precise behavioral control.
- **Framework**: The system is built using the **Google-adk** framework, leveraging its capabilities for robust agent management and tool integration.

---

### Task 2: MCP-Based Architecture
![Task 2 System Diagram](images/task2_system_diagram.png)

Task 2 transitions the system to a Model Context Protocol (MCP) architecture, enhancing scalability and interoperability:
- **MCP Client**: A single agent acts as the MCP client, orchestrating requests across the environment.
- **MCP Servers**: Three distinct servers provide specialized services:
    1. **API Fetching Server**
    2. **Summarization Server**
    3. **Evaluation Server**

> **Note on Evaluation Logic**: The Evaluation Server is exclusively responsible for assessing the **summarization output**. We have omitted automated evaluation for the API fetching stage because the fetching server interacts directly with the ground truth (real API data). Evaluating the raw fetching output against itself would be redundant, as the server's primary role is to provide the factual data used in subsequent steps.

---

### Task 3: Automated Web Extraction & Summarization
Task 3 focuses on automated data extraction from live web sources and processing via MCP:
- **Architecture**: The system consists of **1 MCP Client** and **1 MCP Server** dedicated to summarization.
- **Automation Layer**: We implemented **4 Playwright-based test scripts** to automate content extraction from the Wikipedia "Artificial Intelligence" article:
    1. **Baseline Test (`test_baseline.py`)**: Extracts and summarizes the "Applications" section.
    2. **History Test (`test_history.py`)**: Extracts and summarizes the "History" section to ensure thematic consistency.
    3. **Full Article Test (`test_full_article.py`)**: Extracts the entire article to test the LLM's ability to handle large context windows and high compression ratios.
    4. **Robustness Test (`test_empty_content.py`)**: Verifies that the system handles missing or non-existent sections gracefully without crashing.
