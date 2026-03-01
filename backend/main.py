"""
KiranaConnect AI — FastAPI Backend Application

An AI-powered inventory management system for Kirana stores.
Provides REST APIs for inventory, predictions, orders, analytics, and chat.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import os

from .config import APP_NAME, APP_VERSION, DEBUG
from .routers import inventory, predictions, orders, analytics, chat, products, ai

# ── Create FastAPI App ──
app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="AI-powered inventory management for Kirana stores",
    debug=DEBUG
)

# ── CORS Middleware ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Include Routers ──
app.include_router(inventory.router)
app.include_router(predictions.router)
app.include_router(orders.router)
app.include_router(analytics.router)
app.include_router(chat.router)
app.include_router(products.router)
app.include_router(ai.router)

# ── Mount Frontend Static Files ──
frontend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path, html=True), name="static")


# ── Health Check ──
@app.get("/", tags=["Health"])
async def root():
    return {
        "app": APP_NAME,
        "version": APP_VERSION,
        "status": "running",
        "message": "Welcome to KiranaConnect AI — Inventory Management System",
        "docs": "/docs",
        "endpoints": {
            "inventory": "/api/v1/stores/{store_id}/inventory",
            "predictions": "/api/v1/stores/{store_id}/predictions",
            "orders": "/api/v1/stores/{store_id}/orders",
            "analytics": "/api/v1/stores/{store_id}/analytics/summary",
            "chat": "/api/v1/chat",
            "products": "/api/v1/products"
        }
    }


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "app": APP_NAME, "version": APP_VERSION}


@app.get("/api/v1/stores", tags=["Stores"])
async def get_stores():
    """Get all stores."""
    from .services.data_store import data_store
    return {"stores": data_store.stores, "total": len(data_store.stores)}


@app.get("/api/v1/stores/{store_id}", tags=["Stores"])
async def get_store(store_id: str):
    """Get a specific store."""
    from .services.data_store import data_store
    store = data_store.get_store(store_id)
    if not store:
        return JSONResponse(status_code=404, content={"error": "Store not found"})
    return store


@app.get("/api/v1/distributors", tags=["Distributors"])
async def get_distributors():
    """Get all distributors."""
    from .services.data_store import data_store
    return {"distributors": data_store.distributors, "total": len(data_store.distributors)}


# ── Lambda Handler (for AWS Lambda deployment via Mangum) ──
try:
    from mangum import Mangum
    handler = Mangum(app)
except ImportError:
    handler = None
