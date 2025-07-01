from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime


class SessionBase(BaseModel):
    ip_address: Optional[str] = Field(None, example="192.168.1.1")
    referer: Optional[str] = Field(None, example="https://google.com")

    utm_source: Optional[str] = Field(None, example="google")
    utm_medium: Optional[str] = Field(None, example="cpc")
    utm_campaign: Optional[str] = Field(None, example="spring_sale")
    utm_term: Optional[str] = Field(None, example="shoes")
    utm_content: Optional[str] = Field(None, example="banner1")

    time_spent: Optional[float] = Field(None, example=45.6, description="Время в секундах")
    user_agent: Optional[str] = Field(None)
    screen_resolution: Optional[str] = Field(None, example="1920x1080")
    browser_language: Optional[str] = Field(None, example="en-US")


class SessionCreate(SessionBase):
    pass


class SessionRead(SessionBase):
    id: int
    session_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)