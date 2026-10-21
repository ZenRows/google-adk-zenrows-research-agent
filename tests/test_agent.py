"""Configuration tests for the Google ADK agent."""

from zenrows_research_agent.agent import root_agent


def test_root_agent_registers_zenrows_tool() -> None:
    assert root_agent.name == "web_research_agent"
    assert root_agent.model == "gemini-3.6-flash"
    assert any(
        getattr(tool, "__name__", None) == "fetch_protected_page"
        for tool in root_agent.tools
    )
