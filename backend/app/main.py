from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic_settings import BaseSettings
from typing import List
import os

from .database import init_db, Base, engine
from .routers import fabrics, products, categories, orders, public, uploads

class Settings(BaseSettings):
    SECRET_KEY: str = "dev"
    DATABASE_URL: str = "sqlite:///./app.db"
    CORS_ALLOW_ORIGINS: str = "http://127.0.0.1:5173,http://localhost:5173"

    class Config:
        env_file = ".env"

settings = Settings()

app = FastAPI(title="Wanshop API", version="0.1.0")

# CORS
allow_origins: List[str] = [o.strip() for o in settings.CORS_ALLOW_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files (uploads)
static_dir = os.path.join(os.path.dirname(__file__), "static")
# ensure the directory exists to avoid RuntimeError on mount
os.makedirs(os.path.join(static_dir, "uploads"), exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# DB init
init_db()

# Routers
app.include_router(fabrics.router, prefix="/api/fabrics", tags=["fabrics"])
app.include_router(categories.router, prefix="/api/categories", tags=["categories"])
app.include_router(products.router, prefix="/api/products", tags=["products"])
app.include_router(orders.router, prefix="/api/orders", tags=["orders"])
app.include_router(public.router, prefix="/api/public", tags=["public"])
app.include_router(uploads.router, prefix="/api/upload", tags=["uploads"])

@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.get("/__version")
def version():
    return {"version": "0.1.0"}
