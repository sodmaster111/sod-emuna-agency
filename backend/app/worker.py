import logging

from celery import Celery, signals

from app.core.config import settings
from app.core.logging import configure_logging


configure_logging()
logger = logging.getLogger(__name__)

celery_app = Celery(
    "sod_backend",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    worker_hijack_root_logger=False,
)


@signals.task_prerun.connect
def log_task_start(task_id, task, *args, **kwargs):
    logger.info("task_start", extra={"task": task.name, "task_id": task_id})


@signals.task_postrun.connect
def log_task_end(task_id, task, state, **kwargs):
    logger.info(
        "task_end",
        extra={"task": task.name, "task_id": task_id, "status": state},
    )


@celery_app.task
async def process_task(task_id: int):
    # Placeholder for task processing logic
    return {"task_id": task_id, "status": "completed"}
