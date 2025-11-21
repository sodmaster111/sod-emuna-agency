"""browser-use wrapper for autonomous web actions used by marketing agents."""
from __future__ import annotations

import asyncio
import importlib.util
from typing import Any, Dict, Optional

import requests

from app.core.tracing import end_span, start_span

async_playwright = None
PlaywrightTimeoutError = Exception
if importlib.util.find_spec("playwright"):
    from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

Agent = None
if importlib.util.find_spec("browser_use"):
    from browser_use.agent import Agent  # type: ignore[assignment]


class WebAgent:
    """Lightweight facade over browser-use with Playwright and requests fallbacks."""

    def __init__(self, headless: bool = True, navigation_timeout: int = 15000) -> None:
        self.agent = Agent() if Agent else None
        self.headless = headless
        self.navigation_timeout = navigation_timeout

    async def visit_url(self, url: str) -> Dict[str, Any]:
        """Visit a URL and return metadata or automation results."""

        span = start_span("web_agent.visit_url", input={"url": url})
        if self.agent:
            result = await self.agent.run(
                f"Open {url} and provide a concise summary of the page along with key calls to action."
            )
            payload = {"driver": "browser_use", "result": result, "target": url}
            end_span(span, output=payload)
            return payload

        if async_playwright:
            snapshot = await self._playwright_snapshot(url)
            end_span(span, output=snapshot)
            return snapshot

        fallback = await asyncio.to_thread(self._requests_fetch, url)
        end_span(span, output=fallback)
        return fallback

    async def execute_task(self, goal: str, start_url: Optional[str] = None) -> Dict[str, Any]:
        """Execute an autonomous browsing goal, starting at an optional URL."""

        span = start_span("web_agent.execute_task", input={"goal": goal, "start_url": start_url})
        if self.agent:
            prompt = goal
            if start_url:
                prompt = f"Start at {start_url}. {goal}"
            result = await self.agent.run(prompt)
            payload = {"driver": "browser_use", "result": result}
            end_span(span, output=payload)
            return payload

        if start_url and async_playwright:
            snapshot = await self._playwright_snapshot(start_url)
            snapshot["result"] = "browser_use not installed; provided snapshot only"
            end_span(span, output=snapshot)
            return snapshot

        payload = {"driver": "requests", "result": goal}
        end_span(span, output=payload)
        return payload

    async def post_comment(
        self,
        url: str,
        comment: str,
        field_selector: str = "textarea, [contenteditable='true'], [name='comment'], [aria-label*='comment']",
    ) -> Dict[str, Any]:
        """Navigate to a URL and attempt to post a comment suitable for social feeds."""

        span = start_span("web_agent.post_comment", input={"url": url, "comment": comment})
        if self.agent:
            instruction = (
                f"Navigate to {url}. Find the primary comment box and post the following comment verbatim: "
                f'"{comment}". Confirm posting and capture any response or confirmation text.'
            )
            result = await self.agent.run(instruction)
            payload = {"driver": "browser_use", "result": result, "comment": comment, "target": url}
            end_span(span, output=payload)
            return payload

        if async_playwright:
            result = await self._playwright_post_comment(url, comment, field_selector)
            end_span(span, output=result)
            return result

        payload = {
            "driver": "requests",
            "status": "unavailable",
            "reason": "browser automation not installed",
        }
        end_span(span, output=payload)
        return payload

    def _requests_fetch(self, url: str) -> Dict[str, Any]:
        response = requests.get(url, timeout=10)
        return {"driver": "requests", "url": url, "status": response.status_code, "length": len(response.text)}

    async def _playwright_snapshot(self, url: str) -> Dict[str, Any]:
        if not async_playwright:
            return {"driver": "playwright", "url": url, "error": "playwright not installed"}

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=self.headless)
                page = await browser.new_page()
                await page.goto(url, wait_until="domcontentloaded", timeout=self.navigation_timeout)
                content = await page.content()
                title = await page.title()
                await browser.close()
                return {
                    "driver": "playwright",
                    "url": url,
                    "title": title,
                    "length": len(content),
                }
        except PlaywrightTimeoutError as exc:  # pragma: no cover - depends on live network
            return {"driver": "playwright", "url": url, "error": str(exc)}

    async def _playwright_post_comment(self, url: str, comment: str, field_selector: str) -> Dict[str, Any]:
        if not async_playwright:
            return {"driver": "playwright", "url": url, "error": "playwright not installed"}

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            page = await browser.new_page()
            await page.goto(url, wait_until="domcontentloaded", timeout=self.navigation_timeout)

            field = page.locator(field_selector).first
            if await field.count() == 0:
                await browser.close()
                return {
                    "driver": "playwright",
                    "url": url,
                    "status": "failed",
                    "reason": "No comment field detected",
                }

            await field.click()
            await field.fill(comment)

            submit = page.locator("button[type='submit'], button:has-text('Post'), button:has-text('Comment')").first
            if await submit.count() > 0:
                await submit.click()
                await page.wait_for_timeout(1000)
            else:
                await field.press("Enter")
                await page.wait_for_timeout(500)

            confirmation_preview = await page.text_content("body")
            await browser.close()
            return {
                "driver": "playwright",
                "url": url,
                "status": "posted",
                "comment": comment,
                "confirmation_preview": confirmation_preview[:500] if confirmation_preview else None,
            }


__all__ = ["WebAgent"]
