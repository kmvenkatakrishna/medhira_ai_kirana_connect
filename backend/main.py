"""
KiranaConnect AI — FastAPI Backend Application

An AI-powered inventory management system for Kirana stores.
Provides REST APIs for inventory, predictions, orders, analytics, and chat.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
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

# ── Frontend Path ──
frontend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")

# ── Include Routers (API routes BEFORE static files) ──
app.include_router(inventory.router)
app.include_router(predictions.router)
app.include_router(orders.router)
app.include_router(analytics.router)
app.include_router(chat.router)
app.include_router(products.router)
app.include_router(ai.router)


# ── Health Check ──
@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "app": APP_NAME, "version": APP_VERSION}


# ── API Info ──
@app.get("/api/v1/info", tags=["Health"])
async def api_info():
    return {
        "app": APP_NAME,
        "version": APP_VERSION,
        "status": "running",
        "endpoints": {
            "inventory": "/api/v1/stores/{store_id}/inventory",
            "predictions": "/api/v1/stores/{store_id}/predictions",
            "orders": "/api/v1/stores/{store_id}/orders",
            "analytics": "/api/v1/stores/{store_id}/analytics/summary",
            "chat": "/api/v1/chat",
            "products": "/api/v1/products",
            "ai_insights": "/api/v1/stores/{store_id}/ai/insights"
        }
    }


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


# ── Serve Frontend Pages ──
# Serve specific HTML pages at clean URLs
@app.get("/", response_class=HTMLResponse, tags=["Frontend"])
async def serve_index():
    index = os.path.join(frontend_path, "index.html")
    if os.path.exists(index):
        return FileResponse(index, media_type="text/html")
    return JSONResponse({"app": APP_NAME, "version": APP_VERSION, "status": "running"})


@app.get("/dashboard", response_class=HTMLResponse, tags=["Frontend"])
@app.get("/dashboard.html", response_class=HTMLResponse, include_in_schema=False)
async def serve_dashboard():
    return FileResponse(os.path.join(frontend_path, "dashboard.html"), media_type="text/html")


@app.get("/chat", response_class=HTMLResponse, tags=["Frontend"])
@app.get("/chat.html", response_class=HTMLResponse, include_in_schema=False)
async def serve_chat():
    return FileResponse(os.path.join(frontend_path, "chat.html"), media_type="text/html")


@app.get("/analytics", response_class=HTMLResponse, tags=["Frontend"])
@app.get("/analytics.html", response_class=HTMLResponse, include_in_schema=False)
async def serve_analytics():
    return FileResponse(os.path.join(frontend_path, "analytics.html"), media_type="text/html")


@app.get("/orders", response_class=HTMLResponse, tags=["Frontend"])
@app.get("/orders.html", response_class=HTMLResponse, include_in_schema=False)
async def serve_orders():
    return FileResponse(os.path.join(frontend_path, "orders.html"), media_type="text/html")


@app.get("/presentation", response_class=HTMLResponse, tags=["Frontend"])
@app.get("/presentation.html", response_class=HTMLResponse, include_in_schema=False)
async def serve_presentation():
    pres = os.path.join(os.path.dirname(frontend_path), "presentation.html")
    if os.path.exists(pres):
        return FileResponse(pres, media_type="text/html")
    return JSONResponse(status_code=404, content={"error": "Presentation not found"})


# ── Mount CSS/JS static files ──
if os.path.exists(frontend_path):
    app.mount("/css", StaticFiles(directory=os.path.join(frontend_path, "css")), name="css")
    app.mount("/js", StaticFiles(directory=os.path.join(frontend_path, "js")), name="js")


# ── Lambda Handler (for AWS Lambda deployment via Mangum) ──
try:
    from mangum import Mangum
    handler = Mangum(app)
except ImportError:
    handler = None

