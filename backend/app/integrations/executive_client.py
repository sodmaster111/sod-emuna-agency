"""Client adapter for the Executive LangGraph service."""

from typing import Any, Dict, Optional

import httpx
from pydantic_settings import BaseSettings


class ExecServiceError(Exception):
    """Raised when the Executive LangGraph service returns an error."""


class ExecServiceSettings(BaseSettings):
    EXEC_SERVICE_URL: str = "http://executive-langgraph:8100"

    class Config:
        env_file = ".env"
        case_sensitive = False


def _get_settings() -> ExecServiceSettings:
    return ExecServiceSettings()


async def exec_decide(question: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Call the Executive service to obtain a decision.

    Args:
        question: The question to send to the Executive service.
        context: Optional contextual data for the decision.

    Returns:
        Parsed JSON response containing decision details.

    Raises:
        ExecServiceError: If the service returns an error or cannot be reached.
    """

    settings = _get_settings()
    url = f"{settings.EXEC_SERVICE_URL.rstrip('/')}/exec/decide"
    payload = {"question": question, "context": context}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=30.0)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as exc:
        raise ExecServiceError(f"Failed to reach Executive service: {exc}") from exc
    except Exception as exc:  # pragma: no cover - defensive
        raise ExecServiceError(f"Unexpected error calling Executive service: {exc}") from exc
