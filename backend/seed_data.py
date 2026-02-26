"""Seed data for Kirana-Connect prototype - 50+ common Indian Kirana products."""
import json
from datetime import datetime, timedelta
import random
from sqlalchemy.orm import Session
from models import Store, Product, InventoryItem, Transaction, TransactionItem, Distributor, Order, OrderItem, Prediction


PRODUCTS = [
    # Dairy
    {"name": "Amul Milk (500ml)", "category": "Dairy", "subcategory": "Milk", "brand": "Amul", "unit": "packet", "typical_price": 25, "shelf_life_days": 3, "is_perishable": True},
    {"name": "Amul Butter (100g)", "category": "Dairy", "subcategory": "Butter", "brand": "Amul", "unit": "packet", "typical_price": 52, "shelf_life_days": 60, "is_perishable": True},
    {"name": "Mother Dairy Curd (200g)", "category": "Dairy", "subcategory": "Curd", "brand": "Mother Dairy", "unit": "cup", "typical_price": 20, "shelf_life_days": 7, "is_perishable": True},
    {"name": "Amul Cheese Slice (100g)", "category": "Dairy", "subcategory": "Cheese", "brand": "Amul", "unit": "packet", "typical_price": 40, "shelf_life_days": 90, "is_perishable": True},
    {"name": "Paneer (200g)", "category": "Dairy", "subcategory": "Paneer", "brand": "Local", "unit": "packet", "typical_price": 80, "shelf_life_days": 5, "is_perishable": True},

    # Groceries - Staples
    {"name": "Basmati Rice (1kg)", "category": "Groceries", "subcategory": "Rice", "brand": "India Gate", "unit": "kg", "typical_price": 80, "shelf_life_days": 365, "is_perishable": False},
    {"name": "Wheat Flour / Atta (5kg)", "category": "Groceries", "subcategory": "Flour", "brand": "Aashirvaad", "unit": "kg", "typical_price": 240, "shelf_life_days": 180, "is_perishable": False},
    {"name": "Toor Dal (1kg)", "category": "Groceries", "subcategory": "Pulses", "brand": "Tata", "unit": "kg", "typical_price": 140, "shelf_life_days": 365, "is_perishable": False},
    {"name": "Sugar (1kg)", "category": "Groceries", "subcategory": "Sugar", "brand": "Local", "unit": "kg", "typical_price": 45, "shelf_life_days": 730, "is_perishable": False},
    {"name": "Salt (1kg)", "category": "Groceries", "subcategory": "Salt", "brand": "Tata", "unit": "kg", "typical_price": 20, "shelf_life_days": 730, "is_perishable": False},
    {"name": "Refined Oil (1L)", "category": "Groceries", "subcategory": "Cooking Oil", "brand": "Fortune", "unit": "liter", "typical_price": 130, "shelf_life_days": 365, "is_perishable": False},
    {"name": "Mustard Oil (1L)", "category": "Groceries", "subcategory": "Cooking Oil", "brand": "Dhara", "unit": "liter", "typical_price": 145, "shelf_life_days": 365, "is_perishable": False},
    {"name": "Moong Dal (1kg)", "category": "Groceries", "subcategory": "Pulses", "brand": "Local", "unit": "kg", "typical_price": 120, "shelf_life_days": 365, "is_perishable": False},
    {"name": "Chana Dal (1kg)", "category": "Groceries", "subcategory": "Pulses", "brand": "Local", "unit": "kg", "typical_price": 95, "shelf_life_days": 365, "is_perishable": False},

    # Spices
    {"name": "Turmeric Powder (100g)", "category": "Spices", "subcategory": "Powder", "brand": "MDH", "unit": "packet", "typical_price": 35, "shelf_life_days": 365, "is_perishable": False},
    {"name": "Red Chilli Powder (100g)", "category": "Spices", "subcategory": "Powder", "brand": "MDH", "unit": "packet", "typical_price": 40, "shelf_life_days": 365, "is_perishable": False},
    {"name": "Garam Masala (50g)", "category": "Spices", "subcategory": "Masala", "brand": "MDH", "unit": "packet", "typical_price": 45, "shelf_life_days": 365, "is_perishable": False},
    {"name": "Cumin Seeds (100g)", "category": "Spices", "subcategory": "Seeds", "brand": "Everest", "unit": "packet", "typical_price": 55, "shelf_life_days": 365, "is_perishable": False},
    {"name": "Coriander Powder (100g)", "category": "Spices", "subcategory": "Powder", "brand": "Everest", "unit": "packet", "typical_price": 30, "shelf_life_days": 365, "is_perishable": False},

    # Beverages
    {"name": "Brooke Bond Tea (250g)", "category": "Beverages", "subcategory": "Tea", "brand": "Brooke Bond", "unit": "packet", "typical_price": 130, "shelf_life_days": 365, "is_perishable": False},
    {"name": "Nescafe Classic (50g)", "category": "Beverages", "subcategory": "Coffee", "brand": "Nescafe", "unit": "jar", "typical_price": 155, "shelf_life_days": 365, "is_perishable": False},
    {"name": "Coca-Cola (750ml)", "category": "Beverages", "subcategory": "Soft Drinks", "brand": "Coca-Cola", "unit": "bottle", "typical_price": 38, "shelf_life_days": 180, "is_perishable": False},
    {"name": "Thumbs Up (750ml)", "category": "Beverages", "subcategory": "Soft Drinks", "brand": "Coca-Cola", "unit": "bottle", "typical_price": 38, "shelf_life_days": 180, "is_perishable": False},
    {"name": "Bisleri Water (1L)", "category": "Beverages", "subcategory": "Water", "brand": "Bisleri", "unit": "bottle", "typical_price": 20, "shelf_life_days": 365, "is_perishable": False},

    # Snacks
    {"name": "Lays Classic Salted (52g)", "category": "Snacks", "subcategory": "Chips", "brand": "Lays", "unit": "packet", "typical_price": 20, "shelf_life_days": 120, "is_perishable": False},
    {"name": "Kurkure Masala Munch (80g)", "category": "Snacks", "subcategory": "Namkeen", "brand": "Kurkure", "unit": "packet", "typical_price": 20, "shelf_life_days": 120, "is_perishable": False},
    {"name": "Haldiram Bhujia (200g)", "category": "Snacks", "subcategory": "Namkeen", "brand": "Haldiram", "unit": "packet", "typical_price": 55, "shelf_life_days": 180, "is_perishable": False},
    {"name": "Parle-G Biscuit (800g)", "category": "Snacks", "subcategory": "Biscuits", "brand": "Parle", "unit": "packet", "typical_price": 60, "shelf_life_days": 240, "is_perishable": False},
    {"name": "Britannia Good Day (250g)", "category": "Snacks", "subcategory": "Biscuits", "brand": "Britannia", "unit": "packet", "typical_price": 40, "shelf_life_days": 240, "is_perishable": False},
    {"name": "Maggi Noodles (70g) 4-pack", "category": "Snacks", "subcategory": "Instant Food", "brand": "Maggi", "unit": "packet", "typical_price": 48, "shelf_life_days": 300, "is_perishable": False},

    # Personal Care
    {"name": "Dove Soap (75g)", "category": "Personal Care", "subcategory": "Soap", "brand": "Dove", "unit": "piece", "typical_price": 50, "shelf_life_days": 730, "is_perishable": False},
    {"name": "Colgate MaxFresh (80g)", "category": "Personal Care", "subcategory": "Toothpaste", "brand": "Colgate", "unit": "tube", "typical_price": 55, "shelf_life_days": 730, "is_perishable": False},
    {"name": "Head & Shoulders (180ml)", "category": "Personal Care", "subcategory": "Shampoo", "brand": "Head & Shoulders", "unit": "bottle", "typical_price": 170, "shelf_life_days": 730, "is_perishable": False},
    {"name": "Dettol Handwash (200ml)", "category": "Personal Care", "subcategory": "Handwash", "brand": "Dettol", "unit": "bottle", "typical_price": 55, "shelf_life_days": 730, "is_perishable": False},
    {"name": "Parachute Hair Oil (200ml)", "category": "Personal Care", "subcategory": "Hair Oil", "brand": "Parachute", "unit": "bottle", "typical_price": 105, "shelf_life_days": 730, "is_perishable": False},

    # Household
    {"name": "Surf Excel (1kg)", "category": "Household", "subcategory": "Detergent", "brand": "Surf Excel", "unit": "packet", "typical_price": 145, "shelf_life_days": 730, "is_perishable": False},
    {"name": "Vim Dishwash Bar (300g)", "category": "Household", "subcategory": "Dishwash", "brand": "Vim", "unit": "piece", "typical_price": 30, "shelf_life_days": 730, "is_perishable": False},
    {"name": "Harpic (500ml)", "category": "Household", "subcategory": "Cleaner", "brand": "Harpic", "unit": "bottle", "typical_price": 80, "shelf_life_days": 730, "is_perishable": False},
    {"name": "Phenyl (1L)", "category": "Household", "subcategory": "Cleaner", "brand": "Local", "unit": "bottle", "typical_price": 40, "shelf_life_days": 730, "is_perishable": False},

    # Bakery
    {"name": "Britannia Bread (400g)", "category": "Bakery", "subcategory": "Bread", "brand": "Britannia", "unit": "loaf", "typical_price": 35, "shelf_life_days": 3, "is_perishable": True},
    {"name": "Eggs (12 pack)", "category": "Bakery", "subcategory": "Eggs", "brand": "Local", "unit": "tray", "typical_price": 72, "shelf_life_days": 14, "is_perishable": True},

    # Confectionery
    {"name": "Cadbury Dairy Milk (50g)", "category": "Confectionery", "subcategory": "Chocolate", "brand": "Cadbury", "unit": "piece", "typical_price": 40, "shelf_life_days": 365, "is_perishable": False},
    {"name": "5 Star (22g)", "category": "Confectionery", "subcategory": "Chocolate", "brand": "Cadbury", "unit": "piece", "typical_price": 10, "shelf_life_days": 365, "is_perishable": False},
    {"name": "Pulse Candy (20 pcs)", "category": "Confectionery", "subcategory": "Candy", "brand": "Pulse", "unit": "packet", "typical_price": 40, "shelf_life_days": 365, "is_perishable": False},

    # Frozen / Ready to eat
    {"name": "Frozen Peas (500g)", "category": "Frozen Food", "subcategory": "Vegetables", "brand": "Safal", "unit": "packet", "typical_price": 65, "shelf_life_days": 180, "is_perishable": True},
    {"name": "Frozen Mixed Vegetables (500g)", "category": "Frozen Food", "subcategory": "Vegetables", "brand": "Safal", "unit": "packet", "typical_price": 75, "shelf_life_days": 180, "is_perishable": True},

    # Pooja Items
    {"name": "Agarbatti (20 sticks)", "category": "Pooja Items", "subcategory": "Incense", "brand": "Cycle", "unit": "packet", "typical_price": 25, "shelf_life_days": 730, "is_perishable": False},
    {"name": "Matchbox (10 pack)", "category": "Pooja Items", "subcategory": "Matchbox", "brand": "Ship", "unit": "bundle", "typical_price": 10, "shelf_life_days": 730, "is_perishable": False},

    # Baby Products
    {"name": "Cerelac (300g)", "category": "Baby Products", "subcategory": "Baby Food", "brand": "Nestle", "unit": "box", "typical_price": 215, "shelf_life_days": 365, "is_perishable": False},
    {"name": "Johnson's Baby Powder (100g)", "category": "Baby Products", "subcategory": "Powder", "brand": "Johnson's", "unit": "bottle", "typical_price": 80, "shelf_life_days": 730, "is_perishable": False},

    # Stationery (common in Kirana stores)
    {"name": "Classmate Notebook (180 pages)", "category": "Stationery", "subcategory": "Notebook", "brand": "Classmate", "unit": "piece", "typical_price": 45, "shelf_life_days": None, "is_perishable": False},
    {"name": "Reynolds Pen (5 pack)", "category": "Stationery", "subcategory": "Pen", "brand": "Reynolds", "unit": "packet", "typical_price": 50, "shelf_life_days": None, "is_perishable": False},
]

DISTRIBUTORS = [
    {"name": "Ram Distributors", "phone": "9876543210", "email": "ram@distributors.in", "address": "Nehru Place, Delhi", "city": "Delhi", "rating": 4.5, "categories": json.dumps(["Dairy", "Groceries", "Spices"])},
    {"name": "Sharma Wholesale", "phone": "9876543211", "email": "sharma@wholesale.in", "address": "Chandni Chowk, Delhi", "city": "Delhi", "rating": 4.2, "categories": json.dumps(["Beverages", "Snacks", "Confectionery"])},
    {"name": "Patel FMCG Supply", "phone": "9876543212", "email": "patel@fmcg.in", "address": "Karol Bagh, Delhi", "city": "Delhi", "rating": 4.7, "categories": json.dumps(["Personal Care", "Household", "Baby Products"])},
    {"name": "Delhi Fresh Traders", "phone": "9876543213", "email": "fresh@traders.in", "address": "Azadpur Mandi, Delhi", "city": "Delhi", "rating": 4.0, "categories": json.dumps(["Bakery", "Frozen Food", "Dairy"])},
    {"name": "Bharat Stationery Co.", "phone": "9876543214", "email": "bharat@stationery.in", "address": "Daryaganj, Delhi", "city": "Delhi", "rating": 4.3, "categories": json.dumps(["Stationery", "Pooja Items"])},
]


def seed_database(db: Session):
    """Seed the database with initial data."""
    # Check if already seeded
    if db.query(Product).count() > 0:
        return

    # Seed products
    products = []
    for p in PRODUCTS:
        product = Product(**p)
        db.add(product)
        products.append(product)
    db.flush()

    # Seed distributors
    distributors = []
    for d in DISTRIBUTORS:
        dist = Distributor(**d)
        db.add(dist)
        distributors.append(dist)
    db.flush()

    # Create a demo store
    store = Store(
        owner_name="Rajesh Kumar",
        phone_number="9999999999",
        store_name="Kumar General Store",
        address="123, Main Market, Connaught Place",
        city="New Delhi",
        state="Delhi",
        pincode="110001",
        latitude=28.6315,
        longitude=77.2167,
        subscription_tier="premium",
    )
    db.add(store)
    db.flush()

    # Create inventory items for the store
    random.seed(42)
    for product in products:
        qty = random.randint(5, 200)
        reorder = random.randint(10, 30)
        optimal = random.randint(50, 150)
        inv = InventoryItem(
            store_id=store.id,
            product_id=product.id,
            current_quantity=qty,
            reorder_point=reorder,
            optimal_quantity=optimal,
        )
        db.add(inv)
    db.flush()

    # Create historical transactions (last 30 days)
    for day_offset in range(30, 0, -1):
        date = datetime.utcnow() - timedelta(days=day_offset)

        # 2-5 purchases per day
        num_purchases = random.randint(1, 3)
        for _ in range(num_purchases):
            tx = Transaction(
                store_id=store.id,
                transaction_type="purchase",
                transaction_date=date,
                total_amount=0,
                source="whatsapp",
            )
            db.add(tx)
            db.flush()

            total = 0
            num_items = random.randint(2, 6)
            chosen = random.sample(products, min(num_items, len(products)))
            for prod in chosen:
                qty = random.randint(5, 50)
                price = prod.typical_price * random.uniform(0.9, 1.1)
                ti = TransactionItem(
                    transaction_id=tx.id,
                    product_id=prod.id,
                    quantity=qty,
                    unit_price=round(price, 2),
                    total_price=round(qty * price, 2),
                )
                total += ti.total_price
                db.add(ti)
            tx.total_amount = round(total, 2)

        # 3-8 sales per day
        num_sales = random.randint(3, 8)
        for _ in range(num_sales):
            tx = Transaction(
                store_id=store.id,
                transaction_type="sale",
                transaction_date=date,
                total_amount=0,
                source="manual",
            )
            db.add(tx)
            db.flush()

            total = 0
            num_items = random.randint(1, 5)
            chosen = random.sample(products, min(num_items, len(products)))
            for prod in chosen:
                qty = random.randint(1, 15)
                price = prod.typical_price * random.uniform(1.0, 1.3)
                ti = TransactionItem(
                    transaction_id=tx.id,
                    product_id=prod.id,
                    quantity=qty,
                    unit_price=round(price, 2),
                    total_price=round(qty * price, 2),
                )
                total += ti.total_price
                db.add(ti)
            tx.total_amount = round(total, 2)

    # Create predictions for next 7 days
    for day_offset in range(1, 8):
        forecast_date = datetime.utcnow() + timedelta(days=day_offset)
        for product in products[:20]:  # top 20 products
            pred = Prediction(
                store_id=store.id,
                product_id=product.id,
                forecast_date=forecast_date,
                predicted_quantity=round(random.uniform(3, 40), 1),
                confidence=round(random.uniform(0.7, 0.95), 2),
                factors=json.dumps({
                    "seasonal": round(random.uniform(-0.1, 0.2), 3),
                    "trend": round(random.uniform(-0.05, 0.15), 3),
                    "weather_impact": round(random.uniform(-0.1, 0.1), 3),
                    "festival_effect": round(random.uniform(0, 0.3), 3),
                }),
            )
            db.add(pred)

    # Create sample orders
    for i in range(5):
        dist = random.choice(distributors)
        statuses = ["suggested", "placed", "confirmed", "dispatched", "delivered"]
        order = Order(
            store_id=store.id,
            distributor_id=dist.id,
            status=statuses[i],
            placed_at=datetime.utcnow() - timedelta(days=random.randint(1, 10)) if i > 0 else None,
            delivered_at=datetime.utcnow() - timedelta(days=1) if i == 4 else None,
            total_amount=0,
        )
        db.add(order)
        db.flush()

        total = 0
        num_items = random.randint(3, 8)
        chosen = random.sample(products, min(num_items, len(products)))
        for prod in chosen:
            qty = random.randint(10, 100)
            oi = OrderItem(
                order_id=order.id,
                product_id=prod.id,
                quantity=qty,
                unit_price=prod.typical_price,
            )
            total += qty * prod.typical_price
            db.add(oi)
        order.total_amount = round(total, 2)

    db.commit()
    print("✅ Database seeded successfully!")
