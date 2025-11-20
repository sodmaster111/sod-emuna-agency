"""Marketing research helpers using browser-use automation."""
from __future__ import annotations

from typing import List

from browser_use import Browser, BrowserConfig

TWITTER_TRENDS_URL = "https://x.com/explore/tabs/trending"


async def scout_trends() -> List[str]:
    """Visit social platforms and surface trending Jewish content topics."""

    browser = Browser(config=BrowserConfig(headless=True))
    page = await browser.new_page()
    await page.goto(TWITTER_TRENDS_URL)
    await page.wait_for_timeout(2000)

    trending_texts: List[str] = []
    elements = await page.query_selector_all("[data-testid='trend']")
    for element in elements:
        text = await element.inner_text()
        if text:
            trending_texts.append(text.strip())

    await browser.close()
    return trending_texts
