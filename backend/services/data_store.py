"""
In-memory data store with comprehensive synthetic data for the KiranaConnect prototype.
Simulates DynamoDB tables locally. When USE_LOCAL_DATA=true, all data is served from here.
"""

import random
import math
from datetime import datetime, timedelta
from typing import List, Dict, Optional


# ═══════════════════════════════════════════════════════════════════
# SYNTHETIC DATA GENERATION
# ═══════════════════════════════════════════════════════════════════

def _generate_products() -> List[dict]:
    """Generate 60+ realistic Kirana store products."""
    products = [
        # Groceries - Staples
        {"product_id": "P001", "name": "Tata Salt (1kg)", "category": "Groceries", "subcategory": "Staples", "brand": "Tata", "unit": "packet", "typical_price": 28, "shelf_life_days": 365, "is_perishable": False},
        {"product_id": "P002", "name": "Fortune Sunflower Oil (1L)", "category": "Groceries", "subcategory": "Cooking Oil", "brand": "Fortune", "unit": "bottle", "typical_price": 155, "shelf_life_days": 180, "is_perishable": False},
        {"product_id": "P003", "name": "India Gate Basmati Rice (5kg)", "category": "Groceries", "subcategory": "Staples", "brand": "India Gate", "unit": "bag", "typical_price": 425, "shelf_life_days": 365, "is_perishable": False},
        {"product_id": "P004", "name": "Aashirvaad Atta (5kg)", "category": "Groceries", "subcategory": "Staples", "brand": "Aashirvaad", "unit": "bag", "typical_price": 295, "shelf_life_days": 180, "is_perishable": False},
        {"product_id": "P005", "name": "Toor Dal (1kg)", "category": "Groceries", "subcategory": "Pulses", "brand": "Local", "unit": "packet", "typical_price": 145, "shelf_life_days": 180, "is_perishable": False},
        {"product_id": "P006", "name": "Sugar (1kg)", "category": "Groceries", "subcategory": "Staples", "brand": "Local", "unit": "packet", "typical_price": 45, "shelf_life_days": 365, "is_perishable": False},
        {"product_id": "P007", "name": "MDH Garam Masala (100g)", "category": "Groceries", "subcategory": "Spices", "brand": "MDH", "unit": "packet", "typical_price": 72, "shelf_life_days": 365, "is_perishable": False},
        {"product_id": "P008", "name": "Turmeric Powder (200g)", "category": "Groceries", "subcategory": "Spices", "brand": "Everest", "unit": "packet", "typical_price": 55, "shelf_life_days": 365, "is_perishable": False},
        {"product_id": "P009", "name": "Red Chilli Powder (200g)", "category": "Groceries", "subcategory": "Spices", "brand": "Everest", "unit": "packet", "typical_price": 65, "shelf_life_days": 365, "is_perishable": False},
        {"product_id": "P010", "name": "Moong Dal (1kg)", "category": "Groceries", "subcategory": "Pulses", "brand": "Local", "unit": "packet", "typical_price": 130, "shelf_life_days": 180, "is_perishable": False},

        # Dairy & Perishables
        {"product_id": "P011", "name": "Amul Milk (500ml)", "category": "Dairy", "subcategory": "Milk", "brand": "Amul", "unit": "packet", "typical_price": 30, "shelf_life_days": 3, "is_perishable": True},
        {"product_id": "P012", "name": "Amul Butter (100g)", "category": "Dairy", "subcategory": "Butter", "brand": "Amul", "unit": "packet", "typical_price": 56, "shelf_life_days": 30, "is_perishable": True},
        {"product_id": "P013", "name": "Amul Curd (400g)", "category": "Dairy", "subcategory": "Curd", "brand": "Amul", "unit": "cup", "typical_price": 35, "shelf_life_days": 7, "is_perishable": True},
        {"product_id": "P014", "name": "Paneer (200g)", "category": "Dairy", "subcategory": "Paneer", "brand": "Amul", "unit": "packet", "typical_price": 80, "shelf_life_days": 5, "is_perishable": True},
        {"product_id": "P015", "name": "Bread (400g)", "category": "Bakery", "subcategory": "Bread", "brand": "Britannia", "unit": "packet", "typical_price": 40, "shelf_life_days": 4, "is_perishable": True},

        # Beverages
        {"product_id": "P016", "name": "Coca-Cola (750ml)", "category": "Beverages", "subcategory": "Soft Drinks", "brand": "Coca-Cola", "unit": "bottle", "typical_price": 40, "shelf_life_days": 180, "is_perishable": False},
        {"product_id": "P017", "name": "Pepsi (750ml)", "category": "Beverages", "subcategory": "Soft Drinks", "brand": "Pepsi", "unit": "bottle", "typical_price": 40, "shelf_life_days": 180, "is_perishable": False},
        {"product_id": "P018", "name": "Tata Tea Gold (500g)", "category": "Beverages", "subcategory": "Tea", "brand": "Tata", "unit": "packet", "typical_price": 265, "shelf_life_days": 365, "is_perishable": False},
        {"product_id": "P019", "name": "Nescafe Classic (100g)", "category": "Beverages", "subcategory": "Coffee", "brand": "Nescafe", "unit": "jar", "typical_price": 295, "shelf_life_days": 365, "is_perishable": False},
        {"product_id": "P020", "name": "Bisleri Water (1L)", "category": "Beverages", "subcategory": "Water", "brand": "Bisleri", "unit": "bottle", "typical_price": 20, "shelf_life_days": 180, "is_perishable": False},
        {"product_id": "P021", "name": "Frooti Mango (200ml)", "category": "Beverages", "subcategory": "Juice", "brand": "Parle", "unit": "tetrapack", "typical_price": 10, "shelf_life_days": 90, "is_perishable": False},
        {"product_id": "P022", "name": "Real Fruit Juice (1L)", "category": "Beverages", "subcategory": "Juice", "brand": "Dabur", "unit": "tetrapack", "typical_price": 99, "shelf_life_days": 90, "is_perishable": False},

        # Snacks
        {"product_id": "P023", "name": "Lay's Classic Salted (52g)", "category": "Snacks", "subcategory": "Chips", "brand": "Lay's", "unit": "packet", "typical_price": 20, "shelf_life_days": 90, "is_perishable": False},
        {"product_id": "P024", "name": "Kurkure Masala Munch (90g)", "category": "Snacks", "subcategory": "Namkeen", "brand": "Kurkure", "unit": "packet", "typical_price": 20, "shelf_life_days": 90, "is_perishable": False},
        {"product_id": "P025", "name": "Parle-G Biscuit (250g)", "category": "Snacks", "subcategory": "Biscuits", "brand": "Parle", "unit": "packet", "typical_price": 25, "shelf_life_days": 180, "is_perishable": False},
        {"product_id": "P026", "name": "Britannia Good Day (250g)", "category": "Snacks", "subcategory": "Biscuits", "brand": "Britannia", "unit": "packet", "typical_price": 40, "shelf_life_days": 180, "is_perishable": False},
        {"product_id": "P027", "name": "Maggi Noodles (70g x4)", "category": "Snacks", "subcategory": "Instant Food", "brand": "Maggi", "unit": "pack", "typical_price": 56, "shelf_life_days": 180, "is_perishable": False},
        {"product_id": "P028", "name": "Haldiram Bhujia (200g)", "category": "Snacks", "subcategory": "Namkeen", "brand": "Haldiram", "unit": "packet", "typical_price": 60, "shelf_life_days": 120, "is_perishable": False},
        {"product_id": "P029", "name": "Oreo Biscuit (120g)", "category": "Snacks", "subcategory": "Biscuits", "brand": "Cadbury", "unit": "packet", "typical_price": 30, "shelf_life_days": 180, "is_perishable": False},
        {"product_id": "P030", "name": "Dark Fantasy (75g)", "category": "Snacks", "subcategory": "Biscuits", "brand": "Sunfeast", "unit": "packet", "typical_price": 40, "shelf_life_days": 180, "is_perishable": False},

        # Personal Care
        {"product_id": "P031", "name": "Colgate Toothpaste (100g)", "category": "Personal Care", "subcategory": "Oral Care", "brand": "Colgate", "unit": "tube", "typical_price": 68, "shelf_life_days": 730, "is_perishable": False},
        {"product_id": "P032", "name": "Dove Soap (100g)", "category": "Personal Care", "subcategory": "Soap", "brand": "Dove", "unit": "bar", "typical_price": 52, "shelf_life_days": 730, "is_perishable": False},
        {"product_id": "P033", "name": "Head & Shoulders (180ml)", "category": "Personal Care", "subcategory": "Shampoo", "brand": "H&S", "unit": "bottle", "typical_price": 195, "shelf_life_days": 730, "is_perishable": False},
        {"product_id": "P034", "name": "Dettol Handwash (200ml)", "category": "Personal Care", "subcategory": "Handwash", "brand": "Dettol", "unit": "bottle", "typical_price": 75, "shelf_life_days": 730, "is_perishable": False},
        {"product_id": "P035", "name": "Nivea Body Lotion (200ml)", "category": "Personal Care", "subcategory": "Skin Care", "brand": "Nivea", "unit": "bottle", "typical_price": 199, "shelf_life_days": 730, "is_perishable": False},
        {"product_id": "P036", "name": "Gillette Guard Razor", "category": "Personal Care", "subcategory": "Grooming", "brand": "Gillette", "unit": "piece", "typical_price": 45, "shelf_life_days": None, "is_perishable": False},

        # Household
        {"product_id": "P037", "name": "Vim Dishwash Bar (300g)", "category": "Household", "subcategory": "Cleaning", "brand": "Vim", "unit": "bar", "typical_price": 32, "shelf_life_days": 730, "is_perishable": False},
        {"product_id": "P038", "name": "Surf Excel (1kg)", "category": "Household", "subcategory": "Detergent", "brand": "Surf Excel", "unit": "packet", "typical_price": 145, "shelf_life_days": 730, "is_perishable": False},
        {"product_id": "P039", "name": "Harpic Toilet Cleaner (500ml)", "category": "Household", "subcategory": "Cleaning", "brand": "Harpic", "unit": "bottle", "typical_price": 99, "shelf_life_days": 730, "is_perishable": False},
        {"product_id": "P040", "name": "Good Knight Liquid (45ml)", "category": "Household", "subcategory": "Pest Control", "brand": "Good Knight", "unit": "refill", "typical_price": 62, "shelf_life_days": 365, "is_perishable": False},
        {"product_id": "P041", "name": "Lizol Floor Cleaner (500ml)", "category": "Household", "subcategory": "Cleaning", "brand": "Lizol", "unit": "bottle", "typical_price": 115, "shelf_life_days": 730, "is_perishable": False},

        # Confectionery
        {"product_id": "P042", "name": "Cadbury Dairy Milk (50g)", "category": "Confectionery", "subcategory": "Chocolate", "brand": "Cadbury", "unit": "bar", "typical_price": 50, "shelf_life_days": 270, "is_perishable": False},
        {"product_id": "P043", "name": "5 Star (25g)", "category": "Confectionery", "subcategory": "Chocolate", "brand": "Cadbury", "unit": "bar", "typical_price": 10, "shelf_life_days": 270, "is_perishable": False},
        {"product_id": "P044", "name": "Mints (Polo)", "category": "Confectionery", "subcategory": "Candy", "brand": "Nestle", "unit": "roll", "typical_price": 5, "shelf_life_days": 365, "is_perishable": False},
        {"product_id": "P045", "name": "Center Fresh Gum", "category": "Confectionery", "subcategory": "Gum", "brand": "Perfetti", "unit": "packet", "typical_price": 5, "shelf_life_days": 365, "is_perishable": False},

        # Ready to Eat / Cook
        {"product_id": "P046", "name": "MTR Poha Mix (180g)", "category": "Ready to Cook", "subcategory": "Breakfast", "brand": "MTR", "unit": "packet", "typical_price": 45, "shelf_life_days": 180, "is_perishable": False},
        {"product_id": "P047", "name": "Saffola Oats (1kg)", "category": "Ready to Cook", "subcategory": "Breakfast", "brand": "Saffola", "unit": "packet", "typical_price": 175, "shelf_life_days": 180, "is_perishable": False},
        {"product_id": "P048", "name": "Knorr Soup (12g)", "category": "Ready to Cook", "subcategory": "Soup", "brand": "Knorr", "unit": "sachet", "typical_price": 15, "shelf_life_days": 180, "is_perishable": False},

        # Frozen & Others
        {"product_id": "P049", "name": "Eggs (12 pack)", "category": "Dairy", "subcategory": "Eggs", "brand": "Local", "unit": "dozen", "typical_price": 84, "shelf_life_days": 15, "is_perishable": True},
        {"product_id": "P050", "name": "Onion (1kg)", "category": "Vegetables", "subcategory": "Fresh", "brand": "Local", "unit": "kg", "typical_price": 35, "shelf_life_days": 14, "is_perishable": True},
        {"product_id": "P051", "name": "Potato (1kg)", "category": "Vegetables", "subcategory": "Fresh", "brand": "Local", "unit": "kg", "typical_price": 30, "shelf_life_days": 21, "is_perishable": True},
        {"product_id": "P052", "name": "Tomato (1kg)", "category": "Vegetables", "subcategory": "Fresh", "brand": "Local", "unit": "kg", "typical_price": 40, "shelf_life_days": 7, "is_perishable": True},

        # Additional items
        {"product_id": "P053", "name": "Catch Black Pepper (50g)", "category": "Groceries", "subcategory": "Spices", "brand": "Catch", "unit": "packet", "typical_price": 85, "shelf_life_days": 365, "is_perishable": False},
        {"product_id": "P054", "name": "Ghee (500ml)", "category": "Dairy", "subcategory": "Ghee", "brand": "Amul", "unit": "jar", "typical_price": 290, "shelf_life_days": 180, "is_perishable": False},
        {"product_id": "P055", "name": "Soyabean Oil (1L)", "category": "Groceries", "subcategory": "Cooking Oil", "brand": "Fortune", "unit": "bottle", "typical_price": 130, "shelf_life_days": 180, "is_perishable": False},
        {"product_id": "P056", "name": "Chana Dal (1kg)", "category": "Groceries", "subcategory": "Pulses", "brand": "Local", "unit": "packet", "typical_price": 110, "shelf_life_days": 180, "is_perishable": False},
        {"product_id": "P057", "name": "Rajma (1kg)", "category": "Groceries", "subcategory": "Pulses", "brand": "Local", "unit": "packet", "typical_price": 135, "shelf_life_days": 180, "is_perishable": False},
        {"product_id": "P058", "name": "Maida (1kg)", "category": "Groceries", "subcategory": "Staples", "brand": "Local", "unit": "packet", "typical_price": 40, "shelf_life_days": 180, "is_perishable": False},
        {"product_id": "P059", "name": "Besan (500g)", "category": "Groceries", "subcategory": "Staples", "brand": "Local", "unit": "packet", "typical_price": 55, "shelf_life_days": 180, "is_perishable": False},
        {"product_id": "P060", "name": "Parachute Coconut Oil (200ml)", "category": "Personal Care", "subcategory": "Hair Oil", "brand": "Parachute", "unit": "bottle", "typical_price": 105, "shelf_life_days": 730, "is_perishable": False},
    ]
    return products


def _generate_stores() -> List[dict]:
    """Generate 3 sample Kirana stores."""
    return [
        {
            "store_id": "S001",
            "owner_name": "Rajesh Kumar",
            "phone_number": "+919876543210",
            "store_name": "Rajesh General Store",
            "address": "Shop No. 12, Main Road, Koramangala",
            "city": "Bangalore",
            "state": "Karnataka",
            "pincode": "560034",
            "latitude": 12.9352,
            "longitude": 77.6245,
            "subscription_tier": "premium",
            "created_at": "2025-06-15T10:00:00"
        },
        {
            "store_id": "S002",
            "owner_name": "Priya Sharma",
            "phone_number": "+919876543211",
            "store_name": "Priya Kirana & Provisions",
            "address": "45, Gandhi Nagar, Andheri East",
            "city": "Mumbai",
            "state": "Maharashtra",
            "pincode": "400069",
            "latitude": 19.1136,
            "longitude": 72.8697,
            "subscription_tier": "basic",
            "created_at": "2025-08-20T09:30:00"
        },
        {
            "store_id": "S003",
            "owner_name": "Mohammed Farooq",
            "phone_number": "+919876543212",
            "store_name": "Farooq Provision Store",
            "address": "78, Lajpat Nagar, Block C",
            "city": "Delhi",
            "state": "Delhi",
            "pincode": "110024",
            "latitude": 28.5691,
            "longitude": 77.2404,
            "subscription_tier": "premium",
            "created_at": "2025-07-10T11:00:00"
        }
    ]


def _generate_distributors() -> List[dict]:
    """Generate 5 sample distributors."""
    return [
        {"distributor_id": "D001", "name": "Metro Wholesale Hub", "phone": "+919800000001", "email": "metro@wholesale.com", "address": "Industrial Area, Phase 2", "city": "Bangalore", "rating": 4.5, "categories": ["Groceries", "Household"]},
        {"distributor_id": "D002", "name": "Fresh & Fast Distributors", "phone": "+919800000002", "email": "fresh@fast.com", "address": "APMC Market, Vashi", "city": "Mumbai", "rating": 4.2, "categories": ["Dairy", "Vegetables", "Bakery"]},
        {"distributor_id": "D003", "name": "FMCG Direct Supply", "phone": "+919800000003", "email": "fmcg@direct.com", "address": "Okhla Industrial Estate", "city": "Delhi", "rating": 4.7, "categories": ["Personal Care", "Household", "Confectionery"]},
        {"distributor_id": "D004", "name": "Beverage Kings", "phone": "+919800000004", "email": "bev@kings.com", "address": "Whitefield Road", "city": "Bangalore", "rating": 4.0, "categories": ["Beverages", "Snacks"]},
        {"distributor_id": "D005", "name": "Snack World Traders", "phone": "+919800000005", "email": "snack@world.com", "address": "Kirti Nagar, Ring Road", "city": "Delhi", "rating": 4.3, "categories": ["Snacks", "Confectionery", "Ready to Cook"]},
    ]


def _generate_inventory(products: List[dict], store_id: str) -> List[dict]:
    """Generate inventory for a store (random subset of products)."""
    random.seed(hash(store_id) + 42)
    num_products = random.randint(35, len(products))
    selected = random.sample(products, num_products)
    inventory = []
    for i, p in enumerate(selected):
        base_qty = random.randint(5, 120)
        reorder = max(5, base_qty // 4)
        optimal = base_qty * 2
        inventory.append({
            "inventory_id": f"INV-{store_id}-{i+1:03d}",
            "store_id": store_id,
            "product_id": p["product_id"],
            "product_name": p["name"],
            "category": p["category"],
            "current_quantity": base_qty,
            "reorder_point": reorder,
            "optimal_quantity": optimal,
            "unit": p["unit"],
            "unit_price": p["typical_price"],
            "last_updated": (datetime.now() - timedelta(hours=random.randint(1, 48))).isoformat()
        })
    return inventory


def _generate_transactions(products: List[dict], store_id: str, days: int = 90) -> List[dict]:
    """Generate realistic transaction history for a store."""
    random.seed(hash(store_id) + 100)
    transactions = []
    now = datetime.now()

    for day_offset in range(days, 0, -1):
        date = now - timedelta(days=day_offset)
        day_of_week = date.weekday()

        # More transactions on weekends
        num_sales = random.randint(8, 18) if day_of_week >= 5 else random.randint(5, 12)
        num_purchases = 1 if day_offset % 3 == 0 else 0  # Purchase every 3 days

        # Sales
        for t in range(num_sales):
            num_items = random.randint(1, 5)
            items_selected = random.sample(products, min(num_items, len(products)))
            t_items = []
            total = 0
            for item in items_selected:
                qty = random.randint(1, 8)
                price = item["typical_price"] * (1 + random.uniform(-0.05, 0.05))
                item_total = round(qty * price, 2)
                total += item_total
                t_items.append({
                    "product_id": item["product_id"],
                    "product_name": item["name"],
                    "quantity": qty,
                    "unit_price": round(price, 2),
                    "total_price": item_total
                })

            transactions.append({
                "transaction_id": f"TXN-{store_id}-{day_offset:03d}-S{t+1:02d}",
                "store_id": store_id,
                "transaction_type": "sale",
                "transaction_date": date.replace(
                    hour=random.randint(8, 21),
                    minute=random.randint(0, 59)
                ).isoformat(),
                "total_amount": round(total, 2),
                "source": random.choice(["whatsapp", "manual", "manual"]),
                "items": t_items
            })

        # Purchases
        if num_purchases > 0:
            num_items = random.randint(5, 15)
            items_selected = random.sample(products, min(num_items, len(products)))
            t_items = []
            total = 0
            for item in items_selected:
                qty = random.randint(20, 100)
                price = item["typical_price"] * 0.85  # wholesale discount
                item_total = round(qty * price, 2)
                total += item_total
                t_items.append({
                    "product_id": item["product_id"],
                    "product_name": item["name"],
                    "quantity": qty,
                    "unit_price": round(price, 2),
                    "total_price": item_total
                })

            transactions.append({
                "transaction_id": f"TXN-{store_id}-{day_offset:03d}-P01",
                "store_id": store_id,
                "transaction_type": "purchase",
                "transaction_date": date.replace(hour=7, minute=30).isoformat(),
                "total_amount": round(total, 2),
                "source": "manual",
                "items": t_items
            })

    return transactions


def _generate_predictions(products: List[dict], store_id: str) -> List[dict]:
    """Generate demand predictions for the next 7 days."""
    random.seed(hash(store_id) + 200)
    predictions = []
    now = datetime.now()

    # Pick top 20 products for predictions
    selected = random.sample(products, min(20, len(products)))

    for p in selected:
        days_pred = []
        base_demand = random.uniform(3, 25)

        for d in range(1, 8):
            date = now + timedelta(days=d)
            day_of_week = date.weekday()

            # Seasonal multiplier
            seasonal = 1.0 + 0.2 * math.sin(2 * math.pi * d / 7)

            # Weekend boost
            weekend_mult = 1.3 if day_of_week >= 5 else 1.0

            predicted = round(base_demand * seasonal * weekend_mult * random.uniform(0.8, 1.2), 1)
            margin = max(1, predicted * 0.15)

            days_pred.append({
                "date": date.strftime("%Y-%m-%d"),
                "predicted_quantity": predicted,
                "confidence_low": round(predicted - margin, 1),
                "confidence_high": round(predicted + margin, 1)
            })

        predictions.append({
            "prediction_id": f"PRED-{store_id}-{p['product_id']}",
            "store_id": store_id,
            "product_id": p["product_id"],
            "product_name": p["name"],
            "category": p["category"],
            "predictions": days_pred,
            "model_confidence": round(random.uniform(0.72, 0.95), 2),
            "factors": {
                "seasonality": round(random.uniform(0.1, 0.4), 2),
                "trend": random.choice(["increasing", "stable", "decreasing"]),
                "festival_impact": random.choice([None, "Holi (upcoming)", "Weekend surge"]),
                "weather_impact": random.choice([None, "Hot weather - beverage demand up", "Rain expected"])
            },
            "created_at": now.isoformat()
        })

    return predictions


def _generate_orders(store_id: str, distributors: List[dict], products: List[dict]) -> List[dict]:
    """Generate sample orders."""
    random.seed(hash(store_id) + 300)
    orders = []
    now = datetime.now()
    statuses = ["pending", "confirmed", "shipped", "delivered"]

    for i in range(8):
        dist = random.choice(distributors)
        num_items = random.randint(3, 8)
        items_selected = random.sample(products, min(num_items, len(products)))
        o_items = []
        total = 0
        for item in items_selected:
            qty = random.randint(10, 60)
            price = item["typical_price"] * 0.82
            item_total = round(qty * price, 2)
            total += item_total
            o_items.append({
                "product_id": item["product_id"],
                "product_name": item["name"],
                "quantity": qty,
                "unit_price": round(price, 2),
                "total_price": item_total
            })

        placed = now - timedelta(days=random.randint(0, 14))
        status = statuses[min(i % 4, 3)]
        delivered = (placed + timedelta(days=random.randint(1, 3))).isoformat() if status == "delivered" else None

        orders.append({
            "order_id": f"ORD-{store_id}-{i+1:03d}",
            "store_id": store_id,
            "distributor_id": dist["distributor_id"],
            "distributor_name": dist["name"],
            "status": status,
            "placed_at": placed.isoformat(),
            "expected_delivery": (placed + timedelta(days=2)).isoformat(),
            "delivered_at": delivered,
            "total_amount": round(total, 2),
            "items": o_items
        })

    return orders


# ═══════════════════════════════════════════════════════════════════
# DATA STORE SINGLETON
# ═══════════════════════════════════════════════════════════════════

class DataStore:
    """In-memory data store with pre-generated synthetic data."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

        # Generate all synthetic data
        self.products = _generate_products()
        self.stores = _generate_stores()
        self.distributors = _generate_distributors()

        self.inventory = {}   # store_id -> list
        self.transactions = {}  # store_id -> list
        self.predictions = {}  # store_id -> list
        self.orders = {}  # store_id -> list

        for store in self.stores:
            sid = store["store_id"]
            self.inventory[sid] = _generate_inventory(self.products, sid)
            self.transactions[sid] = _generate_transactions(self.products, sid)
            self.predictions[sid] = _generate_predictions(self.products, sid)
            self.orders[sid] = _generate_orders(sid, self.distributors, self.products)

    # ── Products ──
    def get_products(self, category: str = None, search: str = None) -> List[dict]:
        result = self.products
        if category:
            result = [p for p in result if p["category"].lower() == category.lower()]
        if search:
            q = search.lower()
            result = [p for p in result if q in p["name"].lower() or q in p.get("brand", "").lower()]
        return result

    def get_product(self, product_id: str) -> Optional[dict]:
        return next((p for p in self.products if p["product_id"] == product_id), None)

    def get_categories(self) -> List[str]:
        return list(set(p["category"] for p in self.products))

    # ── Stores ──
    def get_store(self, store_id: str) -> Optional[dict]:
        return next((s for s in self.stores if s["store_id"] == store_id), None)

    # ── Inventory ──
    def get_inventory(self, store_id: str, category: str = None) -> List[dict]:
        items = self.inventory.get(store_id, [])
        if category:
            items = [i for i in items if i["category"].lower() == category.lower()]
        return items

    def get_inventory_item(self, store_id: str, product_id: str) -> Optional[dict]:
        items = self.inventory.get(store_id, [])
        return next((i for i in items if i["product_id"] == product_id), None)

    def get_low_stock(self, store_id: str) -> List[dict]:
        items = self.inventory.get(store_id, [])
        return [i for i in items if i["current_quantity"] <= i["reorder_point"]]

    def update_inventory(self, store_id: str, product_id: str, quantity: float) -> Optional[dict]:
        item = self.get_inventory_item(store_id, product_id)
        if item:
            item["current_quantity"] = quantity
            item["last_updated"] = datetime.now().isoformat()
        return item

    # ── Transactions ──
    def get_transactions(self, store_id: str, txn_type: str = None, days: int = None) -> List[dict]:
        txns = self.transactions.get(store_id, [])
        if txn_type:
            txns = [t for t in txns if t["transaction_type"] == txn_type]
        if days:
            cutoff = (datetime.now() - timedelta(days=days)).isoformat()
            txns = [t for t in txns if t["transaction_date"] >= cutoff]
        return txns

    def add_transaction(self, store_id: str, txn: dict):
        if store_id not in self.transactions:
            self.transactions[store_id] = []
        self.transactions[store_id].append(txn)
        return txn

    # ── Predictions ──
    def get_predictions(self, store_id: str) -> List[dict]:
        return self.predictions.get(store_id, [])

    def get_prediction(self, store_id: str, product_id: str) -> Optional[dict]:
        preds = self.predictions.get(store_id, [])
        return next((p for p in preds if p["product_id"] == product_id), None)

    # ── Orders ──
    def get_orders(self, store_id: str, status: str = None) -> List[dict]:
        orders = self.orders.get(store_id, [])
        if status:
            orders = [o for o in orders if o["status"] == status]
        return orders

    def get_order(self, store_id: str, order_id: str) -> Optional[dict]:
        orders = self.orders.get(store_id, [])
        return next((o for o in orders if o["order_id"] == order_id), None)

    def update_order_status(self, store_id: str, order_id: str, status: str) -> Optional[dict]:
        order = self.get_order(store_id, order_id)
        if order:
            order["status"] = status
            if status == "delivered":
                order["delivered_at"] = datetime.now().isoformat()
        return order

    def add_order(self, store_id: str, order: dict):
        if store_id not in self.orders:
            self.orders[store_id] = []
        self.orders[store_id].append(order)
        return order

    # ── Distributors ──
    def get_distributors(self) -> List[dict]:
        return self.distributors

    def get_distributor(self, distributor_id: str) -> Optional[dict]:
        return next((d for d in self.distributors if d["distributor_id"] == distributor_id), None)


# Global singleton
data_store = DataStore()
