from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional

class ProductImageSchema(BaseModel):
    image_id: int
    image_url: str
    is_main: bool
    order: int

    model_config = ConfigDict(from_attributes=True)

class UpdateProductImageSchema(BaseModel):
    image_url: str
    is_main: bool
    order: int

    model_config = ConfigDict(from_attributes=True)

class BaseProductSchema(BaseModel):
    id: int = Field(alias='good_id')
    name: str = Field(alias='good_name')
    price: float = Field(alias='retail_price')
    retail_price_with_discount: Optional[float]

    short_name: Optional[str]
    description: Optional[str]
    articul: Optional[str]

    category_id: Optional[int]
    manufacturer_id: Optional[int]
    collection_id: Optional[int]
    season_id: Optional[int]
    sex_id: Optional[int]
    color_id: Optional[int]
    material_id: Optional[int]
    measure_unit_id: Optional[int]
    guarantee_mes_unit_id: Optional[int]
    model_good_id: Optional[int]
    short_description: Optional[str] = Field(alias='fashion_name')
    product_size: Optional[float]

    warehouse_quantity: int

    images: List[ProductImageSchema] = []

    model_config = ConfigDict(from_attributes=True)

class UpdateProductSchema(BaseModel):
    good_name: Optional[str] = None
    retail_price: Optional[float] = None
    retail_price_with_discount: Optional[float] = None

    short_name: Optional[str] = None
    description: Optional[str] = None
    articul: Optional[str] = None

    category_id: Optional[int] = None
    manufacturer_id: Optional[int] = None
    collection_id: Optional[int] = None
    season_id: Optional[int] = None
    sex_id: Optional[int] = None
    color_id: Optional[int] = None
    material_id: Optional[int] = None
    measure_unit_id: Optional[int] = None
    guarantee_mes_unit_id: Optional[int] = None
    model_good_id: Optional[int] = None
    fashion_name: Optional[str] = None
    product_size: Optional[float] = None

    warehouse_quantity: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class Color(BaseModel):
    color_id: int
    color_name: str
    model_config = ConfigDict(from_attributes=True)

class SimilarProductSchema(BaseModel):
    id: int = Field(alias='good_id')
    color: Color
    product_size: Optional[float]

    model_config = ConfigDict(from_attributes=True)