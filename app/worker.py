"""Celery worker entrypoint configured for Redis messaging."""
from __future__ import annotations

from celery import Celery

from app.core.config import config

celery_app = Celery(
    "sod_core_worker",
    broker=config.redis_url,
    backend=config.redis_url,
)

celery_app.conf.task_routes = {"app.worker.ping": {"queue": "health"}}
celery_app.conf.task_serializer = "json"
celery_app.conf.result_serializer = "json"
celery_app.conf.accept_content = ["json"]


@celery_app.task(name="app.worker.ping")
def ping() -> str:
    """Lightweight task to confirm the worker can receive jobs."""

    return "pong"


__all__ = ["celery_app", "ping"]
