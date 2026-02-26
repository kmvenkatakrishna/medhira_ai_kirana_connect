"""Store management router."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from database import get_db
from models import Store

router = APIRouter(prefix="/api/v1/stores", tags=["Stores"])


class StoreCreate(BaseModel):
    owner_name: str
    phone_number: str
    store_name: str
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None


@router.get("")
def get_stores(db: Session = Depends(get_db)):
    return db.query(Store).all()


@router.get("/{store_id}")
def get_store(store_id: int, db: Session = Depends(get_db)):
    store = db.query(Store).filter(Store.id == store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    return store


@router.post("")
def create_store(store: StoreCreate, db: Session = Depends(get_db)):
    db_store = Store(**store.model_dump())
    db.add(db_store)
    db.commit()
    db.refresh(db_store)
    return db_store
