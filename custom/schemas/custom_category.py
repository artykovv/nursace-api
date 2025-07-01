from pydantic import BaseModel
from typing import List, Optional

class CustomCategoryBase(BaseModel):
    category_name: str

class CustomCategoryCreate(CustomCategoryBase):
    pass

class CustomCategoryUpdate(CustomCategoryBase):
    pass

class CustomCategoryInDB(CustomCategoryBase):
    category_id: int

    class Config:
        orm_mode = True