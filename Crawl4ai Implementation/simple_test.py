"""
Simple test of crawl4ai. Created from the skills of crawl4ai.
"""

import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
from pathlib import Path

async def main():
    # Browser configuration (controls browser behavior)
    browser_config = BrowserConfig(
        headless=True,  # Run without GUI
        viewport_width=1920,
        viewport_height=1080,
    )
    
    # Crawler configuration (controls crawl behavior)
    crawler_config = CrawlerRunConfig(
        page_timeout=30000,  # 30 seconds timeout
        screenshot=False,  # Take screenshot
        remove_overlay_elements=True  # Remove popups/overlays
    )
    
    # Execute crawl with arun()
    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(
            url="https://medium.com/towards-artificial-intelligence/5-underrated-libraries-frameworks-for-ai-engineers-to-learn-in-2026-751135919d8e",
            config=crawler_config
        )
        
        # CrawlResult contains everything
        print(f"Success: {result.success}")
        print(f"HTML length: {len(result.html)}")
        print(f"Markdown length: {len(result.markdown)}")
        print(f"Links found: {len(result.links)}")
        
        # Save markdown
        output_dir = Path("output")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / "crawled_output.md"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(result.markdown)
        print(f"📄 Markdown saved to: {output_file}")
        
        # Print the full markdown content
        print("\n" + "="*80)
        print("MARKDOWN CONTENT:")
        print("="*80)
        print(result.markdown)

if __name__ == "__main__":
    asyncio.run(main())
