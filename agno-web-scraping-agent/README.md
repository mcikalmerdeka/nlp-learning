# Agno Web Scraping Agent

Testing repository for web scraping and crawling tools using the [Agno Agent Framework](https://github.com/agno-agi/agno).

## Overview

This repo contains examples of different web scraping tools integrated with Agno agents:

- **Crawl4ai** - Browser-based crawling with Playwright ([docs](https://docs.agno.com/concepts/tools/toolkits/web_scrape/crawl4ai))
- **Firecrawl** - Web scraping and crawling API ([docs](https://docs.agno.com/concepts/tools/toolkits/web_scrape/firecrawl))
- **ScrapeGraph** - Smart scraping with structured extraction ([docs](https://docs.agno.com/concepts/tools/toolkits/web_scrape/scrapegraph))

## Setup

1. Install dependencies:
```bash
uv sync
```

2. Install Playwright browsers (for Crawl4ai):
```bash
python -m playwright install chromium
```

3. Create `.env` file with API keys:
```bash
OPENAI_API_KEY=your-openai-key
SCRAPEGRAPH_API_KEY=your-scrapegraph-key  # Only needed for scrapegraph_agent.py
```

## Usage

Run individual agent examples:

```bash
python crawl4ai_agent.py      # Uses Crawl4ai for browser-based scraping
python firecrawl_agent.py     # Uses Firecrawl API for crawling
python scrapegraph_agent.py   # Uses ScrapeGraph for structured extraction
```

## Requirements

- Python >= 3.11
- OpenAI API key (for all agents)
- ScrapeGraph API key (only for `scrapegraph_agent.py`)

