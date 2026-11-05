from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import MetaData

metadata = MetaData(schema="app")

class Base(DeclarativeBase):
    metadata = metadata

from models import (
    user_filestore,
    file_job,
    user_file,
    user_conversation,
    conversation_message,
    file_chunk,
    retrieval_log,
    query_log,
)# noqa: F401