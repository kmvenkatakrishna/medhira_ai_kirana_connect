"""Analytics and reporting router."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, case
from datetime import datetime, timedelta
from typing import Optional

from database import get_db
from models import Transaction, TransactionItem, Product, InventoryItem

router = APIRouter(prefix="/api/v1/stores/{store_id}", tags=["Analytics"])


@router.get("/analytics/dashboard")
def get_dashboard(store_id: int, db: Session = Depends(get_db)):
    """Main dashboard data - today's summary, trends, alerts."""
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday = today - timedelta(days=1)
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)

    # Today's sales
    today_sales = db.query(func.sum(Transaction.total_amount)).filter(
        Transaction.store_id == store_id,
        Transaction.transaction_type == "sale",
        Transaction.transaction_date >= yesterday,
    ).scalar() or 0

    # Yesterday's sales
    day_before = yesterday - timedelta(days=1)
    yesterday_sales = db.query(func.sum(Transaction.total_amount)).filter(
        Transaction.store_id == store_id,
        Transaction.transaction_type == "sale",
        Transaction.transaction_date >= day_before,
        Transaction.transaction_date < yesterday,
    ).scalar() or 0

    # This week's sales
    week_sales = db.query(func.sum(Transaction.total_amount)).filter(
        Transaction.store_id == store_id,
        Transaction.transaction_type == "sale",
        Transaction.transaction_date >= week_ago,
    ).scalar() or 0

    # This month's sales
    month_sales = db.query(func.sum(Transaction.total_amount)).filter(
        Transaction.store_id == store_id,
        Transaction.transaction_type == "sale",
        Transaction.transaction_date >= month_ago,
    ).scalar() or 0

    # Transaction count today
    today_tx_count = db.query(func.count(Transaction.id)).filter(
        Transaction.store_id == store_id,
        Transaction.transaction_type == "sale",
        Transaction.transaction_date >= yesterday,
    ).scalar() or 0

    # Low stock count
    low_stock = db.query(func.count(InventoryItem.id)).filter(
        InventoryItem.store_id == store_id,
        InventoryItem.current_quantity <= InventoryItem.reorder_point,
    ).scalar() or 0

    # Total inventory value
    inv_items = (
        db.query(InventoryItem)
        .options(joinedload(InventoryItem.product))
        .filter(InventoryItem.store_id == store_id)
        .all()
    )
    total_inventory_value = sum(i.current_quantity * i.product.typical_price for i in inv_items)

    # Sales change percentage
    sales_change = 0
    if yesterday_sales > 0:
        sales_change = round(((today_sales - yesterday_sales) / yesterday_sales) * 100, 1)

    return {
        "today_sales": round(today_sales, 2),
        "yesterday_sales": round(yesterday_sales, 2),
        "week_sales": round(week_sales, 2),
        "month_sales": round(month_sales, 2),
        "sales_change_pct": sales_change,
        "today_transactions": today_tx_count,
        "low_stock_alerts": low_stock,
        "total_inventory_value": round(total_inventory_value, 2),
        "total_products": len(inv_items),
    }


@router.get("/analytics/sales-trends")
def get_sales_trends(
    store_id: int,
    days: int = Query(default=30, ge=7, le=90),
    db: Session = Depends(get_db),
):
    """Daily sales trend for the last N days."""
    start_date = datetime.utcnow() - timedelta(days=days)

    transactions = (
        db.query(Transaction)
        .filter(
            Transaction.store_id == store_id,
            Transaction.transaction_type == "sale",
            Transaction.transaction_date >= start_date,
        )
        .all()
    )

    # Group by date
    daily = {}
    for tx in transactions:
        day_key = tx.transaction_date.strftime("%Y-%m-%d")
        if day_key not in daily:
            daily[day_key] = {"date": day_key, "sales": 0, "transactions": 0}
        daily[day_key]["sales"] += tx.total_amount
        daily[day_key]["transactions"] += 1

    # Fill missing days
    result = []
    for i in range(days, -1, -1):
        d = (datetime.utcnow() - timedelta(days=i)).strftime("%Y-%m-%d")
        if d in daily:
            daily[d]["sales"] = round(daily[d]["sales"], 2)
            result.append(daily[d])
        else:
            result.append({"date": d, "sales": 0, "transactions": 0})

    return result


@router.get("/analytics/top-products")
def get_top_products(
    store_id: int,
    days: int = Query(default=30, ge=7, le=90),
    limit: int = Query(default=10, ge=5, le=50),
    db: Session = Depends(get_db),
):
    """Top selling products by quantity and revenue."""
    start_date = datetime.utcnow() - timedelta(days=days)

    results = (
        db.query(
            Product.name,
            Product.category,
            func.sum(TransactionItem.quantity).label("total_qty"),
            func.sum(TransactionItem.total_price).label("total_revenue"),
        )
        .join(TransactionItem, TransactionItem.product_id == Product.id)
        .join(Transaction, Transaction.id == TransactionItem.transaction_id)
        .filter(
            Transaction.store_id == store_id,
            Transaction.transaction_type == "sale",
            Transaction.transaction_date >= start_date,
        )
        .group_by(Product.id, Product.name, Product.category)
        .order_by(func.sum(TransactionItem.total_price).desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "product_name": r.name,
            "category": r.category,
            "total_quantity": round(r.total_qty, 1),
            "total_revenue": round(r.total_revenue, 2),
        }
        for r in results
    ]


@router.get("/analytics/category-breakdown")
def get_category_breakdown(
    store_id: int,
    days: int = Query(default=30, ge=7, le=90),
    db: Session = Depends(get_db),
):
    """Sales breakdown by category."""
    start_date = datetime.utcnow() - timedelta(days=days)

    results = (
        db.query(
            Product.category,
            func.sum(TransactionItem.total_price).label("revenue"),
            func.count(TransactionItem.id).label("items_sold"),
        )
        .join(TransactionItem, TransactionItem.product_id == Product.id)
        .join(Transaction, Transaction.id == TransactionItem.transaction_id)
        .filter(
            Transaction.store_id == store_id,
            Transaction.transaction_type == "sale",
            Transaction.transaction_date >= start_date,
        )
        .group_by(Product.category)
        .order_by(func.sum(TransactionItem.total_price).desc())
        .all()
    )

    total_revenue = sum(r.revenue for r in results) or 1

    return [
        {
            "category": r.category,
            "revenue": round(r.revenue, 2),
            "items_sold": r.items_sold,
            "percentage": round((r.revenue / total_revenue) * 100, 1),
        }
        for r in results
    ]


@router.get("/reports/daily")
def get_daily_report(store_id: int, db: Session = Depends(get_db)):
    """Daily summary report."""
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday = today - timedelta(days=1)

    # Sales for yesterday (since today is in progress)
    sales = (
        db.query(Transaction)
        .filter(
            Transaction.store_id == store_id,
            Transaction.transaction_type == "sale",
            Transaction.transaction_date >= yesterday,
            Transaction.transaction_date < today,
        )
        .all()
    )

    total_sales = sum(t.total_amount for t in sales)
    num_transactions = len(sales)

    # Purchases
    purchases = (
        db.query(Transaction)
        .filter(
            Transaction.store_id == store_id,
            Transaction.transaction_type == "purchase",
            Transaction.transaction_date >= yesterday,
            Transaction.transaction_date < today,
        )
        .all()
    )
    total_purchases = sum(t.total_amount for t in purchases)

    return {
        "date": yesterday.strftime("%Y-%m-%d"),
        "total_sales": round(total_sales, 2),
        "total_purchases": round(total_purchases, 2),
        "num_transactions": num_transactions,
        "profit_estimate": round(total_sales - total_purchases, 2),
        "margin_pct": round(((total_sales - total_purchases) / max(total_sales, 1)) * 100, 1),
    }
