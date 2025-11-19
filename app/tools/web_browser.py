"""Wrapper around browser-use / Playwright for autonomous browsing."""
from __future__ import annotations

from playwright.async_api import async_playwright


class WebBrowserTool:
    """Simple Playwright wrapper to visit a page and return HTML content."""

    async def fetch_page(self, url: str, wait_until: str = "load") -> str:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, wait_until=wait_until)
            content = await page.content()
            await browser.close()
            return content

    async def screenshot(self, url: str, path: str = "screenshot.png", full_page: bool = True) -> str:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url)
            await page.screenshot(path=path, full_page=full_page)
            await browser.close()
            return path
