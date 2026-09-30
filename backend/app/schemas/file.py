from datetime import datetime

from pydantic import BaseModel


class  FileMetadataResponse(BaseModel):
    id: int
    filename: str
    size: int
    content_type: str | None
    created_at: datetime


class FileUploadResponse(BaseModel):
    message: str
    file_id: int
    filename: str
    size: int
    content_type: str | None