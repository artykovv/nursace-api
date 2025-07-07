from pydantic import BaseModel, ConfigDict
from typing import List, Optional

class CustomCategoryBase(BaseModel):
    category_name: str

class CustomCategoryCreate(CustomCategoryBase):
    pass

class CustomCategoryUpdate(CustomCategoryBase):
    pass

class CustomCategoryInDB(CustomCategoryBase):
    category_id: int

    model_config = ConfigDict(from_attributes=True)