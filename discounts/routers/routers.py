from fastapi import APIRouter
from .discount.router import router 

routers = APIRouter()

routers.include_router(router)