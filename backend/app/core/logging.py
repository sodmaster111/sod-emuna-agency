"""Logging configuration utilities for the backend services.

This module standardises JSON logging for API and worker processes so that
log forwarders such as Dozzle receive consistent records containing a
request identifier when available.
"""
from __future__ import annotations

import contextvars
import logging
import os
import sys
from typing import Any

# Context variable used by middleware and other callers to attach a request id
# to each log record. Defaults to a dash when no request context is available
# (e.g., background jobs).
request_id_ctx_var: contextvars.ContextVar[str] = contextvars.ContextVar(
    "request_id", default="-"
)


class RequestIdFilter(logging.Filter):
    """Attach the current request id to every log record."""

    def filter(self, record: logging.LogRecord) -> bool:  # noqa: D401
        record.request_id = request_id_ctx_var.get("-")
        return True


def configure_logging() -> None:
    """Configure root logging with JSON formatting to stdout.

    The log level is controlled by the ``LOG_LEVEL`` environment variable and
    defaults to ``INFO``.
    """

    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove existing handlers to prevent duplicate logs when reloading.
    for handler in list(root_logger.handlers):
        root_logger.removeHandler(handler)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)
    handler.addFilter(RequestIdFilter())
    handler.setFormatter(
        logging.Formatter(
            '{"ts":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s","msg":"%(message)s","request_id":"%(request_id)s"}'
        )
    )

    root_logger.addHandler(handler)


def set_request_id(request_id: str) -> contextvars.Token[Any]:
    """Set the active request id in the context variable."""

    return request_id_ctx_var.set(request_id)


def reset_request_id(token: contextvars.Token[Any]) -> None:
    """Reset the request id context to its previous value."""

    request_id_ctx_var.reset(token)
