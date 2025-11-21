"""Lightweight Langfuse client wrapper for tracing agent activity."""
from __future__ import annotations

import logging
import os
from typing import Any, Dict, Optional

try:  # pragma: no cover - optional dependency
    from langfuse import Langfuse
except Exception:  # pragma: no cover - optional dependency
    Langfuse = None  # type: ignore

logger = logging.getLogger(__name__)


class LangfuseClient:
    """Wrapper around the Langfuse SDK for traces and events."""

    def __init__(
        self,
        *,
        public_key: Optional[str] | None = None,
        secret_key: Optional[str] | None = None,
        host: Optional[str] | None = None,
    ) -> None:
        self.public_key = public_key or os.getenv("LANGFUSE_PUBLIC_KEY")
        self.secret_key = secret_key or os.getenv("LANGFUSE_SECRET_KEY")
        self.host = host or os.getenv("LANGFUSE_HOST")
        self._traces: Dict[str, Any] = {}

        self._client = None
        if Langfuse and self.public_key and self.secret_key and self.host:
            try:
                self._client = Langfuse(
                    public_key=self.public_key,
                    secret_key=self.secret_key,
                    host=self.host,
                )
            except Exception as exc:  # pragma: no cover - depends on env
                logger.warning("Failed to initialise Langfuse client: %s", exc)

    def start_trace(self, name: str, metadata: Optional[Dict[str, Any]] = None):
        """Start a Langfuse trace and return its identifier."""

        if not self._client:
            logger.debug("Langfuse disabled; trace start skipped")
            return None

        trace = self._client.trace(name=name, metadata=metadata)
        trace_id = getattr(trace, "id", None) or getattr(trace, "trace_id", None)
        if trace_id:
            self._traces[str(trace_id)] = trace
        return trace_id

    def log_step(
        self,
        trace_id: str | None,
        step_name: str,
        input: Any = None,
        output: Any = None,
    ) -> None:
        """Record a step/span against an existing trace."""

        if not self._client or not trace_id:
            logger.debug("Langfuse disabled or missing trace id; step not recorded")
            return

        trace = self._traces.get(str(trace_id))
        if not trace:
            logger.warning("Trace %s not found for Langfuse step", trace_id)
            return

        try:
            span = trace.span(name=step_name, input=input)
            if output is not None and hasattr(span, "end"):
                span.end(output=output)
        except Exception as exc:  # pragma: no cover - depends on env
            logger.warning("Failed to record Langfuse step: %s", exc)

    def end_trace(self, trace_id: str | None, status: str) -> None:
        """Close a trace with a final status payload."""

        if not self._client or not trace_id:
            logger.debug("Langfuse disabled or missing trace id; trace end skipped")
            return

        trace = self._traces.pop(str(trace_id), None)
        if not trace:
            logger.warning("Trace %s not found for Langfuse completion", trace_id)
            return

        try:
            if hasattr(trace, "end"):
                trace.end(output={"status": status})
        except Exception as exc:  # pragma: no cover - depends on env
            logger.warning("Failed to end Langfuse trace: %s", exc)
