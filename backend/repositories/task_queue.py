import uuid
from dataclasses import dataclass
from typing import Any

from kombu.exceptions import OperationalError
from celery.result import AsyncResult

from offload_tasks.celery_app import celery_app


FILE_INGESTION_TASK = "tasks.file_tasks.remote_trigger"
DEFAULT_FILE_INGESTION_QUEUE = "documents"


class TaskQueueError(RuntimeError):
    pass


@dataclass(frozen=True)
class QueuedTask:
    celery_task_id: str
    task_name: str
    queue_name: str | None = None


def enqueue_task(
    task_name: str,
    *,
    kwargs: dict[str, Any] | None = None,
    queue_name: str | None = None,
    task_id: str | None = None,
) -> QueuedTask | None:
    try:
        result: AsyncResult = celery_app.send_task( # type: ignore
            task_name,
            kwargs=kwargs or {},
            queue=queue_name,
            task_id=task_id,
        )
    except OperationalError as exc:
        raise TaskQueueError("Could not publish task to Celery broker") from exc


    return QueuedTask(
        celery_task_id=result.id,
        task_name=task_name,
        queue_name=queue_name,
    )


async def enqueue_file_ingestion_task(
    *,
    file_job_ids: list[uuid.UUID],
    queue_name: str = DEFAULT_FILE_INGESTION_QUEUE,
) -> QueuedTask:
    payload: dict[str, list[uuid.UUID]] = {
        "file_job_ids": file_job_ids,
    }

    new_task = enqueue_task(
        FILE_INGESTION_TASK,
        kwargs=payload,
        queue_name=queue_name,
    )

    if new_task is None:
        raise TaskQueueError("Failed to enqueue file ingestion task")

    return new_task
