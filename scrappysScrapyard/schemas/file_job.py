import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class FileJobCreate(BaseModel):
    file_id: int
    job_type: str = "ingest"
    max_attempts: int = 3
    queue_name: str | None = None


class FileJobUpdate(BaseModel):
    job_type: str | None = None
    status: str | None = None
    attempt_count: int | None = None
    max_attempts: int | None = None
    queue_name: str | None = None
    worker_id: str | None = None
    error_message: str | None = None
    queued_at: datetime | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None


class FileJobRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    job_id: uuid.UUID
    file_id: uuid.UUID
    job_type: str
    status: str
    attempt_count: int
    max_attempts: int
    queue_name: str | None
    worker_id: str | None
    error_message: str | None
    queued_at: datetime | None
    started_at: datetime | None
    finished_at: datetime | None
    created_at: datetime
    updated_at: datetime

