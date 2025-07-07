from pydantic import BaseModel, ConfigDict, HttpUrl

class CarouselImageBase(BaseModel):
    src: str
    href: str

class CarouselImageCreate(CarouselImageBase):
    pass

class CarouselImageUpdate(BaseModel):
    src: str | None = None
    href: str | None = None

class CarouselImageRead(CarouselImageBase):
    id: int

    model_config = ConfigDict(from_attributes=True)