from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from pydantic import BaseModel
from services.db import InventoryService

router = APIRouter()

class InventoryItem(BaseModel):
    name: str
    category: str
    quantity: int
    unit_price: float
    min_threshold: int = 10
    unit: str = "pcs"

@router.get("/")
def get_inventory(store_id: str):
    items = InventoryService.get_inventory(store_id)
    return {"store_id": store_id, "inventory": items}

@router.get("/{product_id}")
def get_inventory_item(store_id: str, product_id: str):
    item = InventoryService.get_item(store_id, product_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.post("/")
def add_inventory_item(store_id: str, item: InventoryItem):
    item_dict = item.model_dump()
    saved_item = InventoryService.add_or_update_item(store_id, item_dict)
    return {"message": "Item added successfully", "item": saved_item}

@router.put("/{product_id}")
def update_inventory_item(store_id: str, product_id: str, item: InventoryItem):
    existing = InventoryService.get_item(store_id, product_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Item not found")
    
    item_dict = item.model_dump()
    item_dict['product_id'] = product_id
    saved_item = InventoryService.add_or_update_item(store_id, item_dict)
    return {"message": "Item updated successfully", "item": saved_item}

@router.delete("/{product_id}")
def delete_inventory_item(store_id: str, product_id: str):
    success = InventoryService.delete_item(store_id, product_id)
    if success:
        return {"message": "Item deleted successfully"}
    raise HTTPException(status_code=500, detail="Failed to delete item")
