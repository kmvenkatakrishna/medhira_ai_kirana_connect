"""Inventory router — CRUD endpoints for inventory management."""

from fastapi import APIRouter, Query
from typing import Optional
from ..services.data_store import data_store

router = APIRouter(prefix="/api/v1/stores/{store_id}/inventory", tags=["Inventory"])


@router.get("")
async def get_inventory(store_id: str, category: Optional[str] = None):
    """Get all inventory items for a store."""
    items = data_store.get_inventory(store_id, category=category)
    return {"store_id": store_id, "items": items, "total": len(items)}


@router.get("/low-stock")
async def get_low_stock(store_id: str):
    """Get items below reorder point."""
    items = data_store.get_low_stock(store_id)
    return {"store_id": store_id, "low_stock_items": items, "total": len(items)}


@router.get("/{product_id}")
async def get_inventory_item(store_id: str, product_id: str):
    """Get a specific inventory item."""
    item = data_store.get_inventory_item(store_id, product_id)
    if not item:
        return {"error": "Item not found"}
    return item


@router.put("/{product_id}")
async def update_inventory_item(store_id: str, product_id: str, quantity: float):
    """Update inventory quantity."""
    item = data_store.update_inventory(store_id, product_id, quantity)
    if not item:
        return {"error": "Item not found"}
    return {"message": "Inventory updated", "item": item}


@router.post("/purchase")
async def record_purchase(store_id: str, body: dict):
    """Record a purchase transaction."""
    from datetime import datetime
    import uuid
    txn = {
        "transaction_id": f"TXN-{uuid.uuid4().hex[:8]}",
        "store_id": store_id,
        "transaction_type": "purchase",
        "transaction_date": datetime.now().isoformat(),
        "total_amount": sum(i.get("quantity", 0) * i.get("unit_price", 0) for i in body.get("items", [])),
        "source": "whatsapp",
        "items": body.get("items", [])
    }
    data_store.add_transaction(store_id, txn)
    return {"message": "Purchase recorded", "transaction": txn}


@router.post("/sale")
async def record_sale(store_id: str, body: dict):
    """Record a sale transaction."""
    from datetime import datetime
    import uuid
    txn = {
        "transaction_id": f"TXN-{uuid.uuid4().hex[:8]}",
        "store_id": store_id,
        "transaction_type": "sale",
        "transaction_date": datetime.now().isoformat(),
        "total_amount": sum(i.get("quantity", 0) * i.get("unit_price", 0) for i in body.get("items", [])),
        "source": "whatsapp",
        "items": body.get("items", [])
    }
    data_store.add_transaction(store_id, txn)
    return {"message": "Sale recorded", "transaction": txn}
