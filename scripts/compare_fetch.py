"""Compare standard HTTP access with Zenrows access."""

import json

from dotenv import load_dotenv

from zenrows_research_agent.web import fetch_protected_page, fetch_with_http

TARGET_URL = "https://www.scrapingcourse.com/cloudflare-challenge"


def summarize(result: dict) -> dict:
    """Reduce a fetch result to fields that are safe to print."""
    return {
        "status": result["status"],
        "url": result["url"],
        "status_code": result.get("status_code"),
        "content_preview": result.get("content", "")[:300],
        "error": result.get("error"),
    }


if __name__ == "__main__":
    # load the Zenrows API key from the project environment.
    load_dotenv()

    # retrieve the same URL through both access methods.
    comparison = {
        "standard_http": summarize(fetch_with_http(TARGET_URL)),
        "zenrows": summarize(fetch_protected_page(TARGET_URL)),
    }

    # print the comparison without exposing the API key.
    print(json.dumps(comparison, indent=2))
