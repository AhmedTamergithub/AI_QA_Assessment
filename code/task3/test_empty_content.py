"""
Playwright Script - Empty Content Handling Test
Simulates a case where no content is extracted (e.g., due to a missing section)
to verify graceful error handling.
"""

from playwright.sync_api import sync_playwright
import json
import asyncio
from mcp_client import call_mcp_summarize


def main():
    """
    Empty Content Test Flow:
    1. Navigate to Wikipedia AI article
    2. Attempt to scroll to a NON-EXISTENT section
    3. Verify that no text is extracted and handle gracefully
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
            
            # Step 2: Attempt to find a non-existent section
            print("\n[Step 2] Searching for non-existent section 'NonExistentSection'...")
            
            # Get all h2 headings
            all_h2_headings = page.locator("h2").all()
            
            # Find section index
            target_index = -1
            for i, heading in enumerate(all_h2_headings):
                heading_text = heading.inner_text()
                if "NonExistentSection" in heading_text:
                    target_index = i
                    break
            
            if target_index == -1:
                print("[Step 2]  'NonExistentSection' not found in headings.")
                print("\n" + "="*80)
                print("RESULT: SECTION NOT FOUND ")
                print("="*80)
                print("The script correctly identified that the section does not exist.")
                print("="*80)
                print("\n[SUCCESS] Missing section handled gracefully!")
                return None

            # Step 3: Extract text (this part should not be reached in this test)
            print("\n[Step 3] Extracting text from section...")
            # ... extraction logic would go here ...
            return "Unexpectedly found text"
            
        except Exception as e:
            print(f"\n[ERROR] An error occurred: {e}")
            return None
            
        finally:
            # Close browser
            print("\nClosing browser...")
            browser.close()


if __name__ == "__main__":
    # Step 1: Attempt extraction
    extracted_text = main()
    
    # Step 2: Summarize using MCP client (should be skipped)
    if extracted_text:
        print("\n[ERROR] Unexpectedly found text to summarize!")
        asyncio.run(call_mcp_summarize(extracted_text))
    else:
        print("\n[INFO] No text extracted, skipping MCP summarization call as intended.")
