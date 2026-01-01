# Task 3: MCP Agent - Wikipedia AI Article Summarization Tests

This project contains Playwright-based test scripts for extracting content from the Wikipedia Artificial Intelligence article and summarizing it using an MCP (Model Context Protocol) server.

## Overview

The tests use Playwright to automate browser interactions, extract text from specific sections or the entire article, and then call an MCP client to summarize the content. This setup allows testing summarization on different input sizes and types.

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
- **Use Case**: This test ensures that the system handles cases where no content is found (e.g., due to webpage changes or broken locators) and correctly skips the MCP summarization call instead of crashing or sending empty data.

## Other Files

- **mcp_client.py**: Separated MCP client code for calling the summarization server.
- **summarization_server.py**: The MCP server that provides summarization tools.
- **task3_requirements.txt**: Python dependencies (install with `pip install -r task3_requirements.txt`).
- **AI_QA.pdf**: Additional context or data file (not used in tests).

## Requirements

- Python 3.x
- Playwright (install with `pip install playwright` and run `playwright install firefox`)
- MCP server dependencies (as per requirements.txt)

## How to Run

1. Activate your virtual environment: `& venv\Scripts\Activate.ps1` (Windows)
2. Install dependencies: `pip install -r task3_requirements.txt`
3. Install Playwright browsers: `playwright install firefox`
4. Run any test: `python test_baseline.py` (or `test_history.py`, `test_full_article.py`)

Each test will open Firefox, extract content, and display the summary from the MCP server.

## Notes

- Tests run in headless=False mode by default (browser visible). Change to `headless=True` in the script for background execution.
- The MCP server must be available for summarization to work.
- Extraction focuses on clean text; irrelevant elements (e.g., navigation) are excluded.
