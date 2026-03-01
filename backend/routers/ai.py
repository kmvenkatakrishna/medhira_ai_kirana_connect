"""AI Insights & Predictions API Router."""

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1", tags=["AI Intelligence"])


@router.get("/stores/{store_id}/ai/insights")
async def get_ai_insights(store_id: str):
    """Get comprehensive AI-driven insights for a store."""
    from ..services import ai_insights_engine
    return ai_insights_engine.get_all_insights(store_id)


@router.get("/stores/{store_id}/ai/anomalies")
async def get_anomalies(store_id: str, days: int = 30):
    """Get detected sales anomalies."""
    from ..services import ai_insights_engine
    anomalies = ai_insights_engine.detect_sales_anomalies(store_id, days)
    return {"store_id": store_id, "anomalies": anomalies, "total": len(anomalies)}


@router.get("/stores/{store_id}/ai/recommendations")
async def get_recommendations(store_id: str):
    """Get AI profit optimization recommendations."""
    from ..services import ai_insights_engine
    return ai_insights_engine.analyze_profit_optimization(store_id)


@router.get("/stores/{store_id}/ai/smart-reorder")
async def get_smart_reorder(store_id: str):
    """Get AI-calculated optimal reorder quantities."""
    from ..services import ai_insights_engine
    items = ai_insights_engine.calculate_smart_reorder(store_id)
    total_cost = sum(i["estimated_cost"] for i in items)
    return {
        "store_id": store_id,
        "reorder_items": items,
        "total_items": len(items),
        "total_estimated_cost": round(total_cost, 2)
    }


@router.get("/stores/{store_id}/ai/expiry-risk")
async def get_expiry_risk(store_id: str):
    """Get expiry risk analysis for perishable goods."""
    from ..services import ai_insights_engine
    risks = ai_insights_engine.analyze_expiry_risk(store_id)
    total_waste = sum(r["waste_value"] for r in risks)
    return {
        "store_id": store_id,
        "at_risk_items": risks,
        "total_items": len(risks),
        "total_potential_waste": round(total_waste, 2)
    }


@router.get("/stores/{store_id}/ai/cross-sell")
async def get_cross_sell(store_id: str):
    """Get cross-sell product recommendations."""
    from ..services import ai_insights_engine
    pairs = ai_insights_engine.analyze_cross_sell(store_id)
    return {"store_id": store_id, "recommendations": pairs}


@router.get("/stores/{store_id}/ai/forecast")
async def get_ai_forecast(store_id: str, top_n: int = 15):
    """Get AI-generated demand forecasts for top products."""
    from ..services import prediction_engine
    forecasts = prediction_engine.generate_all_forecasts(store_id, top_n=top_n)
    accuracy = prediction_engine.get_prediction_accuracy_metrics(store_id)
    return {
        "store_id": store_id,
        "forecasts": forecasts,
        "total": len(forecasts),
        "accuracy_metrics": accuracy
    }


@router.get("/stores/{store_id}/ai/forecast/{product_id}")
async def get_product_forecast(store_id: str, product_id: str):
    """Get detailed AI forecast for a specific product."""
    from ..services import prediction_engine
    forecast = prediction_engine.generate_product_forecast(store_id, product_id)
    if not forecast:
        return {"error": "Product not found or no data available"}
    return forecast


@router.get("/stores/{store_id}/ai/accuracy")
async def get_prediction_accuracy(store_id: str):
    """Get prediction model accuracy metrics."""
    from ..services import prediction_engine
    return prediction_engine.get_prediction_accuracy_metrics(store_id)
