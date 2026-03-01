"""Analytics router — reports and insights endpoints."""

from fastapi import APIRouter
from typing import Optional
from ..services import analytics_service

router = APIRouter(prefix="/api/v1/stores/{store_id}", tags=["Analytics"])


@router.get("/reports/daily")
async def daily_report(store_id: str, date: Optional[str] = None):
    """Get daily sales report."""
    return analytics_service.get_daily_report(store_id, date)


@router.get("/reports/weekly")
async def weekly_report(store_id: str):
    """Get weekly sales report."""
    return analytics_service.get_weekly_report(store_id)


@router.get("/reports/monthly")
async def monthly_report(store_id: str):
    """Get monthly sales report."""
    return analytics_service.get_monthly_report(store_id)


@router.get("/analytics/sales-trends")
async def sales_trends(store_id: str, days: int = 30):
    """Get daily sales trend data for charts."""
    return {"trends": analytics_service.get_sales_trends(store_id, days)}


@router.get("/analytics/top-products")
async def top_products(store_id: str, days: int = 30, limit: int = 10):
    """Get top selling products."""
    return {"top_products": analytics_service.get_top_products(store_id, days, limit)}


@router.get("/analytics/summary")
async def analytics_summary(store_id: str):
    """Get full analytics summary for dashboard."""
    return analytics_service.get_analytics_summary(store_id)
