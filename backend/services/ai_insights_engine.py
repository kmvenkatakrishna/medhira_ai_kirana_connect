"""
AI Insights Engine — Proactive business intelligence for Kirana stores.

Generates AI-driven recommendations by analyzing inventory, sales, and prediction data:
- Anomaly Detection (Z-score based unusual sales patterns)
- Profit Optimization (margin analysis, dead stock identification)
- Smart Reorder Calculations (prediction-driven safety stock)
- Expiry Risk Analysis (perishable goods at risk)
- Cross-sell Recommendations (co-occurrence patterns)
- Revenue Forecasting (next-week projection)
"""

import math
from datetime import datetime, timedelta
from collections import defaultdict
from typing import List, Dict, Optional

from .data_store import data_store
from . import prediction_engine


# ═══════════════════════════════════════════════════════════════════
#  ANOMALY DETECTION
# ═══════════════════════════════════════════════════════════════════

def detect_sales_anomalies(store_id: str, days: int = 30) -> List[Dict]:
    """
    Detect unusual sales patterns using Z-score analysis on daily revenue.
    Identifies both spikes (unusually high sales) and drops (unusually low).
    """
    txns = data_store.get_transactions(store_id, txn_type="sale", days=days)
    daily_sales = defaultdict(float)
    daily_txn_count = defaultdict(int)

    for t in txns:
        date_key = t["transaction_date"][:10]
        daily_sales[date_key] += t["total_amount"]
        daily_txn_count[date_key] += 1

    now = datetime.now()
    values = []
    dates = []
    for d in range(days, 0, -1):
        date_key = (now - timedelta(days=d)).strftime("%Y-%m-%d")
        values.append(daily_sales.get(date_key, 0))
        dates.append(date_key)

    if len(values) < 7:
        return []

    mean = sum(values) / len(values)
    variance = sum((x - mean) ** 2 for x in values) / len(values)
    std = math.sqrt(variance) if variance > 0 else 1

    anomalies = []
    for i, (val, date) in enumerate(zip(values, dates)):
        z = (val - mean) / std
        if abs(z) >= 1.8:
            anomaly_type = "spike" if z > 0 else "drop"
            pct_change = ((val - mean) / mean * 100) if mean > 0 else 0

            # Generate explanation
            if anomaly_type == "spike":
                explanation = f"Sales were {abs(pct_change):.0f}% above average (₹{val:,.0f} vs avg ₹{mean:,.0f})"
                suggestion = "Check if this was a festival/event. Consider stocking more for similar future events."
            else:
                explanation = f"Sales were {abs(pct_change):.0f}% below average (₹{val:,.0f} vs avg ₹{mean:,.0f})"
                suggestion = "Investigate cause — was the store closed? Supply issue? Competition?"

            festival = prediction_engine.get_festival_impact(date)

            anomalies.append({
                "date": date,
                "type": anomaly_type,
                "severity": "high" if abs(z) >= 2.5 else "medium",
                "sales_amount": round(val, 2),
                "average_amount": round(mean, 2),
                "z_score": round(z, 2),
                "percent_deviation": round(pct_change, 1),
                "explanation": explanation,
                "suggestion": suggestion,
                "festival_context": festival["festival"] if festival else None,
                "transactions": daily_txn_count.get(date, 0)
            })

    anomalies.sort(key=lambda a: abs(a["z_score"]), reverse=True)
    return anomalies[:10]


# ═══════════════════════════════════════════════════════════════════
#  PROFIT OPTIMIZATION
# ═══════════════════════════════════════════════════════════════════

def analyze_profit_optimization(store_id: str) -> Dict:
    """
    Analyze inventory for profit optimization opportunities.
    Identifies high-margin products, dead stock, overstocked items, and capital utilization.
    """
    inventory = data_store.get_inventory(store_id)
    txns = data_store.get_transactions(store_id, txn_type="sale", days=30)

    # Calculate sales velocity for each product
    product_sales = defaultdict(lambda: {"qty": 0, "revenue": 0})
    for t in txns:
        for item in t["items"]:
            product_sales[item["product_id"]]["qty"] += item["quantity"]
            product_sales[item["product_id"]]["revenue"] += item["total_price"]

    recommendations = []
    dead_stock = []
    overstock = []
    high_velocity = []
    total_locked_capital = 0

    for item in inventory:
        pid = item["product_id"]
        sales = product_sales.get(pid, {"qty": 0, "revenue": 0})
        stock_value = item["current_quantity"] * item["unit_price"]
        daily_velocity = sales["qty"] / 30 if sales["qty"] > 0 else 0
        days_of_stock = item["current_quantity"] / daily_velocity if daily_velocity > 0 else 999

        # Dead stock: no sales in 30 days and significant inventory
        if sales["qty"] == 0 and item["current_quantity"] > 5:
            dead_stock.append({
                "product_name": item["product_name"],
                "product_id": pid,
                "current_stock": item["current_quantity"],
                "stock_value": round(stock_value, 2),
                "recommendation": f"Consider discount/clearance sale to free ₹{stock_value:,.0f} locked capital"
            })
            total_locked_capital += stock_value

        # Overstock: more than 60 days of supply
        elif days_of_stock > 60 and item["current_quantity"] > item["optimal_quantity"]:
            excess = item["current_quantity"] - item["optimal_quantity"]
            excess_value = excess * item["unit_price"]
            overstock.append({
                "product_name": item["product_name"],
                "product_id": pid,
                "current_stock": item["current_quantity"],
                "optimal_stock": item["optimal_quantity"],
                "excess_units": excess,
                "excess_value": round(excess_value, 2),
                "days_of_supply": round(days_of_stock, 0),
                "recommendation": f"Reduce order quantity. {excess} excess units = ₹{excess_value:,.0f} locked"
            })
            total_locked_capital += excess_value

        # High velocity: selling fast
        elif daily_velocity > 3 and days_of_stock < 10:
            margin_pct = 15 + (5 if sales["revenue"] / max(sales["qty"], 1) > item["unit_price"] * 1.1 else 0)
            high_velocity.append({
                "product_name": item["product_name"],
                "product_id": pid,
                "daily_velocity": round(daily_velocity, 1),
                "days_left": round(days_of_stock, 0),
                "monthly_revenue": round(sales["revenue"], 2),
                "estimated_margin": f"{margin_pct}%",
                "recommendation": f"High performer! Ensure continuous supply — sells ~{daily_velocity:.0f}/day"
            })

    # Generate top recommendations
    if dead_stock:
        recommendations.append({
            "type": "dead_stock_alert",
            "priority": "high",
            "icon": "🚨",
            "title": f"{len(dead_stock)} Dead Stock Items Detected",
            "description": f"₹{total_locked_capital:,.0f} capital locked in non-moving inventory. Consider clearance sales.",
            "action": "Review dead stock items and consider discount pricing",
            "impact": f"Could free up ₹{total_locked_capital:,.0f} in working capital"
        })

    if overstock:
        recommendations.append({
            "type": "overstock_warning",
            "priority": "medium",
            "icon": "📦",
            "title": f"{len(overstock)} Products Overstocked",
            "description": "Reduce future order quantities to optimize inventory levels.",
            "action": "Adjust reorder quantities in next purchase",
            "impact": "Reduces carrying cost and frees shelf space"
        })

    if high_velocity:
        recommendations.append({
            "type": "high_performer",
            "priority": "info",
            "icon": "🏆",
            "title": f"{len(high_velocity)} Fast-Moving Products",
            "description": "These products have high demand velocity — ensure continuous supply.",
            "action": "Prioritize reordering these items to prevent stockouts",
            "impact": "Prevents revenue loss from stockouts on best sellers"
        })

    return {
        "recommendations": recommendations,
        "dead_stock": dead_stock[:5],
        "overstock": overstock[:5],
        "high_velocity": high_velocity[:5],
        "total_locked_capital": round(total_locked_capital, 2),
        "optimization_score": _calculate_optimization_score(inventory, product_sales)
    }


def _calculate_optimization_score(inventory, product_sales) -> Dict:
    """Calculate an overall inventory health/optimization score (0-100)."""
    if not inventory:
        return {"score": 50, "label": "No data"}

    total = len(inventory)
    low = sum(1 for i in inventory if i["current_quantity"] <= i["reorder_point"])
    over = sum(1 for i in inventory if i["current_quantity"] > i["optimal_quantity"] * 1.5)
    dead = sum(1 for i in inventory if product_sales.get(i["product_id"], {"qty": 0})["qty"] == 0 and i["current_quantity"] > 5)

    # Penalties
    low_penalty = (low / total) * 30
    over_penalty = (over / total) * 20
    dead_penalty = (dead / total) * 25

    score = max(0, min(100, 100 - low_penalty - over_penalty - dead_penalty))

    if score >= 80: label = "Excellent"
    elif score >= 60: label = "Good"
    elif score >= 40: label = "Needs Improvement"
    else: label = "Critical"

    return {"score": round(score, 1), "label": label}


# ═══════════════════════════════════════════════════════════════════
#  SMART REORDER CALCULATIONS
# ═══════════════════════════════════════════════════════════════════

def calculate_smart_reorder(store_id: str) -> List[Dict]:
    """
    Calculate optimal reorder quantities using AI predictions + safety stock.
    Formula: Reorder Qty = (Predicted Daily Demand × Lead Time) + Safety Stock - Current Stock
    """
    low_stock = data_store.get_low_stock(store_id)
    inventory = data_store.get_inventory(store_id)
    reorder_items = []

    # Include items near reorder point too (within 150%)
    near_low = [i for i in inventory if i["current_quantity"] <= i["reorder_point"] * 1.5]
    all_candidates = {i["product_id"]: i for i in low_stock + near_low}

    for pid, item in all_candidates.items():
        # Get AI prediction for this product
        forecast = prediction_engine.generate_product_forecast(store_id, pid, days_ahead=7)

        if forecast and forecast["predictions"]:
            avg_predicted = sum(p["predicted_quantity"] for p in forecast["predictions"]) / 7
            lead_time = 2  # Default 2 days delivery
            safety_stock = avg_predicted * 1.5  # 1.5 day safety buffer

            reorder_qty = max(0, (avg_predicted * lead_time) + safety_stock - item["current_quantity"])
            reorder_qty = math.ceil(reorder_qty / 5) * 5  # Round to nearest 5

            if reorder_qty > 0:
                est_cost = reorder_qty * item["unit_price"] * 0.85  # Wholesale discount

                reorder_items.append({
                    "product_id": pid,
                    "product_name": item["product_name"],
                    "category": item["category"],
                    "current_stock": item["current_quantity"],
                    "predicted_daily_demand": round(avg_predicted, 1),
                    "reorder_quantity": reorder_qty,
                    "estimated_cost": round(est_cost, 2),
                    "urgency": "critical" if item["current_quantity"] <= 5 else
                               "high" if item["current_quantity"] <= item["reorder_point"] else "medium",
                    "days_until_stockout": round(item["current_quantity"] / max(avg_predicted, 0.1), 1),
                    "confidence": forecast["model_confidence"],
                    "reasoning": f"AI predicts ~{avg_predicted:.0f} units/day demand. "
                                 f"With {item['current_quantity']} in stock and 2-day delivery, "
                                 f"need {reorder_qty} units to maintain supply."
                })

    reorder_items.sort(key=lambda r: {"critical": 0, "high": 1, "medium": 2}[r["urgency"]])
    return reorder_items


# ═══════════════════════════════════════════════════════════════════
#  EXPIRY RISK ANALYSIS
# ═══════════════════════════════════════════════════════════════════

def analyze_expiry_risk(store_id: str) -> List[Dict]:
    """
    Flag perishable items at risk of expiring before they're sold.
    Uses sales velocity vs shelf life to predict waste risk.
    """
    inventory = data_store.get_inventory(store_id)
    txns = data_store.get_transactions(store_id, txn_type="sale", days=14)

    product_velocity = defaultdict(float)
    for t in txns:
        for item in t["items"]:
            product_velocity[item["product_id"]] += item["quantity"]

    risk_items = []
    for inv_item in inventory:
        product = data_store.get_product(inv_item["product_id"])
        if not product or not product.get("is_perishable"):
            continue

        shelf_life = product.get("shelf_life_days", 7)
        daily_velocity = product_velocity.get(inv_item["product_id"], 0) / 14
        current_stock = inv_item["current_quantity"]

        if daily_velocity > 0:
            days_to_sell = current_stock / daily_velocity
        else:
            days_to_sell = 999

        if days_to_sell > shelf_life * 0.7:  # Risk if >70% of shelf life needed to sell
            waste_pct = max(0, (days_to_sell - shelf_life) / days_to_sell * 100)
            risk_level = "high" if waste_pct > 30 else "medium" if waste_pct > 10 else "low"

            risk_items.append({
                "product_name": inv_item["product_name"],
                "product_id": inv_item["product_id"],
                "current_stock": current_stock,
                "shelf_life_days": shelf_life,
                "days_to_sell_all": round(days_to_sell, 1),
                "daily_velocity": round(daily_velocity, 1),
                "waste_risk_pct": round(waste_pct, 1),
                "risk_level": risk_level,
                "estimated_waste_units": max(0, round(current_stock - daily_velocity * shelf_life)),
                "waste_value": round(max(0, current_stock - daily_velocity * shelf_life) * inv_item["unit_price"], 2),
                "recommendation": f"Sell {current_stock} units within {shelf_life} days. "
                                  f"Consider discount pricing if sales velocity doesn't increase."
            })

    risk_items.sort(key=lambda r: r["waste_risk_pct"], reverse=True)
    return risk_items


# ═══════════════════════════════════════════════════════════════════
#  CROSS-SELL ANALYSIS
# ═══════════════════════════════════════════════════════════════════

def analyze_cross_sell(store_id: str) -> List[Dict]:
    """
    Identify products frequently bought together (co-occurrence analysis).
    'Customers who buy X also buy Y' — useful for bundling suggestions.
    """
    txns = data_store.get_transactions(store_id, txn_type="sale", days=60)
    pair_counts = defaultdict(int)
    product_counts = defaultdict(int)

    for t in txns:
        items = [item["product_id"] for item in t["items"]]
        for i, a in enumerate(items):
            product_counts[a] += 1
            for b in items[i+1:]:
                pair = tuple(sorted([a, b]))
                pair_counts[pair] += 1

    # Find top co-occurring pairs
    top_pairs = sorted(pair_counts.items(), key=lambda x: x[1], reverse=True)[:10]

    results = []
    for (pid_a, pid_b), count in top_pairs:
        product_a = data_store.get_product(pid_a)
        product_b = data_store.get_product(pid_b)
        if not product_a or not product_b:
            continue

        # Confidence = co-occurrence / min(individual count)
        min_count = min(product_counts[pid_a], product_counts[pid_b])
        confidence = count / min_count if min_count > 0 else 0

        results.append({
            "product_a": product_a["name"],
            "product_b": product_b["name"],
            "co_occurrence": count,
            "confidence": round(confidence, 2),
            "insight": f"Customers who buy {product_a['name']} also buy {product_b['name']} "
                       f"({count} times, {confidence*100:.0f}% of the time)"
        })

    return results


# ═══════════════════════════════════════════════════════════════════
#  COMPREHENSIVE AI INSIGHTS
# ═══════════════════════════════════════════════════════════════════

def get_all_insights(store_id: str) -> Dict:
    """
    Generate comprehensive AI-driven insights for a store.
    This is the main endpoint used by the frontend AI panel.
    """
    anomalies = detect_sales_anomalies(store_id, days=30)
    profit_analysis = analyze_profit_optimization(store_id)
    smart_reorder = calculate_smart_reorder(store_id)
    expiry_risks = analyze_expiry_risk(store_id)
    cross_sell = analyze_cross_sell(store_id)
    accuracy = prediction_engine.get_prediction_accuracy_metrics(store_id)

    # Count total recommendations
    total_recs = (len(profit_analysis["recommendations"]) +
                  len(smart_reorder) + len(expiry_risks))

    # AI summary
    critical_items = sum(1 for r in smart_reorder if r["urgency"] == "critical")
    high_risk_expiry = sum(1 for e in expiry_risks if e["risk_level"] == "high")

    summary = []
    if critical_items:
        summary.append(f"🚨 {critical_items} items critically low — immediate reorder needed")
    if high_risk_expiry:
        summary.append(f"⏰ {high_risk_expiry} perishable items at high expiry risk")
    if profit_analysis["dead_stock"]:
        summary.append(f"📦 {len(profit_analysis['dead_stock'])} dead stock items wasting ₹{profit_analysis['total_locked_capital']:,.0f}")
    if anomalies:
        spikes = sum(1 for a in anomalies if a["type"] == "spike")
        drops = sum(1 for a in anomalies if a["type"] == "drop")
        if spikes:
            summary.append(f"📈 {spikes} unusual sales spikes detected in last 30 days")
        if drops:
            summary.append(f"📉 {drops} unusual sales drops detected")
    if not summary:
        summary.append("✅ Your store is performing well! No critical issues detected.")

    return {
        "store_id": store_id,
        "generated_at": datetime.now().isoformat(),
        "ai_summary": summary,
        "total_recommendations": total_recs,
        "prediction_accuracy": accuracy,
        "optimization_score": profit_analysis["optimization_score"],
        "anomalies": anomalies[:5],
        "profit_insights": profit_analysis,
        "smart_reorder": smart_reorder[:10],
        "expiry_risks": expiry_risks[:5],
        "cross_sell": cross_sell[:5],
    }
