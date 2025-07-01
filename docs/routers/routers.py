from fastapi import APIRouter
from .docs.router import router 

routers = APIRouter()

routers.include_router(router)