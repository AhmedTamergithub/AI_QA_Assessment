"""
Simple Playwright Script - Wikipedia Content Extraction
Extracts the full article text from Wikipedia AI article (large input test)
"""

from playwright.sync_api import sync_playwright
import json
import asyncio
from mcp_client import call_mcp_summarize


def main():
    """
    Large Input Test Flow:
    1. Navigate to Wikipedia AI article
    2. Extract all paragraph text from the main content area
    3. Summarize the large text block
    """
    
    with sync_playwright() as p:
        # Launch Firefox browser
        print("Launching Firefox browser...")
        browser = p.firefox.launch(headless=False)
        page = browser.new_page()
        
        try:
            # Step 1: Navigate directly to Wikipedia AI article
            print("\n[Step 1] Navigating to Wikipedia AI article...")
            page.goto("https://en.wikipedia.org/wiki/Artificial_intelligence", timeout=60000)
            page.wait_for_load_state("networkidle")
            print("[Step 1] ✓ AI article page loaded")
            
            # Step 2: Extract all paragraph text from main content area
            print("\n[Step 2] Extracting full article text from main content area...")
            
            # Get all paragraphs from the main content div
            all_paragraphs = page.locator("#mw-content-text p").all()
            
            content = []
            for p in all_paragraphs:
                try:
                    text = p.inner_text().strip()
                    if len(text) > 20:  # Only substantial paragraphs
                        content.append(text)
                except Exception as e:
                    # Skip paragraphs that cause errors
                    continue
            
            extracted_text = '\n\n'.join(content)
            
            # Print extracted text summary (not the full text to avoid console overflow)
            print("\n" + "="*80)
            print("EXTRACTED FULL ARTICLE TEXT:")
            print("="*80)
            print(f"Total text length: {len(extracted_text)} characters")
            print(f"Number of paragraphs extracted: {len(content)}")
            print("Preview (first 500 characters):")
            print(extracted_text[:500] + "..." if len(extracted_text) > 500 else extracted_text)
            print("="*80)
            print("\n[SUCCESS] Full content extracted!")
            
            # Return the extracted text for MCP client
            return extracted_text
            
        except Exception as e:
            print(f"\n[ERROR] An error occurred: {e}")
            import traceback
            traceback.print_exc()
            return None
            
        finally:
            # Close browser
            print("\nClosing browser...")
            browser.close()


if __name__ == "__main__":
    # Step 1: Extract Wikipedia content using Playwright
    extracted_text = main()
    
    # Step 2: Summarize using MCP client
    if extracted_text:
        asyncio.run(call_mcp_summarize(extracted_text))
    else:
        print("\n[ERROR] No text extracted, skipping summarization")