"""Langfuse tracing utilities with Pinkas fallback logging."""
from __future__ import annotations

import logging
from contextvars import ContextVar
from typing import Any, Dict, Optional

from langfuse import Langfuse
from langfuse.callback import CallbackHandler

from app.core.config import get_settings
from app.db.models import persist_pinkas_entry

logger = logging.getLogger(__name__)

_settings = get_settings()
_active_trace: ContextVar[Any] = ContextVar("active_trace", default=None)
_active_agent: ContextVar[str] = ContextVar("active_agent", default="unknown")

try:
    _langfuse_client = Langfuse(
        public_key=_settings.langfuse_public_key,
        secret_key=_settings.langfuse_secret_key,
        host=_settings.langfuse_host,
    )
    _callback_handler = CallbackHandler(
        public_key=_settings.langfuse_public_key,
        secret_key=_settings.langfuse_secret_key,
        host=_settings.langfuse_host,
    )
except Exception as exc:  # pragma: no cover - network or credentials may be absent
    logger.warning("Langfuse initialization failed: %s", exc)
    _langfuse_client = None
    _callback_handler = None


def get_tracer() -> Optional[Langfuse]:
    """Expose the initialized Langfuse client, if available."""

    return _langfuse_client


def get_callback_handler() -> Optional[CallbackHandler]:
    """Return the Langfuse callback handler for LangChain integrations."""

    return _callback_handler


def start_trace(
    name: str,
    *,
    input: Any | None = None,
    metadata: Optional[Dict[str, Any]] = None,
    agent_name: str | None = None,
) -> Any:
    """Start a root trace and track the active agent for downstream spans."""

    agent = agent_name or (metadata.get("agent") if metadata else None) or name
    _active_agent.set(agent)
    if _langfuse_client:
        try:
            trace = _langfuse_client.trace(name=name, input=input, metadata=metadata)
            _active_trace.set(trace)
            return trace
        except Exception as exc:  # pragma: no cover - depends on remote availability
            logger.warning("Langfuse trace creation failed: %s", exc)
    persist_pinkas_entry(agent_name=agent, thought=str(input or name), action="trace-start")
    return None


def start_span(
    name: str,
    *,
    input: Any | None = None,
    metadata: Optional[Dict[str, Any]] = None,
    output: Any | None = None,
) -> Any:
    """Create a span within the active trace, or persist to Pinkas on failure."""

    agent = (metadata or {}).get("agent")
    if agent:
        _active_agent.set(agent)
    agent_name = _active_agent.get()
    trace = _active_trace.get()

    if trace and hasattr(trace, "span"):
        try:
            span = trace.span(name=name, input=input, metadata=metadata)
            if output is not None and hasattr(span, "end"):
                span.end(output=output)
            return span
        except Exception as exc:  # pragma: no cover - depends on remote availability
            logger.warning("Langfuse span creation failed: %s", exc)

    persist_pinkas_entry(
        agent_name=agent_name,
        thought=f"{name}: {input}",
        action=None if output is None else str(output),
    )
    return None


def end_span(span: Any, *, output: Any | None = None) -> None:
    """Safely end a span; fallback to Pinkas when Langfuse is unavailable."""

    if span and hasattr(span, "end"):
        try:
            span.end(output=output)
            return
        except Exception as exc:  # pragma: no cover - depends on remote availability
            logger.warning("Langfuse span end failed: %s", exc)

    persist_pinkas_entry(
        agent_name=_active_agent.get(),
        thought="span-end",
        action=str(output) if output is not None else "completed",
    )


__all__ = [
    "end_span",
    "get_callback_handler",
    "get_tracer",
    "start_span",
    "start_trace",
]
