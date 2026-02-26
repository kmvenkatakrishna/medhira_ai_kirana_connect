"""Predictions router - simulated AI demand forecasting."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from datetime import datetime, timedelta
import random
import json

from database import get_db
from models import Prediction, Product, InventoryItem, Transaction, TransactionItem

router = APIRouter(prefix="/api/v1/stores/{store_id}/predictions", tags=["Predictions"])


@router.get("")
def get_predictions(store_id: int, db: Session = Depends(get_db)):
    """Get all active predictions for the store."""
    today = datetime.utcnow()
    preds = (
        db.query(Prediction)
        .options(joinedload(Prediction.product))
        .filter(
            Prediction.store_id == store_id,
            Prediction.forecast_date >= today,
        )
        .order_by(Prediction.forecast_date)
        .all()
    )

    return [
        {
            "id": p.id,
            "product_id": p.product.id,
            "product_name": p.product.name,
            "category": p.product.category,
            "forecast_date": p.forecast_date.strftime("%Y-%m-%d"),
            "predicted_quantity": p.predicted_quantity,
            "confidence": p.confidence,
            "factors": json.loads(p.factors) if p.factors else {},
        }
        for p in preds
    ]


@router.post("/generate")
def generate_predictions(store_id: int, db: Session = Depends(get_db)):
    """Generate new AI predictions (simulated for prototype)."""
    # Delete old predictions
    db.query(Prediction).filter(Prediction.store_id == store_id).delete()

    # Get inventory items
    inv_items = (
        db.query(InventoryItem)
        .options(joinedload(InventoryItem.product))
        .filter(InventoryItem.store_id == store_id)
        .all()
    )

    # Get historical sales (last 30 days)
    start_date = datetime.utcnow() - timedelta(days=30)
    for inv in inv_items:
        total_sold = db.query(func.sum(TransactionItem.quantity)).join(
            Transaction
        ).filter(
            Transaction.store_id == store_id,
            Transaction.transaction_type == "sale",
            Transaction.transaction_date >= start_date,
            TransactionItem.product_id == inv.product_id,
        ).scalar() or 0

        avg_daily = total_sold / 30

        # Generate 7-day forecast with simulated AI
        for day in range(1, 8):
            forecast_date = datetime.utcnow() + timedelta(days=day)

            # Simulate ML prediction with factors
            seasonal = random.uniform(-0.15, 0.25)
            trend = random.uniform(-0.05, 0.15)
            weather = random.uniform(-0.1, 0.1)
            festival = random.uniform(0, 0.35) if day > 4 else random.uniform(0, 0.1)
            day_of_week = (forecast_date.weekday() + 1) % 7
            weekend_boost = 0.15 if day_of_week >= 5 else 0

            factor_total = 1 + seasonal + trend + weather + festival + weekend_boost
            predicted = max(1, avg_daily * factor_total * random.uniform(0.85, 1.15))

            pred = Prediction(
                store_id=store_id,
                product_id=inv.product_id,
                forecast_date=forecast_date,
                predicted_quantity=round(predicted, 1),
                confidence=round(random.uniform(0.7, 0.95), 2),
                factors=json.dumps({
                    "seasonal": round(seasonal, 3),
                    "trend": round(trend, 3),
                    "weather_impact": round(weather, 3),
                    "festival_effect": round(festival, 3),
                    "weekend_boost": round(weekend_boost, 3),
                    "avg_daily_sales": round(avg_daily, 2),
                }),
            )
            db.add(pred)

    db.commit()
    return {"message": "Predictions generated for all products", "days": 7}


@router.get("/summary")
def prediction_summary(store_id: int, db: Session = Depends(get_db)):
    """Get a high-level prediction summary."""
    today = datetime.utcnow()
    week_ahead = today + timedelta(days=7)

    preds = (
        db.query(Prediction)
        .options(joinedload(Prediction.product))
        .filter(
            Prediction.store_id == store_id,
            Prediction.forecast_date >= today,
            Prediction.forecast_date <= week_ahead,
        )
        .all()
    )

    # Get current inventory for comparison
    inv_map = {}
    invs = db.query(InventoryItem).filter(InventoryItem.store_id == store_id).all()
    for inv in invs:
        inv_map[inv.product_id] = inv.current_quantity

    # Aggregate predictions by product
    product_demand = {}
    for p in preds:
        if p.product_id not in product_demand:
            product_demand[p.product_id] = {
                "product_name": p.product.name,
                "category": p.product.category,
                "total_predicted": 0,
                "avg_confidence": 0,
                "count": 0,
                "current_stock": inv_map.get(p.product_id, 0),
            }
        product_demand[p.product_id]["total_predicted"] += p.predicted_quantity
        product_demand[p.product_id]["avg_confidence"] += p.confidence
        product_demand[p.product_id]["count"] += 1

    # Calculate averages and identify risks
    high_risk = []
    for pid, data in product_demand.items():
        data["avg_confidence"] = round(data["avg_confidence"] / max(data["count"], 1), 2)
        data["total_predicted"] = round(data["total_predicted"], 1)
        data["surplus_deficit"] = round(data["current_stock"] - data["total_predicted"], 1)

        if data["surplus_deficit"] < 0:
            high_risk.append(data)

    high_risk.sort(key=lambda x: x["surplus_deficit"])

    return {
        "total_products_analyzed": len(product_demand),
        "at_risk_products": len(high_risk),
        "high_risk_items": high_risk[:10],
    }
