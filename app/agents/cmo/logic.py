"""Actionable marketing playbooks for the CMO agent."""
from __future__ import annotations

from typing import Any, Dict, Optional

from app.tools.web_agent import WebAgent


async def create_viral_comment(trend: str, destination_url: Optional[str] = None) -> Dict[str, Any]:
    """Draft and attempt to publish a viral-ready comment for a trend.

    The comment leans on urgency and community participation. When a destination
    URL is provided, the WebAgent will attempt to post the comment directly
    using browser automation (browser-use if available, otherwise Playwright).
    """

    comment = (
        f"🔥 {trend} is blowing up. We love seeing community momentum—what's your take? "
        "Join us and let's build something meaningful together."
    )

    agent = WebAgent()
    if destination_url:
        post_result = await agent.post_comment(destination_url, comment)
    else:
        post_result = {"status": "skipped", "reason": "No destination_url provided"}

    return {"trend": trend, "comment": comment, "post_result": post_result}


__all__ = ["create_viral_comment"]
