from fastapi import APIRouter
from .cart.router import router as cart

routers = APIRouter()

routers.include_router(cart)