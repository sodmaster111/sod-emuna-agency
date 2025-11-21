from __future__ import annotations

from celery import Celery

from app.core.config import settings

celery_app = Celery("sod_worker", broker=settings.redis_url, backend=settings.redis_url)
celery_app.conf.task_serializer = "json"
celery_app.conf.result_serializer = "json"
celery_app.conf.accept_content = ["json"]


__all__ = ["celery_app"]
