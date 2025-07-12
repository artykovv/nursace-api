from fastapi import APIRouter
from .order_report.rotuer import router as order_report
from .mini_report.router import router as mini_report

routers = APIRouter()

routers.include_router(order_report)
routers.include_router(mini_report)