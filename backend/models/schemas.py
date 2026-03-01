from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


# ── Store ──
class Store(BaseModel):
    store_id: str
    owner_name: str
    phone_number: str
    store_name: str
    address: str
    city: str
    state: str
    pincode: str
    latitude: float = 0.0
    longitude: float = 0.0
    subscription_tier: str = "free"
    created_at: str = ""


# ── Product ──
class Product(BaseModel):
    product_id: str
    name: str
    category: str
    subcategory: str = ""
    brand: str = ""
    unit: str = "piece"
    barcode: Optional[str] = None
    typical_price: float = 0.0
    shelf_life_days: Optional[int] = None
    is_perishable: bool = False


# ── Inventory Item ──
class InventoryItem(BaseModel):
    inventory_id: str
    store_id: str
    product_id: str
    product_name: str = ""
    category: str = ""
    current_quantity: float = 0
    reorder_point: float = 10
    optimal_quantity: float = 50
    unit: str = "piece"
    unit_price: float = 0.0
    last_updated: str = ""


# ── Transaction ──
class TransactionItem(BaseModel):
    product_id: str
    product_name: str = ""
    quantity: float
    unit_price: float
    total_price: float = 0.0


class Transaction(BaseModel):
    transaction_id: str
    store_id: str
    transaction_type: str  # purchase, sale, adjustment
    transaction_date: str
    total_amount: float = 0.0
    source: str = "manual"
    items: List[TransactionItem] = []


# ── Prediction ──
class PredictionDay(BaseModel):
    date: str
    predicted_quantity: float
    confidence_low: float
    confidence_high: float


class Prediction(BaseModel):
    prediction_id: str
    store_id: str
    product_id: str
    product_name: str = ""
    category: str = ""
    predictions: List[PredictionDay] = []
    model_confidence: float = 0.0
    factors: dict = {}
    created_at: str = ""


# ── Distributor ──
class Distributor(BaseModel):
    distributor_id: str
    name: str
    phone: str
    email: str = ""
    address: str = ""
    city: str = ""
    rating: float = 4.0
    categories: List[str] = []


# ── Order ──
class OrderItem(BaseModel):
    product_id: str
    product_name: str = ""
    quantity: float
    unit_price: float
    total_price: float = 0.0


class Order(BaseModel):
    order_id: str
    store_id: str
    distributor_id: str
    distributor_name: str = ""
    status: str = "pending"  # pending, confirmed, shipped, delivered, cancelled
    placed_at: str = ""
    expected_delivery: str = ""
    delivered_at: Optional[str] = None
    total_amount: float = 0.0
    items: List[OrderItem] = []


# ── Chat ──
class ChatMessage(BaseModel):
    message: str
    sender: str = "user"  # user or bot


class ChatResponse(BaseModel):
    response: str
    intent: str = ""
    entities: dict = {}
    suggestions: List[str] = []


# ── Analytics ──
class DailySalesReport(BaseModel):
    date: str
    total_sales: float
    total_transactions: int
    top_products: List[dict] = []
    low_stock_items: List[dict] = []


class AnalyticsSummary(BaseModel):
    total_revenue: float = 0.0
    total_transactions: int = 0
    avg_daily_sales: float = 0.0
    top_categories: List[dict] = []
    sales_trend: List[dict] = []
    inventory_value: float = 0.0
    low_stock_count: int = 0
    overstock_count: int = 0
