"""
Simple Playwright Script - Wikipedia Content Extraction
Extracts the History section from Wikipedia AI article
"""

from playwright.sync_api import sync_playwright
import json
import asyncio
from mcp_client import call_mcp_summarize


def main():
    """
    Baseline Flow:
    1. Navigate to Wikipedia AI article
    2. Scroll to History section
    3. Extract and print paragraph text from History section
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
            
            # Step 2: Scroll to History section
            print("\n[Step 2] Scrolling to 'History' section...")
            history_heading = page.locator("#History")
            history_heading.scroll_into_view_if_needed()
            page.wait_for_timeout(1000)
            print("[Step 2] ✓ History section visible")
            
            # Step 3: Extract text from History section using Python
            print("\n[Step 3] Extracting text from History section...")
            
            # Get all h2 headings
            all_h2_headings = page.locator("h2").all()
            
            # Find History section index
            history_index = -1
            for i, heading in enumerate(all_h2_headings):
                heading_text = heading.inner_text()
                if "History" in heading_text:
                    history_index = i
                    print(f"[Step 3] Found History section at index {i}")
                    break
            
            if history_index == -1:
                print("[ERROR] History section not found!")
                return
            
            # Get all paragraphs from the page
            all_paragraphs = page.locator("#mw-content-text p").all()
            
            # Get the History h2 element
            history_h2 = all_h2_headings[history_index]
            
            # Get the next h2 element (Applications section)
            next_h2 = None
            if history_index + 1 < len(all_h2_headings):
                next_h2 = all_h2_headings[history_index + 1]
                next_section_name = next_h2.inner_text()
                print(f"[Step 3] Next section is: {next_section_name}")
            
            # Now filter paragraphs that are between History and next section
            content = []
            
            for p in all_paragraphs:
                try:
                    # Check if paragraph comes after History heading
                    is_after_history = page.evaluate(
                        "(args) => args.p.compareDocumentPosition(args.h2) & Node.DOCUMENT_POSITION_PRECEDING",
                        {"p": p.element_handle(), "h2": history_h2.element_handle()}
                    )
                    
                    # Check if paragraph comes before next section (if exists)
                    is_before_next = True
                    if next_h2:
                        is_before_next = page.evaluate(
                            "(args) => args.p.compareDocumentPosition(args.h2) & Node.DOCUMENT_POSITION_FOLLOWING",
                            {"p": p.element_handle(), "h2": next_h2.element_handle()}
                        )
                    
                    # If paragraph is in the History section, add it
                    if is_after_history and is_before_next:
                        text = p.inner_text().strip()
                        if len(text) > 20:  # Only substantial paragraphs
                            content.append(text)
                
                except Exception as e:
                    # Skip paragraphs that cause errors
                    continue
            
            extracted_text = '\n\n'.join(content)
            
            # Print extracted text
            print("\n" + "="*80)
            print("EXTRACTED TEXT FROM HISTORY SECTION:")
            print("="*80)
            print(extracted_text)
            print("="*80)
            print(f"\nTotal text length: {len(extracted_text)} characters")
            print(f"Number of paragraphs extracted: {len(content)}")
            print("\n[SUCCESS] Content extracted!")
            
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