from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text
)
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class Store(Base):
    __tablename__ = "stores"

    id = Column(Integer, primary_key=True, index=True)
    owner_name = Column(String(100), nullable=False)
    phone_number = Column(String(15), unique=True, nullable=False)
    store_name = Column(String(200), nullable=False)
    address = Column(String(500))
    city = Column(String(100))
    state = Column(String(100))
    pincode = Column(String(10))
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    subscription_tier = Column(String(20), default="free")

    inventory_items = relationship("InventoryItem", back_populates="store", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="store", cascade="all, delete-orphan")
    predictions = relationship("Prediction", back_populates="store", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="store", cascade="all, delete-orphan")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    category = Column(String(100), nullable=False)
    subcategory = Column(String(100))
    brand = Column(String(100))
    unit = Column(String(20), nullable=False)
    barcode = Column(String(50), unique=True, nullable=True)
    typical_price = Column(Float, default=0)
    shelf_life_days = Column(Integer, nullable=True)
    is_perishable = Column(Boolean, default=False)

    inventory_items = relationship("InventoryItem", back_populates="product")


class InventoryItem(Base):
    __tablename__ = "inventory_items"

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    current_quantity = Column(Float, default=0)
    reorder_point = Column(Float, default=10)
    optimal_quantity = Column(Float, default=50)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    store = relationship("Store", back_populates="inventory_items")
    product = relationship("Product", back_populates="inventory_items")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    transaction_type = Column(String(20), nullable=False)  # purchase, sale, adjustment
    transaction_date = Column(DateTime, default=datetime.utcnow)
    total_amount = Column(Float, default=0)
    source = Column(String(50), default="manual")  # whatsapp, manual, pos

    store = relationship("Store", back_populates="transactions")
    items = relationship("TransactionItem", back_populates="transaction", cascade="all, delete-orphan")


class TransactionItem(Base):
    __tablename__ = "transaction_items"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Float, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)

    transaction = relationship("Transaction", back_populates="items")
    product = relationship("Product")


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    forecast_date = Column(DateTime, nullable=False)
    predicted_quantity = Column(Float, nullable=False)
    confidence = Column(Float, default=0.8)
    factors = Column(Text, nullable=True)  # JSON string of factors
    created_at = Column(DateTime, default=datetime.utcnow)

    store = relationship("Store", back_populates="predictions")
    product = relationship("Product")


class Distributor(Base):
    __tablename__ = "distributors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    phone = Column(String(15))
    email = Column(String(200))
    address = Column(String(500))
    city = Column(String(100))
    rating = Column(Float, default=4.0)
    categories = Column(Text)  # JSON list of categories served

    orders = relationship("Order", back_populates="distributor")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    distributor_id = Column(Integer, ForeignKey("distributors.id"), nullable=False)
    status = Column(String(30), default="suggested")  # suggested, placed, confirmed, dispatched, delivered, cancelled
    placed_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    total_amount = Column(Float, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    store = relationship("Store", back_populates="orders")
    distributor = relationship("Distributor", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Float, nullable=False)
    unit_price = Column(Float, nullable=False)

    order = relationship("Order", back_populates="items")
    product = relationship("Product")
