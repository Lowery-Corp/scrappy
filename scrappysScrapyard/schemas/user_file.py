import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UserFileCreate(BaseModel):
    user_id: uuid.UUID
    original_filename: str
    storage_key: str
    mime_type: str | None = None
    file_size_bytes: int | None = None
    checksum_sha256: str | None = None
    status: str = "uploaded"
    error_message: str | None = None
    uploaded_at: datetime | None = None
    parsed_at: datetime | None = None
    indexed_at: datetime | None = None
    ready_at: datetime | None = None


class UserFileUpdate(BaseModel):
    user_id: uuid.UUID | None = None
    original_filename: str | None = None
    storage_key: str | None = None
    mime_type: str | None = None
    file_size_bytes: int | None = None
    checksum_sha256: str | None = None
    status: str | None = None
    error_message: str | None = None
    uploaded_at: datetime | None = None
    parsed_at: datetime | None = None
    indexed_at: datetime | None = None
    ready_at: datetime | None = None


class UserFileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    # id: int
    file_id: uuid.UUID
    user_id: uuid.UUID
    # original_filename: str
    storage_key: str
    mime_type: str | None
    file_size_bytes: int | None
    # checksum_sha256: str | None
    status: str
    # error_message: str | None
    # uploaded_at: datetime
    # parsed_at: datetime | None
    # indexed_at: datetime | None
    # ready_at: datetime | None
    created_at: datetime
    updated_at: datetime


class ReadUserFiles(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    files: list[UserFileRead]