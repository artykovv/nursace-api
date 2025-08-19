from fastapi import APIRouter
from .outlet.router import router

routers = APIRouter()

routers.include_router(router)


