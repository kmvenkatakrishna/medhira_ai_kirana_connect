"""Orders router — order management endpoints."""

from fastapi import APIRouter
from typing import Optional
from ..services.data_store import data_store
from datetime import datetime
import uuid

router = APIRouter(prefix="/api/v1/stores/{store_id}/orders", tags=["Orders"])


@router.get("")
async def get_orders(store_id: str, status: Optional[str] = None):
    """Get all orders for a store."""
    orders = data_store.get_orders(store_id, status=status)
    return {"store_id": store_id, "orders": orders, "total": len(orders)}


@router.get("/{order_id}")
async def get_order(store_id: str, order_id: str):
    """Get a specific order."""
    order = data_store.get_order(store_id, order_id)
    if not order:
        return {"error": "Order not found"}
    return order


@router.get("/{order_id}/status")
async def get_order_status(store_id: str, order_id: str):
    """Get order status."""
    order = data_store.get_order(store_id, order_id)
    if not order:
        return {"error": "Order not found"}
    return {
        "order_id": order_id,
        "status": order["status"],
        "placed_at": order["placed_at"],
        "expected_delivery": order["expected_delivery"],
        "delivered_at": order.get("delivered_at")
    }


@router.post("/generate")
async def generate_order(store_id: str):
    """Auto-generate order based on low stock and predictions."""
    low_stock = data_store.get_low_stock(store_id)
    distributors = data_store.get_distributors()

    if not low_stock:
        return {"message": "No items need reordering", "order": None}

    # Pick best distributor
    dist = distributors[0] if distributors else None
    items = []
    total = 0

    for inv_item in low_stock[:10]:
        order_qty = inv_item["optimal_quantity"] - inv_item["current_quantity"]
        price = inv_item["unit_price"] * 0.85
        item_total = round(order_qty * price, 2)
        total += item_total
        items.append({
            "product_id": inv_item["product_id"],
            "product_name": inv_item["product_name"],
            "quantity": order_qty,
            "unit_price": round(price, 2),
            "total_price": item_total
        })

    order = {
        "order_id": f"ORD-{uuid.uuid4().hex[:8]}",
        "store_id": store_id,
        "distributor_id": dist["distributor_id"] if dist else "",
        "distributor_name": dist["name"] if dist else "",
        "status": "pending",
        "placed_at": datetime.now().isoformat(),
        "expected_delivery": "",
        "delivered_at": None,
        "total_amount": round(total, 2),
        "items": items
    }

    data_store.add_order(store_id, order)
    return {"message": "Order generated", "order": order}


@router.post("/{order_id}/place")
async def place_order(store_id: str, order_id: str):
    """Confirm and place an order."""
    order = data_store.update_order_status(store_id, order_id, "confirmed")
    if not order:
        return {"error": "Order not found"}
    return {"message": "Order placed successfully", "order": order}


@router.put("/{order_id}/confirm")
async def confirm_delivery(store_id: str, order_id: str):
    """Mark order as delivered."""
    order = data_store.update_order_status(store_id, order_id, "delivered")
    if not order:
        return {"error": "Order not found"}
    return {"message": "Order delivered", "order": order}
