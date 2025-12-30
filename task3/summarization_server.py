# my_adk_mcp_server.py (FastMCP version)
import json
import sys
import os
import time
import datetime
import threading

# Suppress stdout during imports to avoid polluting MCP protocol
_original_stdout = sys.stdout
sys.stdout = sys.stderr

from dotenv import load_dotenv

# FastMCP Import
from mcp.server.fastmcp import FastMCP
from langchain_experimental.text_splitter import SemanticChunker
from langchain_huggingface import HuggingFaceEmbeddings
# PDF and Language Detection Imports (lightweight)
import fitz  # PyMuPDF
from langdetect import detect, DetectorFactory

# Gemini API Import
from google import genai

# Restore stdout
sys.stdout = _original_stdout

# --- Load Environment Variables ---
load_dotenv()

# Set seed for consistent language detection results
DetectorFactory.seed = 0


# --- Initialize FastMCP Server ---
print("Creating FastMCP Server instance...", file=sys.stderr)
mcp = FastMCP("summarization-mcp-server")


# --- Define MCP Tools using FastMCP decorator ---


@mcp.tool()
def extract_pdf(pdf_path: str) -> str:
    """
    Extract text content from a PDF file using PyMuPDF.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        JSON string containing extracted_text, num_pages, and metadata
    """
    print(f"MCP Server: Received extract_pdf request for: {pdf_path}", file=sys.stderr)
    try:
        # Open the PDF file
        doc = fitz.open(pdf_path)
        num_pages = len(doc)
        
        # Check if PDF is empty (0 pages)
        if num_pages == 0:
            doc.close()
            return json.dumps({"error": "PDF file is empty (0 pages)"})
        
        # Extract text from all pages
        text = ""
        for page_num in range(num_pages):
            page = doc[page_num]
            text += page.get_text()
        
        # Close the document
        doc.close()
        
        # Check if PDF has no extractable text
        extracted_text = text.strip()
        if not extracted_text:
            return json.dumps({
                "error": f"PDF has {num_pages} page(s) but no extractable text (might be scanned images, binary data, or images without OCR)"
            })
        
        # Save extracted data to JSON file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(script_dir, "output")
        os.makedirs(output_dir, exist_ok=True)
        
        raw_data = {
            "pdf_path": pdf_path,
            "extracted_text": extracted_text,
            "num_pages": num_pages,
            "extraction_timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        output_path = os.path.join(output_dir, "raw_extracted_data.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(raw_data, f, indent=2, ensure_ascii=False)
        
        print(f"MCP Server: Extracted {len(extracted_text)} chars from {num_pages} pages", file=sys.stderr)
        
        return json.dumps({
            "extracted_text": extracted_text,
            "num_pages": num_pages,
            "output_file": output_path
        }, indent=2)
        
    except FileNotFoundError:
        return json.dumps({"error": f"PDF file not found: {pdf_path}"})
    except Exception as e:
        return json.dumps({"error": f"Error extracting PDF: {str(e)}"})


@mcp.tool()
def detect_language(text: str) -> str:
    """
    Detect the language of the given text using langdetect.
    
    Args:
        text: Text to detect language for
        
    Returns:
        JSON string containing the ISO 639-1 language code (e.g., 'en', 'fr', 'es')
    """
    print(f"MCP Server: Received detect_language request", file=sys.stderr)
    try:
        if not text or not text.strip():
            return json.dumps({"error": "Text is empty or contains only whitespace"})
        
        # Detect language
        language_code = detect(text)
        
        print(f"MCP Server: Detected language: {language_code}", file=sys.stderr)
        return json.dumps({
            "language_code": language_code,
            "text_length": len(text)
        }, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"Error detecting language: {str(e)}"})


@mcp.tool()
def summarize_text(text: str, max_length: str = "medium") -> str:
    """
    Summarize text using Gemini LLM.
    
    Args:
        text: Text to summarize
        max_length: Desired summary length - 'short', 'medium', or 'long'
        
    Returns:
        JSON string containing summary, prompts used, and metadata
    """
    print(f"MCP Server: Received summarize_text request (max_length={max_length})", file=sys.stderr)
    try:
        # Validate input
        if not text or not text.strip():
            return json.dumps({"error": "Text is empty or contains only whitespace"})
        
        # Define length guidelines
        length_guide = {
            "short": "in 2-3 sentences",
            "medium": "in 1-2 paragraphs",
            "long": "in 3-4 paragraphs with detailed key points"
        }
        
        # Create system and user prompts
        system_prompt = (
            "You are a professional text summarization assistant. "
            "Your task is to create clear, concise, and accurate summaries. "
            "Focus on the main ideas, key points, and essential information. "
            "Maintain objectivity and do not add information not present in the original text."
        )
        
        user_prompt = (
            f"Please summarize the following text {length_guide.get(max_length, length_guide['medium'])}:\n\n"
            f"{text}"
        )
        
        # Get API key
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            return json.dumps({"error": "GOOGLE_API_KEY not found in environment variables"})
        
        client = genai.Client(api_key=api_key)
        
        # Retry logic for rate limiting
        max_retries = 3
        retry_delay = 30  # seconds
        summary = None
        model_name = "gemini-2.5-flash-lite"
        
        for attempt in range(max_retries):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=user_prompt,
                    config={
                        'system_instruction': system_prompt,
                        'temperature': 0.7,
                    }
                )
                summary = response.text.strip()
                break  # Success, exit retry loop
                
            except Exception as e:
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    if attempt < max_retries - 1:
                        wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                        print(f"Rate limit hit. Waiting {wait_time} seconds before retry {attempt + 2}/{max_retries}...", file=sys.stderr)
                        time.sleep(wait_time)
                    else:
                        return json.dumps({"error": f"Rate limit exceeded after {max_retries} retries"})
                else:
                    return json.dumps({"error": f"LLM API error: {str(e)}"})
        
        # Prepare structured response
        result = {
            "summary": summary,
            "prompt": {
                "system_prompt": system_prompt,
                "user_prompt": user_prompt
            },
            "metadata": {
                "input_length": len(text),
                "summary_length": len(summary),
                "model": model_name,
                "max_length": max_length,
                "timestamp": datetime.datetime.now().isoformat()
            }
        }
        
        print(f"MCP Server: Summarized {len(text)} chars to {len(summary)} chars", file=sys.stderr)
        return json.dumps(result, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"Error during text summarization: {str(e)}"})

@mcp.tool()
def summarize_pdf(pdf_path: str) -> str:
    """
    Extract text from PDF and perform semantic chunking using embeddings.
    Automatically saves chunking output and final summary to files.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        JSON string containing chunks, chunk_summaries, and combined_summary
    """
    print(f"MCP Server: Received summarize_pdf request for: {pdf_path}", file=sys.stderr)
    try:
        # Determine output directory (relative to this script)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(script_dir, "output")
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Step 1: Extract text from PDF (returns JSON string, need to parse)
        print(f"Extracting text from PDF: {pdf_path}", file=sys.stderr)
        extract_result_json = extract_pdf(pdf_path)
        extract_result = json.loads(extract_result_json)
        
        if "error" in extract_result:
            return json.dumps({"error": f"PDF extraction failed: {extract_result['error']}"})
        
        extracted_text = extract_result["extracted_text"]
        num_pages = extract_result["num_pages"]
        print(f"✓ Extracted {len(extracted_text)} characters from {num_pages} pages", file=sys.stderr)
        
        # Step 2: Detect language (returns JSON string, need to parse)
        language_result_json = detect_language(extracted_text)
        language_result = json.loads(language_result_json)
        
        if "error" in language_result:
            language = "unknown"
        else:
            language = language_result["language_code"]
        print(f"✓ Detected language: {language}", file=sys.stderr)
        
        # Step 3: Perform semantic chunking using embeddings (FREE HuggingFace model)
        print(f"Performing semantic chunking with embeddings...", file=sys.stderr)
        print("Loading embedding model (this may take a moment on first run)...", file=sys.stderr)
        
        # Use free HuggingFace embeddings model
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        # Create semantic chunker that groups similar content together
        text_splitter = SemanticChunker(
            embeddings=embeddings,
            breakpoint_threshold_type="percentile"
        )
        
        # Split text into semantic chunks
        docs = text_splitter.create_documents([extracted_text])
        chunks = [doc.page_content for doc in docs]
        
        # Step 4: Prepare results
        chunk_info = []
        for i, chunk in enumerate(chunks, 1):
            chunk_info.append({
                "chunk_number": i,
                "length": len(chunk),
                "preview": chunk[:100] + "..." if len(chunk) > 100 else chunk
            })
        
        result = {
            "pdf_path": pdf_path,
            "num_pages": num_pages,
            "language": language,
            "total_characters": len(extracted_text),
            "num_chunks": len(chunks),
            "chunks": chunks,
            "chunk_info": chunk_info,
            "chunking_method": "semantic_embeddings",
            "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        # Save chunking output to file
        chunking_output_file = os.path.join(output_dir, "pdf_chunking_output.json")
        with open(chunking_output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Created {len(chunks)} semantic chunks", file=sys.stderr)
        print(f"✓ Chunking output saved to: {chunking_output_file}", file=sys.stderr)
        
        # Step 5: Summarize each chunk (summarize_text returns JSON string)
        print("SUMMARIZING CHUNKS...", file=sys.stderr)
        
        chunk_summaries = []
        for i, chunk in enumerate(chunks, 1):
            print(f"Summarizing chunk {i}/{len(chunks)}...", file=sys.stderr)
            try:
                summary_result_json = summarize_text(chunk, max_length="medium")
                summary_result = json.loads(summary_result_json)
                
                if "error" in summary_result:
                    chunk_summaries.append({
                        "chunk_number": i,
                        "chunk_length": len(chunk),
                        "summary": f"Error: {summary_result['error']}",
                        "summary_length": 0
                    })
                else:
                    chunk_summaries.append({
                        "chunk_number": i,
                        "chunk_length": len(chunk),
                        "summary": summary_result["summary"],
                        "summary_length": summary_result["metadata"]["summary_length"]
                    })
                    print(f"✓ Chunk {i} summarized: {len(chunk)} chars → {len(summary_result['summary'])} chars", file=sys.stderr)
            except Exception as e:
                print(f"✗ Error summarizing chunk {i}: {str(e)}", file=sys.stderr)
                chunk_summaries.append({
                    "chunk_number": i,
                    "chunk_length": len(chunk),
                    "summary": f"Error: {str(e)}",
                    "summary_length": 0
                })
        
        # Step 6: Combine all chunk summaries into one final summary
        print("CREATING COMBINED SUMMARY...", file=sys.stderr)
        
        all_summaries_text = "\n\n".join([f"Section {s['chunk_number']}: {s['summary']}" for s in chunk_summaries])
        print(f"Combining {len(chunk_summaries)} chunk summaries...", file=sys.stderr)
        
        try:
            combined_summary_result_json = summarize_text(all_summaries_text, max_length="short")
            combined_summary_result = json.loads(combined_summary_result_json)
            
            if "error" in combined_summary_result:
                combined_summary = f"Error creating combined summary: {combined_summary_result['error']}"
            else:
                combined_summary = combined_summary_result["summary"]
                print(f"✓ Combined summary created: {len(combined_summary)} characters", file=sys.stderr)
        except Exception as e:
            print(f"✗ Error creating combined summary: {str(e)}", file=sys.stderr)
            combined_summary = f"Error creating combined summary: {str(e)}"
        
        # Step 7: Prepare final output
        summarize_after_chunks = {
            "pdf_path": pdf_path,
            "num_pages": num_pages,
            "language": language,
            "total_characters": len(extracted_text),
            "num_chunks": len(chunks),
            "chunking_method": "semantic_embeddings",
            "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
            "chunk_summaries": chunk_summaries,
            "combined_summary": combined_summary,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        # Step 8: Save final summary to JSON file
        final_summary_file = os.path.join(output_dir, "summarize_after_chunks.json")
        with open(final_summary_file, 'w', encoding='utf-8') as f:
            json.dump(summarize_after_chunks, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Final summary saved to: {final_summary_file}", file=sys.stderr)
        
        # Return result with file paths
        summarize_after_chunks["output_files"] = {
            "chunking_output": chunking_output_file,
            "final_summary": final_summary_file
        }
        
        return json.dumps(summarize_after_chunks, indent=2)
        
    except FileNotFoundError:
        return json.dumps({"error": f"PDF file not found: {pdf_path}"})
    except Exception as e:
        return json.dumps({"error": f"Error in summarize_pdf: {str(e)}"})

if __name__ == "__main__":
    print("Launching FastMCP Server via stdio...", file=sys.stderr)
    mcp.run()
# --- End MCP Server ---
