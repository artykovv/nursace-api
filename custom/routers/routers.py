from fastapi import APIRouter
from .carousel.router import router as carousel
from .category.router import router as category

routers = APIRouter()

routers.include_router(carousel)
routers.include_router(category)