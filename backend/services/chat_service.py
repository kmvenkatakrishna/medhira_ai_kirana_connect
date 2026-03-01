"""Chat service — simulates WhatsApp NLP with intent classification and response generation."""

import random
from datetime import datetime
from .data_store import data_store
from . import analytics_service


# Intent patterns (keyword-based NLP simulation)
INTENT_PATTERNS = {
    "check_inventory": [
        "stock", "inventory", "how many", "kitna", "kya hai", "check",
        "available", "quantity", "stk", "remaining", "left"
    ],
    "add_purchase": [
        "bought", "purchased", "kharida", "buy", "added", "received",
        "arrival", "supply", "delivered", "purchase", "laya"
    ],
    "add_sale": [
        "sold", "sale", "becha", "selling", "customer", "bikta"
    ],
    "get_forecast": [
        "predict", "forecast", "demand", "next week", "upcoming",
        "prediction", "kitna chahiye", "order karna", "suggestion"
    ],
    "place_order": [
        "order", "reorder", "distributor", "supplier", "mangao",
        "supply", "refill", "restock"
    ],
    "get_report": [
        "report", "analytics", "summary", "performance", "sales",
        "revenue", "today", "aaj", "weekly", "monthly"
    ],
    "low_stock": [
        "low stock", "running out", "khatam", "finish", "empty",
        "alert", "warning", "shortage"
    ],
    "greeting": [
        "hi", "hello", "hey", "namaste", "good morning", "good evening",
        "namaskar", "hii", "hola"
    ],
    "help": [
        "help", "what can you do", "commands", "menu", "options",
        "kya kar sakte ho", "features", "guide"
    ]
}

# Product name shortcuts
PRODUCT_ALIASES = {
    "milk": "P011", "doodh": "P011",
    "oil": "P002", "tel": "P002",
    "rice": "P003", "chawal": "P003",
    "atta": "P004", "flour": "P004",
    "dal": "P005", "toor": "P005",
    "sugar": "P006", "cheeni": "P006",
    "salt": "P001", "namak": "P001",
    "tea": "P018", "chai": "P018",
    "coffee": "P019",
    "maggi": "P027", "noodles": "P027",
    "biscuit": "P025", "parle": "P025",
    "soap": "P032",
    "bread": "P015", "roti": "P015",
    "eggs": "P049", "anda": "P049",
    "onion": "P050", "pyaaz": "P050",
    "potato": "P051", "aloo": "P051",
    "tomato": "P052", "tamatar": "P052",
    "coke": "P016", "pepsi": "P017",
    "chips": "P023", "lays": "P023",
    "chocolate": "P042", "dairy milk": "P042",
    "ghee": "P054",
    "butter": "P012", "makhan": "P012",
    "curd": "P013", "dahi": "P013",
    "paneer": "P014",
    "shampoo": "P033",
    "toothpaste": "P031",
    "detergent": "P038", "surf": "P038",
}

DEFAULT_STORE = "S001"


def classify_intent(text: str) -> dict:
    """Classify user intent from message text."""
    text_lower = text.lower().strip()

    best_intent = "unknown"
    best_score = 0
    matched_entities = {}

    for intent, patterns in INTENT_PATTERNS.items():
        score = sum(1 for p in patterns if p in text_lower)
        if score > best_score:
            best_score = score
            best_intent = intent

    # Extract product entities
    for alias, pid in PRODUCT_ALIASES.items():
        if alias in text_lower:
            product = data_store.get_product(pid)
            if product:
                matched_entities["product"] = product["name"]
                matched_entities["product_id"] = pid
                break

    # Extract quantity
    import re
    qty_match = re.search(r'(\d+)\s*(kg|packet|piece|litre|liter|bottle|dozen|l|pcs)?', text_lower)
    if qty_match:
        matched_entities["quantity"] = int(qty_match.group(1))
        if qty_match.group(2):
            matched_entities["unit"] = qty_match.group(2)

    return {
        "intent": best_intent,
        "confidence": min(0.95, 0.5 + best_score * 0.15),
        "entities": matched_entities
    }


def generate_response(message: str, store_id: str = None) -> dict:
    """Process a chat message and generate an AI response."""
    if not store_id:
        store_id = DEFAULT_STORE

    result = classify_intent(message)
    intent = result["intent"]
    entities = result["entities"]

    response = ""
    suggestions = []

    if intent == "greeting":
        store = data_store.get_store(store_id)
        owner = store["owner_name"] if store else "there"
        response = f"🙏 Namaste {owner}! Welcome to KiranaConnect AI.\n\nI'm your smart inventory assistant. I can help you with:\n📦 Check stock levels\n📊 View sales reports\n🔮 Demand predictions\n📋 Place orders\n⚠️ Low stock alerts\n\nHow can I help you today?"
        suggestions = ["Check inventory", "Today's report", "Low stock alerts", "Demand forecast"]

    elif intent == "help":
        response = "🤖 **KiranaConnect AI Commands:**\n\n" \
                   "📦 **Inventory**: \"Check stock\" or \"How many milk packets?\"\n" \
                   "➕ **Add Purchase**: \"Bought 50 packets of dal\"\n" \
                   "💰 **Record Sale**: \"Sold 10 kg rice\"\n" \
                   "📊 **Reports**: \"Today's report\" or \"Weekly sales\"\n" \
                   "🔮 **Forecast**: \"Predict demand for milk\"\n" \
                   "📋 **Orders**: \"Order suggestions\" or \"Place order\"\n" \
                   "⚠️ **Alerts**: \"Low stock alerts\"\n\n" \
                   "You can also send photos of bills for automatic entry!"
        suggestions = ["Check inventory", "Today's report", "Predict demand", "Low stock"]

    elif intent == "check_inventory":
        if "product_id" in entities:
            item = data_store.get_inventory_item(store_id, entities["product_id"])
            if item:
                status_emoji = "✅" if item["current_quantity"] > item["reorder_point"] else "⚠️"
                response = f"{status_emoji} **{item['product_name']}**\n\n" \
                           f"📦 Current Stock: **{item['current_quantity']} {item['unit']}s**\n" \
                           f"🔄 Reorder Point: {item['reorder_point']} {item['unit']}s\n" \
                           f"🎯 Optimal Level: {item['optimal_quantity']} {item['unit']}s\n" \
                           f"💰 Unit Price: ₹{item['unit_price']}\n" \
                           f"🕐 Last Updated: {item['last_updated'][:10]}"
                suggestions = [f"Predict demand for {entities['product']}", "Check all inventory", "Low stock alerts"]
            else:
                response = f"❌ Product **{entities.get('product', 'Unknown')}** not found in your inventory."
                suggestions = ["Add product", "Check all inventory"]
        else:
            inventory = data_store.get_inventory(store_id)
            low = data_store.get_low_stock(store_id)
            total_value = sum(i["current_quantity"] * i["unit_price"] for i in inventory)
            response = f"📦 **Inventory Summary**\n\n" \
                       f"📊 Total Products: **{len(inventory)}**\n" \
                       f"💰 Total Value: **₹{total_value:,.0f}**\n" \
                       f"⚠️ Low Stock Items: **{len(low)}**\n\n"
            if low:
                response += "**⚠️ Low Stock Alert:**\n"
                for item in low[:5]:
                    response += f"  • {item['product_name']}: {item['current_quantity']} {item['unit']}s (reorder at {item['reorder_point']})\n"
            suggestions = ["Low stock details", "Category breakdown", "Place order"]

    elif intent == "low_stock":
        low = data_store.get_low_stock(store_id)
        if low:
            response = f"⚠️ **Low Stock Alert — {len(low)} items need reordering!**\n\n"
            for i, item in enumerate(low, 1):
                deficit = item["reorder_point"] - item["current_quantity"]
                response += f"{i}. **{item['product_name']}**\n" \
                            f"   📦 Current: {item['current_quantity']} | " \
                            f"Reorder at: {item['reorder_point']} | " \
                            f"Need: +{max(0, deficit)}\n"
            response += "\n💡 Shall I generate an order for these items?"
            suggestions = ["Generate order", "Check full inventory", "Demand forecast"]
        else:
            response = "✅ All items are well-stocked! No reordering needed right now."
            suggestions = ["Check inventory", "Today's report"]

    elif intent == "get_report":
        report = analytics_service.get_daily_report(store_id)
        response = f"📊 **Daily Sales Report — {report['date']}**\n\n" \
                   f"💰 Total Sales: **₹{report['total_sales']:,.0f}**\n" \
                   f"🧾 Transactions: **{report['total_transactions']}**\n\n"
        if report["top_products"]:
            response += "**🏆 Top Selling Products:**\n"
            for i, p in enumerate(report["top_products"][:5], 1):
                response += f"  {i}. {p['name']} — ₹{p['revenue']:,.0f} ({p['quantity']} units)\n"
        if report["low_stock_items"]:
            response += f"\n**⚠️ Low Stock ({len(report['low_stock_items'])} items)**\n"
            for item in report["low_stock_items"][:3]:
                response += f"  • {item['name']}: {item['current']} left\n"
        suggestions = ["Weekly report", "Monthly report", "Top products", "Sales trends"]

    elif intent == "get_forecast":
        if "product_id" in entities:
            pred = data_store.get_prediction(store_id, entities["product_id"])
            if pred:
                response = f"🔮 **Demand Forecast — {pred['product_name']}**\n" \
                           f"📈 Model Confidence: {pred['model_confidence']*100:.0f}%\n\n" \
                           f"**Next 7 Days Forecast:**\n"
                for day in pred["predictions"]:
                    response += f"  📅 {day['date']}: ~{day['predicted_quantity']} units " \
                                f"({day['confidence_low']}-{day['confidence_high']})\n"
                factors = pred["factors"]
                response += f"\n**📊 Key Factors:**\n" \
                            f"  • Trend: {factors.get('trend', 'stable')}\n" \
                            f"  • Seasonality Impact: {factors.get('seasonality', 0)*100:.0f}%\n"
                if factors.get("festival_impact"):
                    response += f"  • Festival: {factors['festival_impact']}\n"
                if factors.get("weather_impact"):
                    response += f"  • Weather: {factors['weather_impact']}\n"
                suggestions = [f"Order {entities['product']}", "Full forecast", "Check stock"]
            else:
                response = f"🔮 No prediction data available for {entities.get('product', 'this product')} yet."
                suggestions = ["Generate predictions", "Check other products"]
        else:
            preds = data_store.get_predictions(store_id)
            response = f"🔮 **Demand Forecast Summary**\n\n" \
                       f"Predictions available for **{len(preds)} products**.\n\n"
            for pred in preds[:5]:
                next_day = pred["predictions"][0] if pred["predictions"] else {}
                trend_emoji = {"increasing": "📈", "decreasing": "📉", "stable": "➡️"}.get(pred["factors"].get("trend", ""), "➡️")
                response += f"  {trend_emoji} **{pred['product_name']}**: ~{next_day.get('predicted_quantity', 0)} units tomorrow " \
                            f"(confidence: {pred['model_confidence']*100:.0f}%)\n"
            response += "\n💡 Ask me about any specific product for detailed forecast!"
            suggestions = ["Predict milk demand", "Predict rice demand", "Order suggestions"]

    elif intent == "add_purchase":
        product_name = entities.get("product", "items")
        qty = entities.get("quantity", "some")
        response = f"✅ **Purchase Recorded!**\n\n" \
                   f"📦 Product: {product_name}\n" \
                   f"📊 Quantity: {qty}\n" \
                   f"🕐 Time: {datetime.now().strftime('%I:%M %p')}\n\n" \
                   f"Your inventory has been updated. Current stock has been increased."
        suggestions = ["Check inventory", "Today's report", "Another purchase"]

    elif intent == "add_sale":
        product_name = entities.get("product", "items")
        qty = entities.get("quantity", "some")
        response = f"💰 **Sale Recorded!**\n\n" \
                   f"📦 Product: {product_name}\n" \
                   f"📊 Quantity Sold: {qty}\n" \
                   f"🕐 Time: {datetime.now().strftime('%I:%M %p')}\n\n" \
                   f"Your inventory has been updated accordingly."
        suggestions = ["Check inventory", "Today's sales", "Low stock alerts"]

    elif intent == "place_order":
        low = data_store.get_low_stock(store_id)
        if low:
            response = f"📋 **Order Suggestion Generated!**\n\n" \
                       f"Based on your current stock levels and demand forecast, " \
                       f"here's what you should order:\n\n"
            total_est = 0
            for item in low[:8]:
                order_qty = item["optimal_quantity"] - item["current_quantity"]
                est_cost = order_qty * item["unit_price"] * 0.85
                total_est += est_cost
                response += f"  📦 {item['product_name']}: {order_qty:.0f} {item['unit']}s " \
                            f"(~₹{est_cost:,.0f})\n"
            response += f"\n💰 **Estimated Total: ₹{total_est:,.0f}**\n\n" \
                        f"Shall I place this order with your preferred distributor?"
            suggestions = ["Confirm order", "Modify quantities", "Cancel"]
        else:
            response = "✅ All items are well-stocked! No orders needed at this time.\n\n" \
                       "💡 I'll notify you when items need reordering."
            suggestions = ["Check inventory", "Demand forecast"]

    else:
        response = "🤔 I didn't quite understand that. Could you try rephrasing?\n\n" \
                   "Here are some things I can help with:\n" \
                   "📦 \"Check stock\" — View inventory\n" \
                   "📊 \"Today's report\" — Sales summary\n" \
                   "🔮 \"Predict demand\" — Demand forecast\n" \
                   "📋 \"Place order\" — Order suggestions\n" \
                   "⚠️ \"Low stock\" — Low stock alerts"
        suggestions = ["Check inventory", "Today's report", "Low stock alerts", "Help"]

    return {
        "response": response,
        "intent": intent,
        "entities": entities,
        "suggestions": suggestions
    }
