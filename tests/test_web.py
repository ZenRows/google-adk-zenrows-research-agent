"""Tests for the web retrieval functions."""

from unittest.mock import Mock, patch

import requests

from zenrows_research_agent.web import (
    DEFAULT_TIMEOUT,
    fetch_protected_page,
    fetch_with_http,
)


@patch("zenrows_research_agent.web.requests.get")
def test_standard_http_reports_blocked_response(mock_get: Mock) -> None:
    response = Mock(ok=False, status_code=403, text="Just a moment...")
    mock_get.return_value = response

    result = fetch_with_http("https://example.com/protected")

    assert result["status"] == "blocked"
    assert result["status_code"] == 403


def test_zenrows_requires_api_key(monkeypatch) -> None:
    monkeypatch.delenv("ZENROWS_API_KEY", raising=False)

    result = fetch_protected_page("https://example.com")

    assert result["status"] == "error"
    assert result["error"] == "ZENROWS_API_KEY is not configured."


@patch("zenrows_research_agent.web.requests.get")
def test_zenrows_uses_protected_access_parameters(
    mock_get: Mock, monkeypatch
) -> None:
    monkeypatch.setenv("ZENROWS_API_KEY", "test-key")
    response = Mock(text="# Challenge passed", status_code=200)
    response.raise_for_status.return_value = None
    mock_get.return_value = response

    result = fetch_protected_page("https://example.com/protected")

    assert result["status"] == "success"
    params = mock_get.call_args.kwargs["params"]
    assert params["mode"] == "auto"
    assert params["response_type"] == "markdown"
    assert params["original_status"] == "true"
    assert "js_render" not in params
    assert "premium_proxy" not in params
    assert mock_get.call_args.kwargs["timeout"] == DEFAULT_TIMEOUT == 180


@patch("zenrows_research_agent.web.requests.get")
def test_zenrows_reports_empty_response(mock_get: Mock, monkeypatch) -> None:
    monkeypatch.setenv("ZENROWS_API_KEY", "test-key")
    response = Mock(text="  \n", status_code=200)
    response.raise_for_status.return_value = None
    mock_get.return_value = response

    result = fetch_protected_page("https://example.com/protected")

    assert result == {
        "status": "error",
        "url": "https://example.com/protected",
        "error": "Zenrows returned an empty response.",
    }


@patch("zenrows_research_agent.web.requests.get")
def test_zenrows_returns_structured_error(mock_get: Mock, monkeypatch) -> None:
    monkeypatch.setenv("ZENROWS_API_KEY", "test-key")
    mock_get.side_effect = requests.HTTPError(
        "401 Client Error for url: https://api.zenrows.com/v1/?apikey=test-key"
    )

    result = fetch_protected_page("https://example.com/protected")

    assert result == {
        "status": "error",
        "url": "https://example.com/protected",
        "error": (
            "401 Client Error for url: "
            "https://api.zenrows.com/v1/?apikey=[REDACTED]"
        ),
    }
