"""System resource monitoring utilities for defensive operations."""

from __future__ import annotations

import logging
from typing import Dict

import psutil

logger = logging.getLogger(__name__)


def _send_ceo_emergency_signal(reason: str) -> None:
    """Emit an emergency signal instructing the CEO to pause non-critical tasks."""

    logger.critical("EMERGENCY: %s", reason)


def get_system_health() -> Dict[str, object]:
    """Return current CPU and RAM usage and signal when nearing exhaustion."""

    memory = psutil.virtual_memory()
    cpu_percent = psutil.cpu_percent(interval=0.1)
    health = {
        "memory_percent": memory.percent,
        "memory_available": memory.available,
        "memory_total": memory.total,
        "cpu_percent": cpu_percent,
        "ceo_emergency_signal": False,
    }

    if memory.percent > 90:
        _send_ceo_emergency_signal(
            "Memory consumption exceeded 90%. Pause non-critical tasks immediately.",
        )
        health["ceo_emergency_signal"] = True

    return health


__all__ = ["get_system_health"]
