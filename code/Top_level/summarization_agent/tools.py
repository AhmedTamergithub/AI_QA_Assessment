import fitz  # PyMuPDF
from langdetect import detect, DetectorFactory
from typing import Optional, List
import os
from dotenv import load_dotenv
import json
import time
from langchain_experimental.text_splitter import SemanticChunker
from langchain_huggingface import HuggingFaceEmbeddings

# Load environment variables
load_dotenv()

# Set seed for consistent language detection results
DetectorFactory.seed = 0


def extract_pdf(pdf_path: str) -> tuple[str, int]:
    """
    Extract text content from a PDF file using PyMuPDF.
    
    Args:
        pdf_path (str): Path to the PDF file
        
    Returns:
        tuple[str, int]: A tuple containing (extracted_text, num_pages)
        
    Raises:
        FileNotFoundError: If the PDF file doesn't exist
        ValueError: If PDF is empty or corrupted
        Exception: For other PDF processing errors
    """
    try:
        # Open the PDF file
        doc = fitz.open(pdf_path)
        num_pages = len(doc)
        
        # Check if PDF is empty (0 pages) [Requirement 4]
        if num_pages == 0:
            doc.close()
            raise ValueError("PDF file is empty (0 pages)")
        
        # Extract text from all pages
        text = ""
        for page_num in range(num_pages):
            page = doc[page_num]
            text += page.get_text()
        
        # Close the document
        doc.close()
        
        # Check if PDF has no extractable text (images, scanned without OCR, binary data) [Requirement 3]
        extracted_text = text.strip()
        if not extracted_text:
            raise ValueError(f"PDF has {num_pages} page(s) but no extractable text (might be scanned images, binary data, or images without OCR)")
        
        return extracted_text, num_pages #[Requirement 2]
    
    except FileNotFoundError:
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    except ValueError:
        raise
    except Exception as e:
        raise Exception(f"Error extracting PDF (possibly corrupted or unreadable): {str(e)}")


def detect_language(text: str) -> str:
    """
    Detect the language of the given text using langdetect.
    
    Args:
        text (str): Text to detect language for
        
    Returns:
        str: ISO 639-1 language code (e.g., 'en', 'fr', 'es')
        
    Raises:
        ValueError: If text is empty or language cannot be detected
    """
    try:
        if not text or not text.strip():
            raise ValueError("Text is empty or contains only whitespace")
        
        # Detect language
        language_code = detect(text)
        
        return language_code
    
    except Exception as e:
        raise ValueError(f"Error detecting language: {str(e)}")


def summarize_text(text: str, max_length: str = "medium") -> dict:
    """
    Summarize text using Gemini LLM.
    
    Args:
        text (str): Text to summarize
        max_length (str): Desired summary length - 'short', 'medium', or 'long'
        
    Returns:
        dict: Structured JSON containing:
            - summary (str): The generated summary
            - prompt (dict): Contains system_prompt and user_prompt sent to LLM
            - metadata (dict): Contains input_length, summary_length, model, timestamp
            
    Raises:
        ValueError: If text is empty or invalid
        Exception: For LLM API errors
    """
    try:
        # Validate input
        if not text or not text.strip():
            raise ValueError("Text is empty or contains only whitespace")
        
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
        
        # Use Gemini API with retry logic
        from google import genai
        
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        client = genai.Client(api_key=api_key)
        
        # Retry logic for rate limiting
        max_retries = 3
        retry_delay = 30  # seconds
        
        for attempt in range(max_retries):
            try:
                response = client.models.generate_content(
                    model='gemini-2.5-flash-lite',
                    contents=user_prompt,
                    config={
                        'system_instruction': system_prompt,
                        'temperature': 0.7,
                    }
                )
                
                summary = response.text.strip()
                model_name = "gemini-2.5-flash"
                break  # Success, exit retry loop
                
            except Exception as e:
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    if attempt < max_retries - 1:
                        wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                        print(f"Rate limit hit. Waiting {wait_time} seconds before retry {attempt + 2}/{max_retries}...")
                        time.sleep(wait_time)
                    else:
                        raise  # Max retries reached
                else:
                    raise  # Non-rate-limit error
        
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
                "timestamp": __import__('datetime').datetime.now().isoformat()
            }
        }
        
        return result
    
    except ValueError:
        raise
    except Exception as e:
        raise Exception(f"Error during text summarization: {str(e)}")


def summarize_pdf(pdf_path: str) -> dict:
    """
    Extract text from PDF and perform semantic chunking using embeddings.
    Automatically saves chunking output and final summary to files.
    
    Args:
        pdf_path (str): Path to the PDF file
        
    Returns:
        dict: Contains extracted_text, num_pages, language, chunks, and chunk_info
        
    Raises:
        Exception: If PDF extraction or chunking fails
    """
    try:
        # Determine output directory (relative to this script)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(script_dir, "output")
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Step 1: Extract text from PDF
        print(f"Extracting text from PDF: {pdf_path}")
        extracted_text, num_pages = extract_pdf(pdf_path)
        print(f"✓ Extracted {len(extracted_text)} characters from {num_pages} pages")
        
        # Step 2: Detect language
        language = detect_language(extracted_text)
        print(f"✓ Detected language: {language}")
        
        # Step 3: Perform semantic chunking using embeddings (FREE HuggingFace model)
        print(f"\nPerforming semantic chunking with embeddings...")
        print("Loading embedding model (this may take a moment on first run)...")
        
        # Use free HuggingFace embeddings model
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"  # Free, lightweight, and effective
        )
        
        # Create semantic chunker that groups similar content together
        text_splitter = SemanticChunker(
            embeddings=embeddings,
            breakpoint_threshold_type="percentile"  # Splits when similarity drops significantly
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
            "timestamp": __import__('datetime').datetime.now().isoformat()
        }
        
        # Save chunking output to file
        chunking_output_file = os.path.join(output_dir, "pdf_chunking_output.json")
        with open(chunking_output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Created {len(chunks)} semantic chunks")
        print(f"✓ Chunking output saved to: {chunking_output_file}")
        print(f"\n{'='*80}")
        print("CHUNKING RESULTS")
        print(f"{'='*80}")
        for i, chunk in enumerate(chunks, 1):
            print(f"\n{'='*80}")
            print(f"CHUNK {i}: {len(chunk)} characters")
            print(f"{'='*80}")
            print(chunk)
            print(f"{'='*80}")
        
        # Step 5: Summarize each chunk
        print(f"\n{'='*80}")
        print("SUMMARIZING CHUNKS")
        print(f"{'='*80}")
        
        chunk_summaries = []
        for i, chunk in enumerate(chunks, 1):
            print(f"\nSummarizing chunk {i}/{len(chunks)}...")
            try:
                summary_result = summarize_text(chunk, max_length="short")
                chunk_summaries.append({
                    "chunk_number": i,
                    "chunk_length": len(chunk),
                    "summary": summary_result["summary"],
                    "summary_length": summary_result["metadata"]["summary_length"]
                })
                print(f"✓ Chunk {i} summarized: {len(chunk)} chars → {len(summary_result['summary'])} chars")
            except Exception as e:
                print(f"✗ Error summarizing chunk {i}: {str(e)}")
                chunk_summaries.append({
                    "chunk_number": i,
                    "chunk_length": len(chunk),
                    "summary": f"Error: {str(e)}",
                    "summary_length": 0
                })
        
        # Step 6: Combine all chunk summaries into one final summary
        print(f"\n{'='*80}")
        print("CREATING COMBINED SUMMARY")
        print(f"{'='*80}")
        
        all_summaries_text = "\n\n".join([f"Section {s['chunk_number']}: {s['summary']}" for s in chunk_summaries])
        print(f"Combining {len(chunk_summaries)} chunk summaries...")
        
        try:
            combined_summary_result = summarize_text(all_summaries_text, max_length="short")
            combined_summary = combined_summary_result["summary"]
            print(f"✓ Combined summary created: {len(combined_summary)} characters")
        except Exception as e:
            print(f"✗ Error creating combined summary: {str(e)}")
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
            "timestamp": __import__('datetime').datetime.now().isoformat()
        }
        
        # Step 8: Save final summary to JSON file
        final_summary_file = os.path.join(output_dir, "summarize_after_chunks.json")
        with open(final_summary_file, 'w', encoding='utf-8') as f:
            json.dump(summarize_after_chunks, f, indent=2, ensure_ascii=False)
        
        print(f"\n{'='*80}")
        print(f"✓ Final summary saved to: {final_summary_file}")
        print(f"{'='*80}")
        
        # Return result with file paths
        summarize_after_chunks["output_files"] = {
            "chunking_output": chunking_output_file,
            "final_summary": final_summary_file
        }
        
        return summarize_after_chunks
        
    except Exception as e:
        raise Exception(f"Error in summarize_pdf: {str(e)}")


# if __name__ == "__main__":
#     # Set your PDF path here
#     pdf_path = "/home/ahmedubuntu/AI_EDA/code/summarization_agent/resources/Ahmed_Tamer_Samir_CV.pdf"
    
#     try:
#         # Test the summarize_pdf function with semantic chunking
#         result = summarize_pdf(pdf_path)
        
#         # Save results to JSON
#         output_file = "output/pdf_chunking_output.json"
#         # Don't save the full chunks to keep the file manageable, just the metadata
#         save_result = {k: v for k, v in result.items() if k != 'chunks'}
        
#         with open(output_file, 'w', encoding='utf-8') as f:
#             json.dump(save_result, f, indent=2, ensure_ascii=False)
        
#         print(f"\n✓ Results saved to: {output_file}")
        
#     except Exception as e:
#         print(f"Error: {e}")
