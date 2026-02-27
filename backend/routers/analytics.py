from fastapi import APIRouter
from services.db import InventoryService
from typing import List, Dict, Any
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/dashboard")
def get_dashboard_summary(store_id: str):
    inventory = InventoryService.get_inventory(store_id)
    
    total_items = len(inventory)
    low_stock_items = [i for i in inventory if i.get('quantity', 0) <= i.get('min_threshold', 10)]
    out_of_stock_items = [i for i in inventory if i.get('quantity', 0) == 0]
    
    # Calculate total value
    total_value = sum((i.get('quantity', 0) * i.get('unit_price', 0)) for i in inventory)
    
    return {
        "store_id": store_id,
        "metrics": {
            "total_products": total_items,
            "low_stock_count": len(low_stock_items),
            "out_of_stock_count": len(out_of_stock_items),
            "total_inventory_value": total_value
        },
        "low_stock_alerts": low_stock_items
    }

@router.get("/predictions")
def get_sales_predictions(store_id: str):
    """
    Mock endpoint for predicting next week's sales/demand.
    In a real system, this would call an ML model (like Prophet)
    hosted on SageMaker or a dedicated prediction container.
    """
    inventory = InventoryService.get_inventory(store_id)
    
    predictions = []
    
    # Generate mock predictions for top 5 items
    for item in inventory[:5]: 
        # Simulated prediction: current stock will run out in X days, suggested order qty
        daily_sales_rate = item.get('quantity', 10) * 0.1 # Mock rate: 10% of stock sold daily
        if daily_sales_rate == 0:
            daily_sales_rate = 1
            
        days_to_stock_out = int(item.get('quantity', 0) / daily_sales_rate)
        
        predictions.append({
            "product_id": item.get('product_id'),
            "name": item.get('name'),
            "current_stock": item.get('quantity'),
            "predicted_daily_demand": round(daily_sales_rate, 2),
            "estimated_stockout_days": days_to_stock_out,
            "suggested_order_qty": int(daily_sales_rate * 7) # Order for next 7 days
        })
        
    return {
        "store_id": store_id,
        "forecast_period_days": 7,
        "predictions": predictions
    }
