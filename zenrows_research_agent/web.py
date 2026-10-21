"""Web retrieval tools used by the Google ADK agent."""

import os

import requests

ZENROWS_ENDPOINT = "https://api.zenrows.com/v1/"
DEFAULT_TIMEOUT = 180
MAX_TOOL_CONTENT = 12_000


def fetch_with_http(url: str) -> dict:
    """Fetch a public URL with a standard HTTP request for comparison."""
    try:
        # send the request without a protected-site access service.
        response = requests.get(
            url,
            headers={"User-Agent": "google-adk-research-agent/0.1"},
            timeout=20,
        )
    except requests.RequestException as exc:
        return {"status": "error", "url": url, "error": str(exc)}

    return {
        "status": "success" if response.ok else "blocked",
        "url": url,
        "status_code": response.status_code,
        "content": response.text[:2_000],
    }


def fetch_protected_page(url: str) -> dict:
    """Fetch a protected or JavaScript-rendered page through Zenrows.

    Args:
        url: The complete public URL the research agent needs to read.

    Returns:
        A dictionary containing the request status, source URL, and page content.
    """
    api_key = os.getenv("ZENROWS_API_KEY")
    if not api_key:
        return {
            "status": "error",
            "url": url,
            "error": "ZENROWS_API_KEY is not configured.",
        }

    # let Adaptive Stealth Mode select the request configuration.
    params = {
        "apikey": api_key,
        "url": url,
        "mode": "auto",
        "response_type": "markdown",
        "original_status": "true",
    }

    try:
        # give Adaptive Stealth Mode enough time to retrieve the page.
        response = requests.get(
            ZENROWS_ENDPOINT,
            params=params,
            timeout=DEFAULT_TIMEOUT,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        # remove the API key from the error text before it reaches the model.
        error = str(exc).replace(api_key, "[REDACTED]")
        return {"status": "error", "url": url, "error": error}

    # do not return a successful result without page content.
    if not response.text.strip():
        return {
            "status": "error",
            "url": url,
            "error": "Zenrows returned an empty response.",
        }

    return {
        "status": "success",
        "url": url,
        "content": response.text[:MAX_TOOL_CONTENT],
    }
