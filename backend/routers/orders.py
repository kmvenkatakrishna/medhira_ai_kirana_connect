"""Orders management router."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

from database import get_db
from models import Order, OrderItem, Product, InventoryItem, Distributor

router = APIRouter(prefix="/api/v1/stores/{store_id}/orders", tags=["Orders"])


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: float
    unit_price: float


class OrderCreate(BaseModel):
    distributor_id: int
    items: List[OrderItemCreate]


@router.get("")
def get_orders(store_id: int, status: Optional[str] = None, db: Session = Depends(get_db)):
    query = (
        db.query(Order)
        .options(
            joinedload(Order.distributor),
            joinedload(Order.items).joinedload(OrderItem.product),
        )
        .filter(Order.store_id == store_id)
    )
    if status:
        query = query.filter(Order.status == status)

    orders = query.order_by(Order.created_at.desc()).all()

    return [
        {
            "id": o.id,
            "distributor_name": o.distributor.name if o.distributor else "Unknown",
            "distributor_phone": o.distributor.phone if o.distributor else "",
            "status": o.status,
            "placed_at": o.placed_at.isoformat() if o.placed_at else None,
            "delivered_at": o.delivered_at.isoformat() if o.delivered_at else None,
            "total_amount": o.total_amount,
            "created_at": o.created_at.isoformat() if o.created_at else None,
            "items": [
                {
                    "product_name": item.product.name if item.product else "Unknown",
                    "category": item.product.category if item.product else "",
                    "quantity": item.quantity,
                    "unit_price": item.unit_price,
                    "total": round(item.quantity * item.unit_price, 2),
                }
                for item in o.items
            ],
        }
        for o in orders
    ]


@router.post("/generate")
def generate_order_suggestions(store_id: int, db: Session = Depends(get_db)):
    """Generate smart order suggestions based on stock levels and predictions."""
    items = (
        db.query(InventoryItem)
        .options(joinedload(InventoryItem.product))
        .filter(
            InventoryItem.store_id == store_id,
            InventoryItem.current_quantity <= InventoryItem.reorder_point,
        )
        .all()
    )

    if not items:
        return {"message": "All stock levels are healthy", "suggestions": []}

    suggestions = []
    for item in items:
        order_qty = item.optimal_quantity - item.current_quantity
        suggestions.append({
            "product_id": item.product.id,
            "product_name": item.product.name,
            "category": item.product.category,
            "current_stock": item.current_quantity,
            "reorder_point": item.reorder_point,
            "suggested_quantity": round(order_qty, 1),
            "estimated_cost": round(order_qty * item.product.typical_price, 2),
            "priority": "high" if item.current_quantity <= item.reorder_point * 0.5 else "medium",
        })

    suggestions.sort(key=lambda x: 0 if x["priority"] == "high" else 1)

    return {
        "total_items": len(suggestions),
        "total_estimated_cost": round(sum(s["estimated_cost"] for s in suggestions), 2),
        "suggestions": suggestions,
    }


@router.post("")
def create_order(store_id: int, order_data: OrderCreate, db: Session = Depends(get_db)):
    order = Order(
        store_id=store_id,
        distributor_id=order_data.distributor_id,
        status="placed",
        placed_at=datetime.utcnow(),
        total_amount=0,
    )
    db.add(order)
    db.flush()

    total = 0
    for item in order_data.items:
        oi = OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            unit_price=item.unit_price,
        )
        total += item.quantity * item.unit_price
        db.add(oi)

    order.total_amount = round(total, 2)
    db.commit()

    return {"message": "Order placed", "order_id": order.id, "total_amount": order.total_amount}


@router.put("/{order_id}/status")
def update_order_status(store_id: int, order_id: int, status: str, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id, Order.store_id == store_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order.status = status
    if status == "delivered":
        order.delivered_at = datetime.utcnow()
    db.commit()

    return {"message": f"Order status updated to {status}"}


@router.get("/distributors")
def get_distributors(store_id: int, db: Session = Depends(get_db)):
    return db.query(Distributor).order_by(Distributor.rating.desc()).all()
