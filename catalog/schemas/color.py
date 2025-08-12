from pydantic import BaseModel

class ColorCreate(BaseModel):
    color_name: str
    color_hex: str | None = None

class ColorUpdate(BaseModel):
    color_name: str | None = None
    color_hex: str | None = None