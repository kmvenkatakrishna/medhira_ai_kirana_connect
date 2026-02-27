import urllib.request
import json
import random
from datetime import datetime
import time

BASE_URL = "http://localhost:8000/api/v1"
STORE_ID = "test-store-123"

def send_post(endpoint, data):
    url = f"{BASE_URL}{endpoint}"
    req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'}, method='POST')
    try:
        response = urllib.request.urlopen(req)
        return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"Error calling {url}: {e}")
        return None

def generate_inventory():
    print("Generating synthetic inventory data...")
    products = [
        {"name": "Amul Milk 500ml", "category": "Dairy", "unit_price": 28.0, "unit": "packet"},
        {"name": "Aashirvaad Atta 5kg", "category": "Grocery", "unit_price": 250.0, "unit": "bag"},
        {"name": "Tata Salt 1kg", "category": "Grocery", "unit_price": 25.0, "unit": "packet"},
        {"name": "Maggi Noodles 140g", "category": "Snacks", "unit_price": 24.0, "unit": "packet"},
        {"name": "Parle G 200g", "category": "Snacks", "unit_price": 20.0, "unit": "packet"},
        {"name": "Fortune Sunflower Oil 1L", "category": "Grocery", "unit_price": 145.0, "unit": "bottle"},
        {"name": "Dabur Honey 500g", "category": "Grocery", "unit_price": 180.0, "unit": "bottle"},
        {"name": "Lifebuoy Soap 100g", "category": "Personal Care", "unit_price": 25.0, "unit": "bar"},
        {"name": "Colgate Toothpaste 100g", "category": "Personal Care", "unit_price": 55.0, "unit": "tube"},
        {"name": "Red Label Tea 250g", "category": "Beverages", "unit_price": 140.0, "unit": "packet"}
    ]

    for p in products:
        d = p.copy()
        # Ensure we have out of stock and low stock
        if d["name"] == "Tata Salt 1kg":
            d["quantity"] = 0
            d["min_threshold"] = 5
        elif d["name"] == "Amul Milk 500ml":
            d["quantity"] = 3
            d["min_threshold"] = 10
        else:
            d["quantity"] = random.randint(5, 50)
            d["min_threshold"] = random.randint(5, 15)
        
        endpoint = f"/stores/{STORE_ID}/inventory/"
        send_post(endpoint, d)
        time.sleep(0.1)
    print("Inventory data generated.")

def generate_chat_history():
    print("Generating synthetic chat history...")
    messages = [
        "Bought 50 Amul Milk 500ml",
        "Check stock",
        "Bought 10 Tata Salt 1kg",
        "Add 20 Maggi Noodles 140g"
    ]
    
    for msg in messages:
        payload = {
            "store_id": STORE_ID,
            "sender": "user",
            "text": msg
        }
        send_post("/whatsapp/message", payload)
        time.sleep(0.5)
    print("Chat history generated.")

if __name__ == "__main__":
    generate_inventory()
    generate_chat_history()
    print("Synthetic data generation complete. You can now refresh the dashboard.")
