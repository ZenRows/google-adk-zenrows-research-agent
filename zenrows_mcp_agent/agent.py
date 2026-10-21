"""Google ADK agent that uses the hosted Zenrows MCP server."""

import os
from pathlib import Path

from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import MCPToolset, StreamableHTTPConnectionParams

# load the API keys stored in the project environment file.
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

# connect to the hosted Zenrows MCP server with the API key as a bearer token.
zenrows_toolset = MCPToolset(
    connection_params=StreamableHTTPConnectionParams(
        url="https://mcp.zenrows.com/mcp",
        headers={"Authorization": f"Bearer {os.getenv('ZENROWS_API_KEY', '')}"},
    )
)

# the agent chooses between the Zenrows scrape and browser tools on its own.
root_agent = Agent(
    model="gemini-3.6-flash",
    name="web_research_mcp_agent",
    description="Researches public web pages through the Zenrows MCP server.",
    instruction=(
        "You are a web research agent. Use the Zenrows tools whenever a task "
        "requires content from a supplied URL. Base the answer only on returned "
        "page content, mention the source URL, and state clearly when retrieval "
        "fails or the page does not contain the requested information."
    ),
    tools=[zenrows_toolset],
)
