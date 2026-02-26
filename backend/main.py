"""Kirana-Connect Backend API - Main Entry Point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import engine, SessionLocal, Base
from models import *  # noqa: ensure all models are imported for table creation
from seed_data import seed_database
from routers import inventory, products, analytics, predictions, orders, stores

# Create tables
Base.metadata.create_all(bind=engine)

# Seed data
db = SessionLocal()
try:
    seed_database(db)
finally:
    db.close()

app = FastAPI(
    title="Kirana-Connect API",
    description="AI-powered inventory management for Kirana stores",
    version="1.0.0",
)

# CORS - allow frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(stores.router)
app.include_router(inventory.router)
app.include_router(products.router)
app.include_router(analytics.router)
app.include_router(predictions.router)
app.include_router(orders.router)


@app.get("/")
def root():
    return {
        "name": "Kirana-Connect API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}
