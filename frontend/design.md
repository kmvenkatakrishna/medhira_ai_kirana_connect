# Kirana-Connect: Inventory AI Agent - Design Document

## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture Design](#architecture-design)
3. [Component Design](#component-design)
4. [Data Model](#data-model)
5. [API Design](#api-design)
6. [AI/ML Model Design](#aiml-model-design)
7. [User Interface Design](#user-interface-design)
8. [Integration Design](#integration-design)
9. [Security Design](#security-design)
10. [Deployment Architecture](#deployment-architecture)

---

## System Overview

### Architecture Philosophy
Kirana-Connect follows a **microservices architecture** with event-driven communication, designed for:
- **Scalability**: Handle millions of users with elastic scaling
- **Reliability**: Fault-tolerant with graceful degradation
- **Maintainability**: Loosely coupled services for independent deployment
- **Cost Efficiency**: Serverless components where appropriate

### Technology Stack

#### Backend Services
- **Primary Language**: Python 3.11+ (FastAPI for APIs)
- **ML/AI Framework**: TensorFlow, scikit-learn, Prophet
- **Message Queue**: Apache Kafka / AWS SQS
- **Cache**: Redis (session management, prediction caching)
- **Search**: Elasticsearch (product catalog)

#### Data Storage
- **Primary Database**: PostgreSQL 15+ (transactional data)
- **Time-Series DB**: TimescaleDB (sales history, metrics)
- **Document Store**: MongoDB (unstructured data, logs)
- **Object Storage**: AWS S3 / GCP Cloud Storage (images, audio files)

#### Communication Layer
- **WhatsApp**: WhatsApp Business API (official API partner)
- **SMS Gateway**: Twilio / MSG91 (backup channel)
- **Email**: SendGrid (reports, notifications)

#### Infrastructure
- **Cloud Provider**: AWS (primary) with multi-region deployment
- **Container Orchestration**: Kubernetes (EKS)
- **CI/CD**: GitLab CI / GitHub Actions
- **Monitoring**: Prometheus + Grafana, ELK stack

---

## Architecture Design

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Layer                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │WhatsApp  │  │  Voice   │  │  Image   │  │   Text   │       │
│  │ Messages │  │  Notes   │  │  Upload  │  │ Messages │       │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘       │
└───────┼─────────────┼─────────────┼─────────────┼──────────────┘
        │             │             │             │
        └─────────────┴─────────────┴─────────────┘
                          │
        ┌─────────────────▼─────────────────┐
        │    API Gateway / Load Balancer    │
        │         (Kong / AWS ALB)          │
        └─────────────────┬─────────────────┘
                          │
        ┌─────────────────▼─────────────────┐
        │   WhatsApp Integration Service    │
        │    - Message routing              │
        │    - Session management           │
        │    - Media handling               │
        └─────────────────┬─────────────────┘
                          │
        ┌─────────────────▼─────────────────┐
        │      Message Processing Layer      │
        │                                    │
        │  ┌──────────┐  ┌──────────┐      │
        │  │   NLP    │  │   OCR    │      │
        │  │  Engine  │  │  Engine  │      │
        │  └────┬─────┘  └────┬─────┘      │
        │       │             │             │
        │  ┌────▼─────────────▼─────┐      │
        │  │  Data Extraction Svc   │      │
        │  └────────────┬────────────┘      │
        └───────────────┼───────────────────┘
                        │
        ┌───────────────▼───────────────┐
        │      Core Business Layer      │
        │                                │
        │  ┌────────────────────────┐   │
        │  │  Inventory Service     │   │
        │  │  - Stock tracking      │   │
        │  │  - Product catalog     │   │
        │  └──────────┬─────────────┘   │
        │             │                  │
        │  ┌──────────▼─────────────┐   │
        │  │  Prediction Service    │   │
        │  │  - Demand forecasting  │   │
        │  │  - ML model inference  │   │
        │  └──────────┬─────────────┘   │
        │             │                  │
        │  ┌──────────▼─────────────┐   │
        │  │  Order Service         │   │
        │  │  - Order generation    │   │
        │  │  - Distributor mgmt    │   │
        │  └──────────┬─────────────┘   │
        │             │                  │
        │  ┌──────────▼─────────────┐   │
        │  │  Analytics Service     │   │
        │  │  - Reports generation  │   │
        │  │  - Insights            │   │
        │  └────────────────────────┘   │
        └────────────────────────────────┘
                        │
        ┌───────────────▼───────────────┐
        │      Data & ML Layer          │
        │                                │
        │  ┌─────────┐  ┌──────────┐   │
        │  │   DB    │  │ML Models │   │
        │  │Cluster  │  │ Storage  │   │
        │  └─────────┘  └──────────┘   │
        └────────────────────────────────┘
                        │
        ┌───────────────▼───────────────┐
        │   External Integrations       │
        │                                │
        │  ┌──────┐ ┌────────┐ ┌─────┐ │
        │  │Weather│ │Festival│ │Maps │ │
        │  │  API  │ │  Data  │ │ API │ │
        │  └──────┘ └────────┘ └─────┘ │
        └────────────────────────────────┘
```

### Service Interaction Patterns

#### 1. Message Flow (User Input)
```
User → WhatsApp → Webhook → API Gateway → Session Manager
  → Message Queue (Kafka) → Processor Service → NLP/OCR Engine
  → Data Extraction → Inventory Service → Response Generation
  → WhatsApp API → User
```

#### 2. Prediction Flow (Daily Forecast)
```
Scheduler (Cron) → Prediction Service → Inventory Service (get data)
  → External APIs (weather, festivals) → ML Model Inference
  → Cache Results (Redis) → Inventory Service (update forecasts)
  → Notification Service → WhatsApp API → User
```

#### 3. Order Flow (Automated Ordering)
```
Prediction Service (low stock alert) → Order Service
  → Distributor Service (check availability) → Order Optimization
  → User Confirmation (WhatsApp) → Distributor Portal
  → Order Tracking → Status Updates → User
```

---

## Component Design

### 1. WhatsApp Integration Service

**Responsibilities**:
- Handle incoming/outgoing WhatsApp messages
- Manage media uploads (images, audio)
- Session management (user context)
- Rate limiting and quota management

**Key Classes**:
```python
class WhatsAppClient:
    """Main client for WhatsApp Business API"""
    
    def __init__(self, api_key: str, phone_number_id: str):
        self.api_key = api_key
        self.phone_number_id = phone_number_id
        self.base_url = "https://graph.facebook.com/v18.0"
    
    async def send_text_message(self, to: str, message: str) -> dict:
        """Send text message to user"""
        pass
    
    async def send_template_message(self, to: str, template_name: str, 
                                   parameters: dict) -> dict:
        """Send template-based message (pre-approved)"""
        pass
    
    async def download_media(self, media_id: str) -> bytes:
        """Download media file from WhatsApp servers"""
        pass
    
    async def send_interactive_message(self, to: str, 
                                      message_type: str, 
                                      options: list) -> dict:
        """Send interactive buttons/lists"""
        pass

class WebhookHandler:
    """Handle incoming webhook events from WhatsApp"""
    
    async def handle_message(self, payload: dict):
        """Process incoming message"""
        message_type = payload.get('type')
        
        if message_type == 'text':
            await self._handle_text(payload)
        elif message_type == 'image':
            await self._handle_image(payload)
        elif message_type == 'audio':
            await self._handle_audio(payload)
        elif message_type == 'interactive':
            await self._handle_interactive(payload)
    
    async def handle_status_update(self, payload: dict):
        """Handle delivery/read receipts"""
        pass
```

**API Endpoints**:
- `POST /webhook/whatsapp` - Receive messages from WhatsApp
- `GET /webhook/whatsapp` - Verification endpoint
- `POST /api/v1/send-message` - Internal API to send messages
- `GET /api/v1/media/{media_id}` - Retrieve media files

### 2. NLP/OCR Processing Service

**Responsibilities**:
- Extract text from images (OCR)
- Transcribe voice notes to text
- Parse and understand user intent
- Extract entities (products, quantities, dates)

**Key Components**:

```python
class OCRProcessor:
    """Extract text from images"""
    
    def __init__(self):
        self.tesseract_engine = pytesseract
        self.easy_ocr_engine = easyocr.Reader(['en', 'hi'])
    
    async def process_image(self, image_bytes: bytes) -> dict:
        """
        Returns: {
            'text': str,
            'confidence': float,
            'language': str,
            'structured_data': dict
        }
        """
        # Preprocess image
        img = self._preprocess(image_bytes)
        
        # Run OCR
        text = self.easy_ocr_engine.readtext(img)
        
        # Post-process and structure
        structured = self._extract_invoice_data(text)
        
        return {
            'text': text,
            'structured_data': structured,
            'confidence': self._calculate_confidence(text)
        }
    
    def _preprocess(self, image_bytes: bytes) -> np.ndarray:
        """Image preprocessing for better OCR"""
        # Convert to grayscale
        # Denoise
        # Enhance contrast
        # Deskew if needed
        pass

class VoiceProcessor:
    """Transcribe voice notes"""
    
    def __init__(self):
        self.whisper_model = whisper.load_model("base")
        self.language_detector = LanguageDetector()
    
    async def transcribe(self, audio_bytes: bytes) -> dict:
        """
        Returns: {
            'text': str,
            'language': str,
            'confidence': float
        }
        """
        # Detect language
        lang = self.language_detector.detect(audio_bytes)
        
        # Transcribe
        result = self.whisper_model.transcribe(
            audio_bytes, 
            language=lang
        )
        
        return {
            'text': result['text'],
            'language': lang,
            'confidence': result.get('confidence', 0.8)
        }

class IntentClassifier:
    """Understand user intent from text"""
    
    INTENTS = [
        'add_purchase',
        'check_inventory',
        'get_forecast',
        'place_order',
        'get_report',
        'ask_question'
    ]
    
    def __init__(self):
        self.model = self._load_model()
    
    async def classify(self, text: str) -> dict:
        """
        Returns: {
            'intent': str,
            'confidence': float,
            'entities': dict
        }
        """
        # Clean text
        cleaned = self._clean_text(text)
        
        # Extract entities
        entities = self._extract_entities(cleaned)
        
        # Classify intent
        intent, confidence = self.model.predict(cleaned)
        
        return {
            'intent': intent,
            'confidence': confidence,
            'entities': entities
        }
    
    def _extract_entities(self, text: str) -> dict:
        """Extract products, quantities, dates, prices"""
        entities = {
            'products': [],
            'quantities': [],
            'dates': [],
            'prices': []
        }
        
        # Use NER model or regex patterns
        # Example: "Bought 100 milk packets for 5000 rupees"
        # → products: ['milk packets']
        # → quantities: [100]
        # → prices: [5000]
        
        return entities
```

### 3. Inventory Management Service

**Responsibilities**:
- Track stock levels in real-time
- Manage product catalog
- Record sales and purchases
- Calculate metrics (turnover, velocity)

**Data Models**:

```python
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship

class Store(Base):
    __tablename__ = 'stores'
    
    id = Column(Integer, primary_key=True)
    owner_name = Column(String(100))
    phone_number = Column(String(15), unique=True)
    store_name = Column(String(200))
    address = Column(String(500))
    city = Column(String(100))
    state = Column(String(100))
    pincode = Column(String(10))
    latitude = Column(Float)
    longitude = Column(Float)
    created_at = Column(DateTime)
    subscription_tier = Column(String(20))  # free, basic, premium
    
    inventory_items = relationship("InventoryItem", back_populates="store")
    transactions = relationship("Transaction", back_populates="store")

class Product(Base):
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200))
    category = Column(String(100))
    subcategory = Column(String(100))
    brand = Column(String(100))
    unit = Column(String(20))  # kg, liter, packet, piece
    barcode = Column(String(50), unique=True, nullable=True)
    typical_price = Column(Float)
    shelf_life_days = Column(Integer, nullable=True)
    is_perishable = Column(Boolean, default=False)
    
    inventory_items = relationship("InventoryItem", back_populates="product")

class InventoryItem(Base):
    __tablename__ = 'inventory_items'
    
    id = Column(Integer, primary_key=True)
    store_id = Column(Integer, ForeignKey('stores.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    current_quantity = Column(Float, default=0)
    reorder_point = Column(Float)  # Alert when stock falls below this
    optimal_quantity = Column(Float)  # Target stock level
    last_updated = Column(DateTime)
    
    store = relationship("Store", back_populates="inventory_items")
    product = relationship("Product", back_populates="inventory_items")

class Transaction(Base):
    __tablename__ = 'transactions'
    
    id = Column(Integer, primary_key=True)
    store_id = Column(Integer, ForeignKey('stores.id'))
    transaction_type = Column(String(20))  # purchase, sale, adjustment
    transaction_date = Column(DateTime)
    total_amount = Column(Float)
    source = Column(String(50))  # whatsapp, manual, pos
    
    store = relationship("Store", back_populates="transactions")
    items = relationship("TransactionItem", back_populates="transaction")

class TransactionItem(Base):
    __tablename__ = 'transaction_items'
    
    id = Column(Integer, primary_key=True)
    transaction_id = Column(Integer, ForeignKey('transactions.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity = Column(Float)
    unit_price = Column(Float)
    total_price = Column(Float)
    
    transaction = relationship("Transaction", back_populates="items")
    product = relationship("Product")
```

**Service APIs**:

```python
class InventoryService:
    """Core inventory management logic"""
    
    async def add_purchase(self, store_id: int, items: List[dict]) -> Transaction:
        """Record a purchase transaction"""
        transaction = Transaction(
            store_id=store_id,
            transaction_type='purchase',
            transaction_date=datetime.now()
        )
        
        for item in items:
            product = await self._get_or_create_product(item)
            
            # Update inventory
            inventory_item = await self._get_inventory_item(
                store_id, product.id
            )
            inventory_item.current_quantity += item['quantity']
            
            # Record transaction
            transaction_item = TransactionItem(
                product_id=product.id,
                quantity=item['quantity'],
                unit_price=item['price'],
                total_price=item['quantity'] * item['price']
            )
            transaction.items.append(transaction_item)
        
        await self.db.commit()
        return transaction
    
    async def get_current_stock(self, store_id: int, 
                               product_id: int = None) -> List[dict]:
        """Get current stock levels"""
        query = self.db.query(InventoryItem).filter(
            InventoryItem.store_id == store_id
        )
        
        if product_id:
            query = query.filter(InventoryItem.product_id == product_id)
        
        items = await query.all()
        return [self._serialize_inventory_item(item) for item in items]
    
    async def check_low_stock_alerts(self, store_id: int) -> List[dict]:
        """Find items that need reordering"""
        low_stock = await self.db.query(InventoryItem).filter(
            InventoryItem.store_id == store_id,
            InventoryItem.current_quantity <= InventoryItem.reorder_point
        ).all()
        
        return [self._serialize_inventory_item(item) for item in low_stock]
    
    async def calculate_sales_velocity(self, store_id: int, 
                                      product_id: int, 
                                      days: int = 7) -> float:
        """Calculate average daily sales for a product"""
        start_date = datetime.now() - timedelta(days=days)
        
        sales = await self.db.query(
            func.sum(TransactionItem.quantity)
        ).join(Transaction).filter(
            Transaction.store_id == store_id,
            TransactionItem.product_id == product_id,
            Transaction.transaction_type == 'sale',
            Transaction.transaction_date >= start_date
        ).scalar()
        
        return (sales or 0) / days
```

### 4. Prediction Service (ML Engine)

**Responsibilities**:
- Forecast demand for next 7-30 days
- Consider seasonality, trends, external factors
- Continuously learn and improve predictions
- Cache predictions for fast retrieval

**ML Model Architecture**:

```python
class DemandForecaster:
    """Multi-model ensemble for demand prediction"""
    
    def __init__(self):
        self.prophet_model = Prophet()
        self.arima_model = ARIMA()
        self.lstm_model = LSTMForecaster()
        self.xgboost_model = XGBRegressor()
        
        # Feature engineering components
        self.feature_engineer = FeatureEngineer()
        self.external_data_fetcher = ExternalDataFetcher()
    
    async def predict_demand(self, store_id: int, product_id: int, 
                            forecast_days: int = 7) -> dict:
        """
        Returns: {
            'product_id': int,
            'predictions': [
                {'date': str, 'quantity': float, 'confidence_low': float, 
                 'confidence_high': float}
            ],
            'model_confidence': float,
            'factors': dict  # What influenced the prediction
        }
        """
        # Get historical data
        historical_data = await self._get_historical_sales(
            store_id, product_id, days=90
        )
        
        # Fetch external data
        external_data = await self.external_data_fetcher.fetch(
            store_id, forecast_days
        )
        
        # Feature engineering
        features = self.feature_engineer.create_features(
            historical_data, external_data
        )
        
        # Run multiple models
        prophet_pred = self.prophet_model.predict(features)
        arima_pred = self.arima_model.predict(features)
        lstm_pred = self.lstm_model.predict(features)
        xgb_pred = self.xgboost_model.predict(features)
        
        # Ensemble (weighted average based on past accuracy)
        final_prediction = self._ensemble_predictions([
            (prophet_pred, 0.3),
            (arima_pred, 0.2),
            (lstm_pred, 0.3),
            (xgb_pred, 0.2)
        ])
        
        return {
            'product_id': product_id,
            'predictions': final_prediction,
            'model_confidence': self._calculate_confidence(historical_data),
            'factors': self._explain_prediction(features, final_prediction)
        }

class FeatureEngineer:
    """Create features for ML models"""
    
    def create_features(self, historical_data: pd.DataFrame, 
                       external_data: dict) -> pd.DataFrame:
        """
        Features:
        1. Time-based: day_of_week, week_of_month, month, is_weekend
        2. Lag features: sales_lag_1, sales_lag_7, sales_lag_30
        3. Rolling statistics: rolling_mean_7d, rolling_std_7d
        4. Trend: linear_trend, exponential_trend
        5. Seasonality: monthly_seasonality, festival_flag
        6. External: temperature, rainfall, is_festival, is_holiday
        7. Store-specific: avg_basket_size, customer_traffic
        """
        features = pd.DataFrame()
        
        # Time features
        features['day_of_week'] = historical_data['date'].dt.dayofweek
        features['week_of_month'] = historical_data['date'].dt.day // 7
        features['month'] = historical_data['date'].dt.month
        features['is_weekend'] = features['day_of_week'].isin([5, 6])
        
        # Lag features
        for lag in [1, 7, 14, 30]:
            features[f'sales_lag_{lag}'] = historical_data['quantity'].shift(lag)
        
        # Rolling features
        for window in [7, 14, 30]:
            features[f'rolling_mean_{window}d'] = (
                historical_data['quantity'].rolling(window).mean()
            )
            features[f'rolling_std_{window}d'] = (
                historical_data['quantity'].rolling(window).std()
            )
        
        # External features
        features['temperature'] = external_data.get('temperature', [])
        features['rainfall'] = external_data.get('rainfall', [])
        features['is_festival'] = external_data.get('is_festival', [])
        
        return features

class ExternalDataFetcher:
    """Fetch weather, festival, and other external data"""
    
    async def fetch(self, store_id: int, forecast_days: int) -> dict:
        """Fetch all external data sources"""
        store = await self._get_store(store_id)
        
        # Fetch weather data
        weather = await self._fetch_weather(
            store.latitude, store.longitude, forecast_days
        )
        
        # Fetch festival calendar
        festivals = await self._fetch_festivals(
            store.state, forecast_days
        )
        
        # Fetch economic calendar (payday, holidays)
        economic = await self._fetch_economic_calendar(forecast_days)
        
        return {
            'weather': weather,
            'festivals': festivals,
            'economic': economic
        }
    
    async def _fetch_weather(self, lat: float, lon: float, 
                            days: int) -> List[dict]:
        """Fetch weather forecast from OpenWeatherMap or similar"""
        # API call to weather service
        pass
    
    async def _fetch_festivals(self, state: str, days: int) -> List[dict]:
        """Get upcoming festivals from calendar"""
        # Query festival database
        pass
```

**Model Training Pipeline**:

```python
class ModelTrainer:
    """Retrain models periodically with new data"""
    
    async def train_store_models(self, store_id: int):
        """Train custom models for a specific store"""
        # Get all historical data
        data = await self._get_training_data(store_id)
        
        # Split into train/validation
        train, val = self._split_data(data, test_size=0.2)
        
        # Train models
        prophet_model = self._train_prophet(train)
        arima_model = self._train_arima(train)
        lstm_model = self._train_lstm(train)
        xgb_model = self._train_xgboost(train)
        
        # Evaluate on validation set
        metrics = self._evaluate_models(val, [
            prophet_model, arima_model, lstm_model, xgb_model
        ])
        
        # Save best models
        await self._save_models(store_id, {
            'prophet': prophet_model,
            'arima': arima_model,
            'lstm': lstm_model,
            'xgboost': xgb_model,
            'metrics': metrics
        })
    
    def _evaluate_models(self, validation_data: pd.DataFrame, 
                        models: List) -> dict:
        """Calculate MAE, RMSE, MAPE for each model"""
        metrics = {}
        
        for model_name, model in models:
            predictions = model.predict(validation_data)
            actual = validation_data['quantity']
            
            metrics[model_name] = {
                'mae': mean_absolute_error(actual, predictions),
                'rmse': np.sqrt(mean_squared_error(actual, predictions)),
                'mape': mean_absolute_percentage_error(actual, predictions)
            }
        
        return metrics
```

### 5. Order Management Service

**Responsibilities**:
- Generate optimal order recommendations
- Manage distributor relationships
- Track order status
- Handle confirmations and modifications

**Key Components**:

```python
class OrderGenerator:
    """Generate smart order recommendations"""
    
    async def generate_order(self, store_id: int) -> dict:
        """
        Returns: {
            'order_id': str,
            'items': [
                {
                    'product_id': int,
                    'product_name': str,
                    'current_stock': float,
                    'recommended_quantity': float,
                    'estimated_cost': float,
                    'reason': str  # Why this quantity
                }
            ],
            'total_cost': float,
            'distributor': str,
            'estimated_delivery': str
        }
        """
        # Get low stock items
        low_stock = await self.inventory_service.check_low_stock_alerts(store_id)
        
        # Get predictions for next 7 days
        order_items = []
        total_cost = 0
        
        for item in low_stock:
            prediction = await self.prediction_service.predict_demand(
                store_id, item['product_id'], forecast_days=7
            )
            
            # Calculate order quantity
            # Formula: (7-day forecast + safety stock) - current stock
            forecast_qty = sum(p['quantity'] for p in prediction['predictions'])
            safety_stock = forecast_qty * 0.2  # 20% buffer
            order_qty = forecast_qty + safety_stock - item['current_quantity']
            
            if order_qty > 0:
                order_items.append({
                    'product_id': item['product_id'],
                    'product_name': item['product_name'],
                    'current_stock': item['current_quantity'],
                    'recommended_quantity': order_qty,
                    'estimated_cost': order_qty * item['unit_price'],
                    'reason': self._generate_reason(prediction, item)
                })
                total_cost += order_qty * item['unit_price']
        
        return {
            'order_id': self._generate_order_id(),
            'items': order_items,
            'total_cost': total_cost,
            'distributor': await self._find_best_distributor(store_id, order_items),
            'estimated_delivery': self._estimate_delivery_date()
        }
    
    def _generate_reason(self, prediction: dict, item: dict) -> str:
        """Explain why this quantity is recommended"""
        factors = prediction['factors']
        
        reasons = []
        if factors.get('festival'):
            reasons.append(f"Upcoming festival: {factors['festival']['name']}")
        if factors.get('trend') == 'increasing':
            reasons.append("Sales trending up")
        if factors.get('weather_impact'):
            reasons.append("Weather-related demand increase")
        
        return " | ".join(reasons) or "Normal restock"

class DistributorService:
    """Manage distributor relationships and orders"""
    
    async def find_best_distributor(self, store_id: int, 
                                   items: List[dict]) -> dict:
        """Find distributor with best price and availability"""
        store = await self._get_store(store_id)
        
        # Get distributors in the area
        distributors = await self._get_nearby_distributors(
            store.latitude, store.longitude, radius_km=50
        )
        
        # Check availability and pricing
        quotes = []
        for distributor in distributors:
            quote = await self._get_quote(distributor, items)
            if quote['available']:
                quotes.append({
                    'distributor': distributor,
                    'total_price': quote['total_price'],
                    'delivery_time': quote['delivery_time'],
                    'rating': distributor.rating
                })
        
        # Select best option (balance price, delivery time, rating)
        best = sorted(quotes, key=lambda x: (
            x['total_price'] * 0.6 +  # 60% weight on price
            x['delivery_time'] * 0.2 +  # 20% weight on delivery time
            (5 - x['rating']) * 0.2  # 20% weight on rating (inverted)
        ))[0]
        
        return best['distributor']
    
    async def place_order(self, order_id: str, 
                         distributor_id: int) -> dict:
        """Place order with distributor"""
        order = await self._get_order(order_id)
        distributor = await self._get_distributor(distributor_id)
        
        # Send order to distributor (via WhatsApp, email, or API)
        if distributor.api_endpoint:
            response = await self._place_order_via_api(order, distributor)
        else:
            response = await self._place_order_via_whatsapp(order, distributor)
        
        # Update order status
        order.status = 'placed'
        order.placed_at = datetime.now()
        await self.db.commit()
        
        return response
```

---

## Data Model

### Entity Relationship Diagram

```
┌─────────────┐
│   Stores    │
├─────────────┤
│ id (PK)     │
│ owner_name  │
│ phone       │
│ address     │
│ city        │
│ state       │
│ pincode     │
│ lat/lon     │
└──────┬──────┘
       │
       │ 1:N
       ▼
┌─────────────────┐
│InventoryItems  │
├─────────────────┤
│ id (PK)         │
│ store_id (FK)   │
│ product_id (FK) │
│ current_qty     │
│ reorder_point   │
│ optimal_qty     │
└────────┬────────┘
         │
         │ N:1
         ▼
    ┌─────────────┐
    │  Products   │
    ├─────────────┤
    │ id (PK)     │
    │ name        │
    │ category    │
    │ brand       │
    │ unit        │
    │ price       │
    └─────────────┘

┌─────────────┐
│   Stores    │
└──────┬──────┘
       │
       │ 1:N
       ▼
┌──────────────────┐
│  Transactions    │
├──────────────────┤
│ id (PK)          │
│ store_id (FK)    │
│ type             │
│ date             │
│ total_amount     │
└────────┬─────────┘
         │
         │ 1:N
         ▼
┌────────────────────┐
│ TransactionItems  │
├────────────────────┤
│ id (PK)            │
│ transaction_id(FK) │
│ product_id (FK)    │
│ quantity           │
│ unit_price         │
│ total_price        │
└────────────────────┘

┌─────────────┐
│   Stores    │
└──────┬──────┘
       │
       │ 1:N
       ▼
┌─────────────────┐
│  Predictions    │
├─────────────────┤
│ id (PK)         │
│ store_id (FK)   │
│ product_id (FK) │
│ forecast_date   │
│ predicted_qty   │
│ confidence      │
│ created_at      │
└─────────────────┘

┌──────────────┐
│Distributors  │
├──────────────┤
│ id (PK)      │
│ name         │
│ phone        │
│ email        │
│ address      │
│ lat/lon      │
│ rating       │
│ api_endpoint │
└──────┬───────┘
       │
       │ 1:N
       ▼
┌──────────────────┐
│     Orders       │
├──────────────────┤
│ id (PK)          │
│ store_id (FK)    │
│ distributor_id(FK)│
│ status           │
│ placed_at        │
│ delivered_at     │
│ total_amount     │
└────────┬─────────┘
         │
         │ 1:N
         ▼
┌──────────────────┐
│   OrderItems     │
├──────────────────┤
│ id (PK)          │
│ order_id (FK)    │
│ product_id (FK)  │
│ quantity         │
│ unit_price       │
└──────────────────┘
```

---

## API Design

### REST API Endpoints

#### Authentication
```
POST /api/v1/auth/register
POST /api/v1/auth/verify-otp
POST /api/v1/auth/login
POST /api/v1/auth/refresh-token
```

#### Inventory Management
```
GET    /api/v1/stores/{store_id}/inventory
POST   /api/v1/stores/{store_id}/inventory/purchase
POST   /api/v1/stores/{store_id}/inventory/sale
GET    /api/v1/stores/{store_id}/inventory/low-stock
GET    /api/v1/stores/{store_id}/inventory/{product_id}
PUT    /api/v1/stores/{store_id}/inventory/{product_id}
DELETE /api/v1/stores/{store_id}/inventory/{product_id}
```

#### Predictions
```
GET  /api/v1/stores/{store_id}/predictions
GET  /api/v1/stores/{store_id}/predictions/{product_id}
POST /api/v1/stores/{store_id}/predictions/generate
```

#### Orders
```
GET    /api/v1/stores/{store_id}/orders
POST   /api/v1/stores/{store_id}/orders/generate
POST   /api/v1/stores/{store_id}/orders/{order_id}/place
PUT    /api/v1/stores/{store_id}/orders/{order_id}/confirm
GET    /api/v1/stores/{store_id}/orders/{order_id}/status
DELETE /api/v1/stores/{store_id}/orders/{order_id}
```

#### Analytics
```
GET /api/v1/stores/{store_id}/reports/daily
GET /api/v1/stores/{store_id}/reports/weekly
GET /api/v1/stores/{store_id}/reports/monthly
GET /api/v1/stores/{store_id}/analytics/sales-trends
GET /api/v1/stores/{store_id}/analytics/top-products
```

#### Products (Catalog)
```
GET   /api/v1/products
GET   /api/v1/products/{product_id}
GET   /api/v1/products/search?q={query}
GET   /api/v1/products/categories
```

---

## User Interface Design

### WhatsApp Conversation Flows

#### Flow 1: Onboarding
```
Bot: Welcome to Kirana-Connect! 👋 I'm your AI assistant for inventory management.

Bot: Let's get started! What's your store name?

User: Sharma General Store

Bot: Great! Where is your store located? (City/Area)

User: Connaught Place, Delhi

Bot: Perfect! Now I need your phone number for verification.
[Button: Share Contact]

User: [Shares contact]

Bot: OTP sent to your number. Please enter the OTP:

User: 123456

Bot: Verified! ✅ Your store is registered.

Bot: How would you like to add purchases?
1️⃣ Take photo of bill
2️⃣ Send voice note
3️⃣ Type manually

User: 1

Bot: Perfect! Whenever you make a purchase, just send me a photo of the bill. I'll handle the rest! 📸

Bot: Try it now - send a photo of a recent purchase bill.
```

#### Flow 2: Adding Purchase via Photo
```
User: [Sends photo of bill]

Bot: Got it! Processing your bill... ⏳

Bot: I found these items:
✅ Milk packets - 100 units - ₹5,000
✅ Bread - 50 units - ₹1,500
✅ Eggs (30 pack) - 20 units - ₹2,000

Total: ₹8,500

Is this correct?
[Button: Yes, add to inventory]
[Button: No, let me edit]

User: [Clicks "Yes"]

Bot: Inventory updated! ✅

Your current stock:
🥛 Milk: 250 packets
🍞 Bread: 80 loaves
🥚 Eggs: 45 packs
```

#### Flow 3: Getting Forecast
```
User: What should I order for next week?

Bot: Analyzing your data... 📊

Bot: Based on:
🎉 Raksha Bandhan on Aug 30
🌡️ Hot weather forecast
📈 Recent sales trends

Here's what I recommend:

High Priority (Low Stock):
🥛 Milk: Order 200 packets (₹10,000)
   Current: 50 | 7-day need: 180
   
⚠️ Bread: Order 100 loaves (₹3,000)
   Current: 20 | 7-day need: 90

Medium Priority:
🍫 Chocolates: Order 150 pcs (₹6,000)
   Festival demand expected ↑

Total order value: ₹19,000

[Button: Place Order]
[Button: Modify Order]
[Button: View Details]

User: [Clicks "Place Order"]

Bot: Order sent to Ram Distributors! 📦
Expected delivery: Tomorrow 10 AM

I'll notify you when it's dispatched.
```

#### Flow 4: Daily Summary
```
Bot: Good Morning! ☀️ Here's your daily summary:

📊 Yesterday's Sales:
₹12,500 (15 transactions)
Top seller: Milk packets (80 sold)

📦 Inventory Status:
✅ 85% items in good stock
⚠️ 3 items need reordering

💰 Profit margin: 12.8%

📈 Prediction for today:
Expected sales: ₹13,200
Peak hours: 6-8 PM

[Button: View Full Report]
[Button: Place Order]
[Button: Check Stock]
```

### Interactive Buttons & Lists

```python
# Example interactive messages for WhatsApp

# Single-select buttons
{
  "type": "button",
  "body": {
    "text": "How can I help you today?"
  },
  "action": {
    "buttons": [
      {"type": "reply", "reply": {"id": "add_purchase", "title": "Add Purchase"}},
      {"type": "reply", "reply": {"id": "check_stock", "title": "Check Stock"}},
      {"type": "reply", "reply": {"id": "get_forecast", "title": "Get Forecast"}}
    ]
  }
}

# List message (for product selection)
{
  "type": "list",
  "body": {
    "text": "Select a product to view details:"
  },
  "action": {
    "button": "View Products",
    "sections": [
      {
        "title": "Dairy",
        "rows": [
          {"id": "product_1", "title": "Milk (500ml)", "description": "₹25 per unit"},
          {"id": "product_2", "title": "Curd (200g)", "description": "₹20 per unit"}
        ]
      },
      {
        "title": "Groceries",
        "rows": [
          {"id": "product_3", "title": "Rice (1kg)", "description": "₹60 per unit"},
          {"id": "product_4", "title": "Wheat (1kg)", "description": "₹45 per unit"}
        ]
      }
    ]
  }
}
```

---

## Integration Design

### External API Integrations

#### 1. Weather API
```python
class WeatherService:
    """OpenWeatherMap integration"""
    
    BASE_URL = "https://api.openweathermap.org/data/2.5"
    
    async def get_forecast(self, lat: float, lon: float, 
                          days: int = 7) -> List[dict]:
        """Get weather forecast for location"""
        url = f"{self.BASE_URL}/forecast"
        params = {
            'lat': lat,
            'lon': lon,
            'appid': self.api_key,
            'units': 'metric'
        }
        
        response = await self.http_client.get(url, params=params)
        data = response.json()
        
        return self._parse_forecast(data, days)
```

#### 2. Festival Calendar API
```python
class FestivalService:
    """Indian festival calendar"""
    
    FESTIVALS = {
        'diwali': {'month': 10, 'impact': 'high', 'categories': ['sweets', 'snacks']},
        'holi': {'month': 3, 'impact': 'high', 'categories': ['colors', 'sweets']},
        'raksha_bandhan': {'month': 8, 'impact': 'medium', 'categories': ['sweets', 'gifts']},
        # ... more festivals
    }
    
    async def get_upcoming_festivals(self, state: str, 
                                    days: int = 30) -> List[dict]:
        """Get festivals in next N days"""
        today = date.today()
        end_date = today + timedelta(days=days)
        
        upcoming = []
        for festival, info in self.FESTIVALS.items():
            festival_date = self._calculate_festival_date(
                festival, today.year
            )
            
            if today <= festival_date <= end_date:
                upcoming.append({
                    'name': festival,
                    'date': festival_date,
                    'impact': info['impact'],
                    'categories': info['categories']
                })
        
        return upcoming
```

#### 3. Payment Gateway
```python
class PaymentService:
    """Razorpay integration for subscriptions"""
    
    async def create_subscription(self, store_id: int, 
                                 plan: str) -> dict:
        """Create subscription for store"""
        customer = await self._create_customer(store_id)
        
        subscription = await self.razorpay_client.subscription.create({
            'plan_id': self.PLANS[plan],
            'customer_id': customer['id'],
            'total_count': 12,  # 12 months
            'notify_info': {
                'notify_phone': customer['phone'],
                'notify_email': customer['email']
            }
        })
        
        return subscription
```

---

## Security Design

### Authentication & Authorization

```python
class AuthService:
    """JWT-based authentication"""
    
    async def register_store(self, phone: str, store_data: dict) -> dict:
        """Register new store"""
        # Send OTP
        otp = self._generate_otp()
        await self.sms_service.send_otp(phone, otp)
        
        # Store OTP temporarily
        await self.redis.setex(f"otp:{phone}", 300, otp)
        
        return {'message': 'OTP sent', 'expires_in': 300}
    
    async def verify_otp(self, phone: str, otp: str) -> dict:
        """Verify OTP and create account"""
        stored_otp = await self.redis.get(f"otp:{phone}")
        
        if stored_otp != otp:
            raise InvalidOTPError()
        
        # Create store
        store = await self._create_store(phone, store_data)
        
        # Generate tokens
        access_token = self._generate_jwt(store.id, expires_in=3600)
        refresh_token = self._generate_jwt(store.id, expires_in=86400*30)
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'store_id': store.id
        }
    
    def _generate_jwt(self, store_id: int, expires_in: int) -> str:
        """Generate JWT token"""
        payload = {
            'store_id': store_id,
            'exp': datetime.now() + timedelta(seconds=expires_in),
            'iat': datetime.now()
        }
        
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
```

### Data Encryption

```python
class EncryptionService:
    """Encrypt sensitive data"""
    
    def __init__(self):
        self.cipher = Fernet(settings.ENCRYPTION_KEY)
    
    def encrypt(self, data: str) -> str:
        """Encrypt string data"""
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt string data"""
        return self.cipher.decrypt(encrypted_data.encode()).decode()

# Use for sensitive fields
class Store(Base):
    # ...
    phone_encrypted = Column(String(200))
    
    @property
    def phone(self):
        return encryption_service.decrypt(self.phone_encrypted)
    
    @phone.setter
    def phone(self, value):
        self.phone_encrypted = encryption_service.encrypt(value)
```

---

## Deployment Architecture

### Kubernetes Deployment

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: inventory-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: inventory-service
  template:
    metadata:
      labels:
        app: inventory-service
    spec:
      containers:
      - name: inventory-service
        image: kirana-connect/inventory-service:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secrets
              key: url
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5

---
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: inventory-service
spec:
  selector:
    app: inventory-service
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

### Infrastructure as Code (Terraform)

```hcl
# main.tf
provider "aws" {
  region = "ap-south-1"  # Mumbai
}

# EKS Cluster
module "eks" {
  source = "terraform-aws-modules/eks/aws"
  
  cluster_name    = "kirana-connect-prod"
  cluster_version = "1.28"
  
  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets
  
  node_groups = {
    general = {
      desired_capacity = 3
      max_capacity     = 10
      min_capacity     = 2
      
      instance_types = ["t3.large"]
    }
  }
}

# RDS PostgreSQL
resource "aws_db_instance" "postgres" {
  identifier        = "kirana-connect-db"
  engine            = "postgres"
  engine_version    = "15"
  instance_class    = "db.t3.large"
  allocated_storage = 100
  
  db_name  = "kiranaconnect"
  username = var.db_username
  password = var.db_password
  
  multi_az               = true
  backup_retention_period = 7
  
  tags = {
    Environment = "production"
  }
}

# ElastiCache Redis
resource "aws_elasticache_cluster" "redis" {
  cluster_id           = "kirana-connect-cache"
  engine               = "redis"
  node_type            = "cache.t3.medium"
  num_cache_nodes      = 1
  parameter_group_name = "default.redis7"
  port                 = 6379
}
```

### CI/CD Pipeline (GitLab CI)

```yaml
# .gitlab-ci.yml
stages:
  - test
  - build
  - deploy

test:
  stage: test
  image: python:3.11
  script:
    - pip install -r requirements.txt
    - pytest tests/ --cov=src --cov-report=xml
    - pylint src/
  coverage: '/TOTAL.*\s+(\d+%)$/'

build:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
  only:
    - main

deploy_prod:
  stage: deploy
  image: bitnami/kubectl:latest
  script:
    - kubectl set image deployment/inventory-service 
        inventory-service=$CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
    - kubectl rollout status deployment/inventory-service
  only:
    - main
  environment:
    name: production
```

---

## Conclusion

This design document provides a comprehensive technical blueprint for building Kirana-Connect. The system is designed to be:

- **Scalable**: Microservices architecture with Kubernetes orchestration
- **Reliable**: Multi-AZ deployment, automated backups, health monitoring
- **Intelligent**: Multi-model ML ensemble for accurate predictions
- **User-friendly**: Simple WhatsApp interface requiring minimal training
- **Maintainable**: Modular codebase with comprehensive testing and monitoring

The phased implementation approach allows for iterative development and validation with real users, ensuring product-market fit at each stage.

---

**Document Version**: 1.0  
**Last Updated**: February 2026  
**Owner**: Engineering Team  
**Status**: Initial Draft
