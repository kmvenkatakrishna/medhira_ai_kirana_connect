"""Analytics service — computes reports and insights from transaction data."""

from datetime import datetime, timedelta
from collections import defaultdict
from .data_store import data_store


def get_daily_report(store_id: str, date_str: str = None):
    """Get sales summary for a specific day."""
    if not date_str:
        date_str = datetime.now().strftime("%Y-%m-%d")

    txns = data_store.get_transactions(store_id, txn_type="sale")
    day_txns = [t for t in txns if t["transaction_date"][:10] == date_str]

    total_sales = sum(t["total_amount"] for t in day_txns)
    product_sales = defaultdict(lambda: {"qty": 0, "revenue": 0, "name": ""})

    for t in day_txns:
        for item in t["items"]:
            pid = item["product_id"]
            product_sales[pid]["qty"] += item["quantity"]
            product_sales[pid]["revenue"] += item["total_price"]
            product_sales[pid]["name"] = item["product_name"]

    top_products = sorted(product_sales.values(), key=lambda x: x["revenue"], reverse=True)[:10]
    low_stock = data_store.get_low_stock(store_id)

    return {
        "date": date_str,
        "total_sales": round(total_sales, 2),
        "total_transactions": len(day_txns),
        "top_products": [{"name": p["name"], "quantity": p["qty"], "revenue": round(p["revenue"], 2)} for p in top_products],
        "low_stock_items": [{"name": i["product_name"], "current": i["current_quantity"], "reorder": i["reorder_point"]} for i in low_stock[:5]]
    }


def get_weekly_report(store_id: str):
    """Get sales summary for the last 7 days."""
    txns = data_store.get_transactions(store_id, txn_type="sale", days=7)

    total_sales = sum(t["total_amount"] for t in txns)
    daily_breakdown = defaultdict(lambda: {"sales": 0, "count": 0})

    for t in txns:
        day = t["transaction_date"][:10]
        daily_breakdown[day]["sales"] += t["total_amount"]
        daily_breakdown[day]["count"] += 1

    # Category breakdown
    cat_sales = defaultdict(float)
    for t in txns:
        for item in t["items"]:
            product = data_store.get_product(item["product_id"])
            if product:
                cat_sales[product["category"]] += item["total_price"]

    return {
        "period": "Last 7 Days",
        "total_sales": round(total_sales, 2),
        "total_transactions": len(txns),
        "avg_daily_sales": round(total_sales / 7, 2),
        "daily_breakdown": [{"date": k, "sales": round(v["sales"], 2), "transactions": v["count"]} for k, v in sorted(daily_breakdown.items())],
        "category_breakdown": [{"category": k, "sales": round(v, 2)} for k, v in sorted(cat_sales.items(), key=lambda x: x[1], reverse=True)]
    }


def get_monthly_report(store_id: str):
    """Get sales summary for the last 30 days."""
    txns = data_store.get_transactions(store_id, txn_type="sale", days=30)

    total_sales = sum(t["total_amount"] for t in txns)
    weekly = defaultdict(lambda: {"sales": 0, "count": 0})

    for t in txns:
        dt = datetime.fromisoformat(t["transaction_date"])
        week_key = f"Week {(dt.day - 1) // 7 + 1}"
        weekly[week_key]["sales"] += t["total_amount"]
        weekly[week_key]["count"] += 1

    # Product performance
    product_perf = defaultdict(lambda: {"qty": 0, "revenue": 0, "name": ""})
    for t in txns:
        for item in t["items"]:
            pid = item["product_id"]
            product_perf[pid]["qty"] += item["quantity"]
            product_perf[pid]["revenue"] += item["total_price"]
            product_perf[pid]["name"] = item["product_name"]

    top = sorted(product_perf.values(), key=lambda x: x["revenue"], reverse=True)[:10]
    slow = sorted(product_perf.values(), key=lambda x: x["qty"])[:5]

    return {
        "period": "Last 30 Days",
        "total_sales": round(total_sales, 2),
        "total_transactions": len(txns),
        "avg_daily_sales": round(total_sales / 30, 2),
        "weekly_breakdown": [{"week": k, "sales": round(v["sales"], 2), "transactions": v["count"]} for k, v in sorted(weekly.items())],
        "top_products": [{"name": p["name"], "quantity": p["qty"], "revenue": round(p["revenue"], 2)} for p in top],
        "slow_moving": [{"name": p["name"], "quantity": p["qty"], "revenue": round(p["revenue"], 2)} for p in slow]
    }


def get_sales_trends(store_id: str, days: int = 30):
    """Get daily sales trend data for charting."""
    txns = data_store.get_transactions(store_id, txn_type="sale", days=days)
    daily = defaultdict(float)

    for t in txns:
        day = t["transaction_date"][:10]
        daily[day] += t["total_amount"]

    now = datetime.now()
    result = []
    for d in range(days, 0, -1):
        date = (now - timedelta(days=d)).strftime("%Y-%m-%d")
        result.append({"date": date, "sales": round(daily.get(date, 0), 2)})

    return result


def get_top_products(store_id: str, days: int = 30, limit: int = 10):
    """Get top selling products."""
    txns = data_store.get_transactions(store_id, txn_type="sale", days=days)
    product_sales = defaultdict(lambda: {"qty": 0, "revenue": 0, "name": "", "category": ""})

    for t in txns:
        for item in t["items"]:
            pid = item["product_id"]
            product_sales[pid]["qty"] += item["quantity"]
            product_sales[pid]["revenue"] += item["total_price"]
            product_sales[pid]["name"] = item["product_name"]
            product = data_store.get_product(pid)
            if product:
                product_sales[pid]["category"] = product["category"]

    top = sorted(product_sales.values(), key=lambda x: x["revenue"], reverse=True)[:limit]
    return [{"name": p["name"], "category": p["category"], "quantity": p["qty"], "revenue": round(p["revenue"], 2)} for p in top]


def get_analytics_summary(store_id: str):
    """Get full analytics summary for dashboard."""
    inventory = data_store.get_inventory(store_id)
    txns_30d = data_store.get_transactions(store_id, txn_type="sale", days=30)
    low_stock = data_store.get_low_stock(store_id)

    total_revenue = sum(t["total_amount"] for t in txns_30d)
    inventory_value = sum(i["current_quantity"] * i["unit_price"] for i in inventory)

    # Category breakdown
    cat_sales = defaultdict(float)
    for t in txns_30d:
        for item in t["items"]:
            product = data_store.get_product(item["product_id"])
            if product:
                cat_sales[product["category"]] += item["total_price"]

    top_cats = sorted(cat_sales.items(), key=lambda x: x[1], reverse=True)

    # Overstock
    overstock = [i for i in inventory if i["current_quantity"] > i["optimal_quantity"] * 1.5]

    return {
        "total_revenue": round(total_revenue, 2),
        "total_transactions": len(txns_30d),
        "avg_daily_sales": round(total_revenue / 30, 2),
        "top_categories": [{"category": c, "sales": round(s, 2)} for c, s in top_cats[:6]],
        "sales_trend": get_sales_trends(store_id, 30),
        "inventory_value": round(inventory_value, 2),
        "low_stock_count": len(low_stock),
        "overstock_count": len(overstock),
        "total_products": len(inventory),
        "top_products": get_top_products(store_id, 30, 5)
    }
