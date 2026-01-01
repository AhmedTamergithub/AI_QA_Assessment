"""
MCP Client Module
Handles communication with the MCP summarization server.
"""

import json
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def call_mcp_summarize(text):
    """
    Create an MCP client and call the summarize_text tool from the MCP server.
    
    Args:
        text: The text to summarize
    """
    if not text:
        print("\n[ERROR] No text to summarize")
        return
    
    print("\n" + "="*80)
    print("CALLING MCP SERVER TO SUMMARIZE TEXT")
    print("="*80)
    
    try:
        # Define server parameters for the MCP server
        import sys
        import os
        
        # Get the absolute path to the server script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        server_script = os.path.join(script_dir, "summarization_server.py")
        
        server_params = StdioServerParameters(
            command=sys.executable,  # Use the same Python interpreter
            args=[server_script],
            env=None
        )
        
        # Create and connect to the MCP server
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize the connection
                await session.initialize()
                
                # List available tools
                tools = await session.list_tools()
                print(f"\n[MCP Client] Available tools: {[tool.name for tool in tools.tools]}")
                
                # Call the summarize_text tool
                print(f"\n[MCP Client] Calling summarize_text tool with {len(text)} characters...")
                result = await session.call_tool("summarize_text", arguments={
                    "text": text,
                    "max_length": "short"
                })
                
                # Parse the result
                result_data = json.loads(result.content[0].text)
                
                if "error" in result_data:
                    print(f"\n[ERROR] Summarization failed: {result_data['error']}")
                    return
                
                # Print the summary
                print("\n" + "="*80)
                print("SUMMARY FROM MCP SERVER:")
                print("="*80)
                print(result_data["summary"])
                print("="*80)
                print(f"\nSummary length: {result_data['metadata']['summary_length']} characters")
                print(f"Model used: {result_data['metadata']['model']}")
                print(f"Compression ratio: {result_data['metadata']['input_length'] / result_data['metadata']['summary_length']:.2f}x")
                print("\n[SUCCESS] Summarization complete!")
                
    except Exception as e:
        print(f"\n[ERROR] MCP client error: {e}")
        import traceback
        traceback.print_exc()