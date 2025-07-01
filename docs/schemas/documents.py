

# Pydantic models for request/response
from datetime import datetime
from pydantic import BaseModel


class DocumentCreate(BaseModel):
    slug: str
    title: str
    content: str
    is_active: bool = True

class DocumentUpdate(BaseModel):
    slug: str | None = None
    title: str | None = None
    content: str | None = None
    is_active: bool | None = None

class DocumentResponse(BaseModel):
    id: int
    slug: str
    title: str
    content: str
    is_active: bool
    created_at: datetime
    updated_at: datetime | None

    class Config:
        from_attributes = True

class DocumentListResponse(BaseModel):
    id: int
    slug: str
    title: str
    is_active: bool
    created_at: datetime
    updated_at: datetime | None

    class Config:
        from_attributes = True