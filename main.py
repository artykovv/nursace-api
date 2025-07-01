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

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8080", "http://127.0.0.1:8001", "http://127.0.0.1:8002", "https://7cce-95-87-69-227.ngrok-free.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

app.include_router(catalog_router)
app.include_router(user_router)
app.include_router(storage_router)
app.include_router(session_router)
app.include_router(cart)
app.include_router(order)
app.include_router(docs)
app.include_router(custom)
