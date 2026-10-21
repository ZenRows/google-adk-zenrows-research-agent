"""Check which Zenrows MCP tools Google ADK loads for the MCP agent."""

import asyncio

from zenrows_mcp_agent.agent import zenrows_toolset

RESEARCH_TOOLS = ["scrape", "extract", "crawl_create", "batch_create", "browser_navigate"]


async def main() -> None:
    # ask the hosted Zenrows MCP server which tools it exposes.
    tools = await zenrows_toolset.get_tools()
    await zenrows_toolset.close()
    names = {tool.name for tool in tools}

    # confirm the tools a research agent relies on are loaded.
    print(f"Loaded {len(names)} Zenrows tools")
    for name in RESEARCH_TOOLS:
        print(f"{name}: {'available' if name in names else 'not loaded'}")


if __name__ == "__main__":
    asyncio.run(main())
