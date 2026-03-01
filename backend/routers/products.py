"""Products router — product catalog endpoints."""

from fastapi import APIRouter
from typing import Optional
from ..services.data_store import data_store

router = APIRouter(prefix="/api/v1/products", tags=["Products"])


@router.get("")
async def get_products(category: Optional[str] = None, search: Optional[str] = None):
    """Get all products, optionally filtered."""
    products = data_store.get_products(category=category, search=search)
    return {"products": products, "total": len(products)}


@router.get("/categories")
async def get_categories():
    """Get all product categories."""
    categories = data_store.get_categories()
    return {"categories": sorted(categories)}


@router.get("/{product_id}")
async def get_product(product_id: str):
    """Get a specific product."""
    product = data_store.get_product(product_id)
    if not product:
        return {"error": "Product not found"}
    return product
