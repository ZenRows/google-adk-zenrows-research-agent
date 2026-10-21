"""Configuration tests for the Zenrows MCP agent."""

from google.adk.tools.mcp_tool import MCPToolset

from zenrows_mcp_agent.agent import root_agent, zenrows_toolset


def test_mcp_agent_uses_zenrows_toolset() -> None:
    assert root_agent.name == "web_research_mcp_agent"
    assert isinstance(zenrows_toolset, MCPToolset)
    assert zenrows_toolset in root_agent.tools
