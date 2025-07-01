from pydantic import BaseModel, HttpUrl

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

    class Config:
        orm_mode = True