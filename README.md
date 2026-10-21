# Build a Web Research Agent With Google ADK and Zenrows

This project shows how to give a Google Agent Development Kit (ADK) agent access to a protected or JavaScript-rendered web page. Google ADK handles the agent workflow, while a Python function calls Zenrows [Fetch](https://docs.zenrows.com/fetch/api-reference) and returns Markdown that the model can use for its answer. A second agent reaches the same pages through the hosted Zenrows MCP server, with no function code.

Companion code for the Zenrows article [Build a Web Research Agent With Google ADK and Zenrows](https://www.zenrows.com/blog/web-research-agent-google-adk-zenrows).

## Features

- Registers a typed Python function as a Google ADK tool.
- Retrieves protected pages with Zenrows Adaptive Stealth Mode (`mode=auto`).
- Returns Markdown instead of passing an entire raw HTML document to the model.
- Reports retrieval errors as structured tool results, with the API key removed from the error text.
- Compares Zenrows with a standard HTTP request on the same URL.
- Connects a second ADK agent to the hosted Zenrows MCP server through `MCPToolset`.
- Includes unit tests that replace external HTTP calls with test responses, so running `pytest` does not spend Zenrows or Gemini credits.

## Prerequisites

- Python 3.10 or later
- A [Google AI Studio API key](https://aistudio.google.com/app/apikey)
- A [Zenrows API key](https://app.zenrows.com/register)

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/ZenRows/google-adk-zenrows-research-agent.git
cd google-adk-zenrows-research-agent
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the environment

macOS and Linux:

```bash
source .venv/bin/activate
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
python -m pip install -r requirements.txt
```

`requirements.txt` pins the versions the project was tested with (`google-adk` 2.9.2 with its MCP extra) and installs the project itself.

## Configuration

Copy the environment template:

```bash
cp .env.example .env
```

On Windows PowerShell, use:

```powershell
Copy-Item .env.example .env
```

Add your keys to `.env`:

```dotenv
GOOGLE_API_KEY=your_google_api_key
ZENROWS_API_KEY=your_zenrows_api_key
```

`GOOGLE_API_KEY` comes from Google AI Studio and `ZENROWS_API_KEY` from your Zenrows dashboard. The `.gitignore` file excludes `.env` so the keys are not committed.

## Project Structure

```text
google-adk-zenrows-research-agent/
├── scripts/
│   ├── compare_fetch.py
│   └── list_mcp_tools.py
├── tests/
│   ├── test_agent.py
│   ├── test_mcp_agent.py
│   └── test_web.py
├── zenrows_mcp_agent/
│   ├── __init__.py
│   └── agent.py
├── zenrows_research_agent/
│   ├── __init__.py
│   ├── agent.py
│   └── web.py
├── .env.example
├── .gitignore
├── LICENSE
├── pyproject.toml
├── README.md
└── requirements.txt
```

- `zenrows_research_agent/web.py`: the standard HTTP and Zenrows retrieval functions.
- `zenrows_research_agent/agent.py`: the ADK agent that registers `fetch_protected_page` as a tool.
- `zenrows_mcp_agent/agent.py`: the ADK agent connected to the Zenrows MCP server.
- `scripts/compare_fetch.py`: sends one URL through both retrieval paths and prints the results.
- `scripts/list_mcp_tools.py`: checks which Zenrows MCP tools ADK loads.

## How It Works

```text
Research prompt with a URL
  ↓
Google ADK agent (Gemini) picks a tool
  ↓
fetch_protected_page  ──or──  Zenrows MCP tools (MCPToolset)
  ↓
Zenrows Fetch with mode=auto returns the page as Markdown
  ↓
Gemini answers from the page content and cites the URL
```

The `fetch_protected_page` function accepts a public URL and sends it to Fetch. It enables Adaptive Stealth Mode with `mode=auto`, asks for Markdown, and returns a dictionary containing the retrieval status, URL, and page content. `original_status=true` makes Zenrows return the target page's status code, so an error page from the target is reported as an error.

The 180-second timeout gives `mode=auto` enough time to complete retrieval on the protected target. The function also checks that the response contains page content before returning it to the agent, preventing an empty response from being treated as a successful retrieval.

Google ADK inspects the function signature and docstring when the function is added to the agent's `tools` list. The agent uses the `gemini-3.6-flash` model, which can select the tool, pass it a URL, and use the returned content to answer the user's research question.

The function limits returned content to 12,000 characters so a large page does not fill the model context unnecessarily. For a production system, replace this simple limit with section selection, extraction, or chunking based on the pages you need to research.

The MCP agent skips the function: `MCPToolset` connects to `https://mcp.zenrows.com/mcp` with your API key as a bearer token, and ADK loads the Zenrows tools (`scrape`, `extract`, Crawl, Batch and browser tools) from the server.

## Running the Project

### Run the tests

```bash
pytest -q
```

### Compare standard HTTP and Zenrows

```bash
python scripts/compare_fetch.py
```

### Run the function-tool agent

```bash
adk run zenrows_research_agent
```

Then submit this task:

```text
Fetch https://www.scrapingcourse.com/cloudflare-challenge and report the page title, whether the challenge was passed, and the visible verification text. Cite the source URL.
```

### Run the MCP agent

Check which Zenrows tools ADK loads, then start the agent and describe the task in plain English:

```bash
python scripts/list_mcp_tools.py
adk run zenrows_mcp_agent
```

`adk web` opens both agents in ADK's browser UI instead of the terminal.

## Output

The comparison run produced:

```json
{
  "standard_http": {
    "status": "blocked",
    "url": "https://www.scrapingcourse.com/cloudflare-challenge",
    "status_code": 403,
    "content_preview": "<!DOCTYPE html><html lang=\"en-US\"><head><title>Just a moment...</title><meta http-equiv=\"Content-Type\" content=\"text/html; charset=UTF-8\"><meta http-equiv=\"X-UA-Compatible\" content=\"IE=Edge\"><meta name=\"robots\" content=\"noindex,nofollow\"><meta name=\"viewport\" content=\"width=device-width,initial-scal",
    "error": null
  },
  "zenrows": {
    "status": "success",
    "url": "https://www.scrapingcourse.com/cloudflare-challenge",
    "status_code": null,
    "content_preview": "[![](https://www.scrapingcourse.com/assets/images/logo.svg) Scraping Course](http://www.scrapingcourse.com/)\n\n# Cloudflare Challenge\n\n![](https://www.scrapingcourse.com/assets/images/challenge.svg)\n\n## You bypassed the Cloudflare challenge! :D",
    "error": null
  }
}
```

The MCP tool check printed (after ADK's experimental-feature warnings):

```text
Loaded 62 Zenrows tools
scrape: available
extract: available
crawl_create: available
batch_create: available
browser_navigate: available
```

The function-tool agent answered:

```text
[web_research_agent]: Based on the content retrieved from [https://www.scrapingcourse.com/cloudflare-challenge](https://www.scrapingcourse.com/cloudflare-challenge):

* **Page Title / Main Heading:** Cloudflare Challenge
* **Challenge Status:** Passed / Bypassed
* **Visible Verification Text:** "You bypassed the Cloudflare challenge! :D"
* **Source URL:** `https://www.scrapingcourse.com/cloudflare-challenge`
```

## Technologies

- Python
- Google Agent Development Kit (ADK)
- Gemini API
- Zenrows Fetch API
- Zenrows MCP server
- Requests
- pytest
- Ruff

## Related Article

This repository accompanies the Zenrows article:

**Build a Web Research Agent With Google ADK and Zenrows**

https://www.zenrows.com/blog/web-research-agent-google-adk-zenrows
