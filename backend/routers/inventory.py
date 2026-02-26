"""Inventory management router."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

from database import get_db
from models import InventoryItem, Product, Transaction, TransactionItem

router = APIRouter(prefix="/api/v1/stores/{store_id}/inventory", tags=["Inventory"])


class PurchaseItem(BaseModel):
    product_id: int
    quantity: float
    unit_price: float


class PurchaseRequest(BaseModel):
    items: List[PurchaseItem]
    source: str = "manual"


class SaleItem(BaseModel):
    product_id: int
    quantity: float
    unit_price: float


class SaleRequest(BaseModel):
    items: List[SaleItem]
    source: str = "manual"


class InventoryUpdate(BaseModel):
    current_quantity: Optional[float] = None
    reorder_point: Optional[float] = None
    optimal_quantity: Optional[float] = None


@router.get("")
def get_inventory(
    store_id: int,
    category: Optional[str] = None,
    low_stock_only: bool = False,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = (
        db.query(InventoryItem)
        .options(joinedload(InventoryItem.product))
        .filter(InventoryItem.store_id == store_id)
    )

    if category:
        query = query.join(Product).filter(Product.category == category)

    if low_stock_only:
        query = query.filter(
            InventoryItem.current_quantity <= InventoryItem.reorder_point
        )

    if search:
        query = query.join(Product, isouter=True).filter(
            Product.name.ilike(f"%{search}%")
        )

    items = query.all()

    return [
        {
            "id": item.id,
            "product_id": item.product.id,
            "product_name": item.product.name,
            "category": item.product.category,
            "brand": item.product.brand,
            "unit": item.product.unit,
            "current_quantity": item.current_quantity,
            "reorder_point": item.reorder_point,
            "optimal_quantity": item.optimal_quantity,
            "typical_price": item.product.typical_price,
            "is_perishable": item.product.is_perishable,
            "shelf_life_days": item.product.shelf_life_days,
            "last_updated": item.last_updated.isoformat() if item.last_updated else None,
            "status": (
                "critical" if item.current_quantity <= item.reorder_point * 0.5
                else "low" if item.current_quantity <= item.reorder_point
                else "good" if item.current_quantity <= item.optimal_quantity
                else "overstock"
            ),
        }
        for item in items
    ]


@router.get("/low-stock")
def get_low_stock(store_id: int, db: Session = Depends(get_db)):
    items = (
        db.query(InventoryItem)
        .options(joinedload(InventoryItem.product))
        .filter(
            InventoryItem.store_id == store_id,
            InventoryItem.current_quantity <= InventoryItem.reorder_point,
        )
        .all()
    )

    return [
        {
            "id": item.id,
            "product_name": item.product.name,
            "category": item.product.category,
            "current_quantity": item.current_quantity,
            "reorder_point": item.reorder_point,
            "optimal_quantity": item.optimal_quantity,
            "unit": item.product.unit,
            "days_until_stockout": max(0, round(item.current_quantity / max(1, (item.optimal_quantity - item.current_quantity) / 7), 1)),
        }
        for item in items
    ]


@router.post("/purchase")
def record_purchase(store_id: int, request: PurchaseRequest, db: Session = Depends(get_db)):
    transaction = Transaction(
        store_id=store_id,
        transaction_type="purchase",
        transaction_date=datetime.utcnow(),
        total_amount=0,
        source=request.source,
    )
    db.add(transaction)
    db.flush()

    total = 0
    for item in request.items:
        ti = TransactionItem(
            transaction_id=transaction.id,
            product_id=item.product_id,
            quantity=item.quantity,
            unit_price=item.unit_price,
            total_price=round(item.quantity * item.unit_price, 2),
        )
        total += ti.total_price
        db.add(ti)

        # Update inventory
        inv = db.query(InventoryItem).filter(
            InventoryItem.store_id == store_id,
            InventoryItem.product_id == item.product_id,
        ).first()
        if inv:
            inv.current_quantity += item.quantity
            inv.last_updated = datetime.utcnow()
        else:
            inv = InventoryItem(
                store_id=store_id,
                product_id=item.product_id,
                current_quantity=item.quantity,
                reorder_point=10,
                optimal_quantity=50,
            )
            db.add(inv)

    transaction.total_amount = round(total, 2)
    db.commit()

    return {"message": "Purchase recorded", "transaction_id": transaction.id, "total_amount": transaction.total_amount}


@router.post("/sale")
def record_sale(store_id: int, request: SaleRequest, db: Session = Depends(get_db)):
    transaction = Transaction(
        store_id=store_id,
        transaction_type="sale",
        transaction_date=datetime.utcnow(),
        total_amount=0,
        source=request.source,
    )
    db.add(transaction)
    db.flush()

    total = 0
    for item in request.items:
        ti = TransactionItem(
            transaction_id=transaction.id,
            product_id=item.product_id,
            quantity=item.quantity,
            unit_price=item.unit_price,
            total_price=round(item.quantity * item.unit_price, 2),
        )
        total += ti.total_price
        db.add(ti)

        # Update inventory
        inv = db.query(InventoryItem).filter(
            InventoryItem.store_id == store_id,
            InventoryItem.product_id == item.product_id,
        ).first()
        if inv:
            inv.current_quantity = max(0, inv.current_quantity - item.quantity)
            inv.last_updated = datetime.utcnow()

    transaction.total_amount = round(total, 2)
    db.commit()

    return {"message": "Sale recorded", "transaction_id": transaction.id, "total_amount": transaction.total_amount}


@router.put("/{product_id}")
def update_inventory(store_id: int, product_id: int, update: InventoryUpdate, db: Session = Depends(get_db)):
    inv = db.query(InventoryItem).filter(
        InventoryItem.store_id == store_id,
        InventoryItem.product_id == product_id,
    ).first()

    if not inv:
        raise HTTPException(status_code=404, detail="Inventory item not found")

    if update.current_quantity is not None:
        inv.current_quantity = update.current_quantity
    if update.reorder_point is not None:
        inv.reorder_point = update.reorder_point
    if update.optimal_quantity is not None:
        inv.optimal_quantity = update.optimal_quantity

    inv.last_updated = datetime.utcnow()
    db.commit()

    return {"message": "Inventory updated"}


@router.get("/summary")
def get_inventory_summary(store_id: int, db: Session = Depends(get_db)):
    items = (
        db.query(InventoryItem)
        .options(joinedload(InventoryItem.product))
        .filter(InventoryItem.store_id == store_id)
        .all()
    )

    total_items = len(items)
    total_value = sum(i.current_quantity * i.product.typical_price for i in items)
    low_stock = sum(1 for i in items if i.current_quantity <= i.reorder_point)
    critical = sum(1 for i in items if i.current_quantity <= i.reorder_point * 0.5)
    overstock = sum(1 for i in items if i.current_quantity > i.optimal_quantity)

    # Category breakdown
    categories = {}
    for item in items:
        cat = item.product.category
        if cat not in categories:
            categories[cat] = {"count": 0, "value": 0}
        categories[cat]["count"] += 1
        categories[cat]["value"] += round(item.current_quantity * item.product.typical_price, 2)

    return {
        "total_items": total_items,
        "total_value": round(total_value, 2),
        "low_stock_count": low_stock,
        "critical_count": critical,
        "overstock_count": overstock,
        "healthy_count": total_items - low_stock - overstock,
        "categories": categories,
    }
