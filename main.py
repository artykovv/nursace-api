from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from catalog.routers.routers import routers as catalog_router
from user.router.router import router as user_router
from storage.router import router as storage_router
from session.routers.router import router as session_router
from cart.routers.routers import routers as cart
from order.routers.routers import routers as order
from docs.routers.routers import routers as docs
from custom.routers.routers import routers as custom
from notification.router.router import router as notification
from report.routers.routers import routers as report
from leads.routers.router import router as leads
from facebook.router import router as facebook
from discounts.routers.routers import routers as discounts


from config.config import origins

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    return {"message": "Hello, World! "}

app.include_router(catalog_router)
app.include_router(user_router)
app.include_router(storage_router)
app.include_router(session_router)
app.include_router(cart)
app.include_router(order)
app.include_router(docs)
app.include_router(custom)
app.include_router(notification)
app.include_router(report)
app.include_router(leads)
app.include_router(facebook)
app.include_router(discounts)