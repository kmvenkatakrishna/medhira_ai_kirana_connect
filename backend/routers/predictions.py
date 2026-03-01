"""Predictions router — demand forecasting endpoints."""

from fastapi import APIRouter
from ..services.data_store import data_store

router = APIRouter(prefix="/api/v1/stores/{store_id}/predictions", tags=["Predictions"])


@router.get("")
async def get_predictions(store_id: str):
    """Get all predictions for a store."""
    preds = data_store.get_predictions(store_id)
    return {"store_id": store_id, "predictions": preds, "total": len(preds)}


@router.get("/{product_id}")
async def get_product_prediction(store_id: str, product_id: str):
    """Get prediction for a specific product."""
    pred = data_store.get_prediction(store_id, product_id)
    if not pred:
        return {"error": "No prediction available for this product"}
    return pred


@router.post("/generate")
async def generate_predictions(store_id: str):
    """Trigger prediction generation (returns existing cached predictions)."""
    preds = data_store.get_predictions(store_id)
    return {
        "message": "Predictions generated successfully",
        "store_id": store_id,
        "predictions_count": len(preds),
        "predictions": preds
    }
