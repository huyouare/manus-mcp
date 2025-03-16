from typing import Any, Dict, List
import logging
import asyncio
import os
from fastapi import FastAPI
from mcp.server import FastMCP
from googlesearch import search
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("manus-mcp")

# Google Search configuration
GOOGLE_SEARCH_USER_AGENT = os.getenv("GOOGLE_SEARCH_USER_AGENT", "Mozilla/5.0")
GOOGLE_SEARCH_MAX_RESULTS = int(os.getenv("GOOGLE_SEARCH_MAX_RESULTS", "10"))

# Create the FastAPI app
app = FastAPI(title="Manus MCP Server")

# Create the MCP server
mcp_server = FastMCP(app=app, name="manus-mcp")

# Define the hello_world tool
@mcp_server.tool()
async def hello_world(name: str = "World") -> str:
    """
    Returns a friendly greeting message.
    
    Args:
        name: The name to greet. Defaults to 'World' if not provided.
    """
    logger.info(f"Saying hello to {name}")
    return f"Hello, {name}! Welcome to Manus MCP."

# Define the google_search tool
@mcp_server.tool()
async def google_search(query: str, num_results: int = None) -> List[str]:
    """
    Perform a Google search and return a list of relevant links.
    
    Use this tool when you need to find information on the web, get up-to-date data, 
    or research specific topics. The tool returns a list of URLs that match the search query.
    
    Args:
        query: The search query to submit to Google.
        num_results: The number of search results to return. Default is configured in environment.
    
    Returns:
        A list of URLs matching the search query.
    """
    if num_results is None:
        num_results = GOOGLE_SEARCH_MAX_RESULTS
    
    logger.info(f"Performing Google search for: {query} (max results: {num_results})")
    
    # Run the search in a thread pool to prevent blocking
    loop = asyncio.get_event_loop()
    try:
        links = await loop.run_in_executor(
            None, 
            lambda: list(search(
                query, 
                num_results=num_results,
                user_agent=GOOGLE_SEARCH_USER_AGENT
            ))
        )
        logger.info(f"Found {len(links)} results for query: {query}")
        return links
    except Exception as e:
        logger.error(f"Error performing Google search: {e}")
        return [f"Error performing search: {str(e)}"]

# Create a simple root endpoint for the API
@app.get("/")
async def root():
    """Root endpoint that returns basic server information."""
    return {
        "name": "Manus MCP Server",
        "version": "0.1.0",
        "description": "An MCP server that can browse the web, perform search queries, and execute code.",
        "capabilities": [
            "hello_world",
            "google_search"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=os.getenv("MCP_HOST", "127.0.0.1"), port=int(os.getenv("MCP_PORT", "8000")), reload=True) 