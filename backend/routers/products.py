"""Products catalog router."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import distinct
from typing import Optional

from database import get_db
from models import Product

router = APIRouter(prefix="/api/v1/products", tags=["Products"])


@router.get("")
def get_products(
    category: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Product)
    if category:
        query = query.filter(Product.category == category)
    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))
    return query.order_by(Product.category, Product.name).all()


@router.get("/categories")
def get_categories(db: Session = Depends(get_db)):
    cats = db.query(distinct(Product.category)).order_by(Product.category).all()
    return [c[0] for c in cats]


@router.get("/{product_id}")
def get_product(product_id: int, db: Session = Depends(get_db)):
    return db.query(Product).filter(Product.id == product_id).first()
