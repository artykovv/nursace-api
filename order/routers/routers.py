from fastapi import APIRouter
from .order.router import router as order
from .checkout.router import router as checkout

routers = APIRouter()

routers.include_router(order)
routers.include_router(checkout)