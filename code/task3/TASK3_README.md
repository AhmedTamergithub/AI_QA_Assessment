# Task 3: MCP Agent - Wikipedia AI Article Summarization Tests

This task contains Playwright-based test scripts for extracting content from the Wikipedia Artificial Intelligence article and summarizing it using an MCP (Model Context Protocol) server.

## Overview

Task 3 implements an MCP-based system for automated web content extraction and summarization. The workflow follows this sequence:

1. **Test Script Execution**: Playwright-based test scripts run to extract text from Wikipedia articles
2. **MCP Client Communication**: Extracted text is passed to the MCP client for processing
3. **Server Connection**: MCP client establishes connection with the summarization MCP server
4. **Summarization**: MCP server uses the `summarize_text` tool (powered by Gemini 3 Flash Preview) to generate summaries and returns results to the terminal

## Directory Structure

- **[mcp_client.py](mcp_client.py)** - MCP client for server communication
- **[summarization_server.py](summarization_server.py)** - MCP server providing summarization tools
- **[TASK3_README.md](TASK3_README.md)** - This documentation file
- **[task3_requirements.txt](task3_requirements.txt)** - Python dependencies
- **test_scripts/** - Directory containing test files
  - **[test_baseline.py](test_scripts/test_baseline.py)** - Baseline test for Applications section
  - **[test_history.py](test_scripts/test_history.py)** - History section test
  - **[test_full_article.py](test_scripts/test_full_article.py)** - Full article test
  - **[test_empty_content.py](test_scripts/test_empty_content.py)** - Empty content robustness test


## Test Files

### test_baseline.py
- **Purpose**: Baseline test extracting the "Applications" section.
- **What it does**:
  - Navigates to the Wikipedia AI article.
  - Scrolls to and extracts text from the "Applications" section.
  - Calls the MCP server to summarize the extracted text.
- **Input Size**: Medium (section-specific, ~several paragraphs).
- **Use Case**: This was the baseline test for this task, specifically designed for the Wikipedia AI article webpage using Firefox browser. Tests summarization of a focused, thematic section.

### test_history.py
- **Purpose**: Additional test extracting the "History" section.
- **What it does**:
  - Navigates to the Wikipedia AI article.
  - Scrolls to and extracts text from the "History" section.
  - Calls the MCP server to summarize the extracted text.
- **Input Size**: Medium (section-specific, ~several paragraphs).
- **Use Case**: This is an additional test script to ensure that our logic tests another section, not agnostic to the Applications section only as the baseline test script. Tests summarization of historical/timeline content.

### test_full_article.py
- **Purpose**: Large input test extracting the entire article text.
- **What it does**:
  - Navigates to the Wikipedia AI article.
  - Extracts all paragraph text from the main content area.
  - Calls the MCP server to summarize the large text block.
- **Input Size**: Large (~88,000 characters from 181 paragraphs).
- **Use Case**: This test was designed to extract very large input context and verify that the LLM found in the summarize_text tool handles that effectively, performing a concise summary with a high compression ratio.

### test_empty_content.py
- **Purpose**: Robustness test for missing or empty extracted content.
- **What it does**:
  - Navigates to the Wikipedia AI article.
  - Attempts to extract text from a non-existent section (`#NonExistentSection`).
  - Verifies that the script handles the empty result gracefully.
- **Input Size**: Zero (empty string).
- **Use Case**: This test ensures that the system handles cases where no content is found (e.g., chosing a section not found or due to webpage changes or broken locators) and correctly skips the MCP summarization call instead of crashing or sending empty data.






## How to Run

> **Environment Requirements**: Tasks 1 and 2 were executed on WSL1 due to limited Linux environment access. Task 3 requires a full Linux environment, Windows, or WSL2 for proper Playwright browser automation. This task was run on Windows using PowerShell terminal, which necessitated a separate `task3_requirements.txt` file. When running Task 3, create a new virtual environment to ensure proper dependency isolation. 

1. Activate your virtual environment: `& venv\Scripts\Activate.ps1` (Windows)
2. Install dependencies: `pip install -r task3_requirements.txt`
3. Configure API key: Add your Gemini API key to the [`.env`](.env) file (Task 3 uses a separate environment file from the main project [`.env`](../../.env) used in Tasks 1 and 2)
4. Navigate to test_scripts directory
5. Run any test: `python test_baseline.py` (or `test_history.py`, `test_full_article.py`)

Each test will open Firefox, extract content, and display the summary from the MCP server.




## Notes

- Tests run in headless=False mode by default (browser visible). Change to `headless=True` in the script for background execution.
- The MCP server must be available for summarization to work.
- Extraction focuses on clean text; irrelevant elements (e.g., navigation bars, images) are excluded.



