# KiranaConnect AI — Inventory Management Agent 🏪🤖

> **AI-powered inventory management for India's 12M+ Kirana stores — accessible through WhatsApp.**

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.135-green?logo=fastapi)
![AWS](https://img.shields.io/badge/AWS-Powered-orange?logo=amazon-aws)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 📋 Table of Contents

- [Problem Statement](#-problem-statement)
- [Solution Overview](#-solution-overview)
- [Key Features](#-key-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Setup & Run](#-setup--run)
- [API Documentation](#-api-documentation)
- [Screenshots](#-screenshots)
- [AWS Deployment](#-aws-deployment)
- [Team](#-team)

---

## 🎯 Problem Statement

India's **12 million+ Kirana stores** lose **15-25% of potential revenue** due to poor inventory management:

- **₹50,000+/year lost** per store from overstocking and stockouts
- **No data analytics** — store owners rely on intuition alone
- **Technology gap** — most owners can't afford ERP/POS systems
- **Capital locked** in slow-moving inventory, especially perishables

### Market Impact
- Combined annual revenue: **$600+ billion**
- Average store inventory: **₹2-5 lakhs**
- Typical profit margins: **5-15%**

---

## 💡 Solution Overview

**KiranaConnect AI** is an intelligent inventory management assistant that:

1. **Accessible** — WhatsApp-based interface (no app installation needed)
2. **Simple** — Send voice notes, photos of bills, or text messages
3. **Intelligent** — AI predicts demand 7 days ahead with 80%+ accuracy
4. **Actionable** — Auto-generates optimized orders to distributors
5. **Affordable** — Starting at ₹199/month

### Core Value Proposition

```
Store Owner → WhatsApp Message → AI Processing → Smart Insights → Auto-Orders → Profit!
```

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 💬 **WhatsApp AI Chat** | Natural language interface supporting English, Hindi, Hinglish |
| 📦 **Real-time Inventory** | Track 60+ product categories with live stock levels |
| 🔮 **AI Demand Forecast** | ML-based 7-day prediction with seasonal/festival awareness |
| ⚡ **Smart Auto-Ordering** | Low-stock alerts & one-click orders to distributors |
| 📊 **Analytics Dashboard** | Daily/weekly/monthly reports with interactive charts |
| 📸 **OCR Bill Scanning** | Extract data from purchase receipts automatically |
| 🌦️ **External Intelligence** | Weather, festival, and economic cycle integration |
| 🏭 **Distributor Portal** | Manage multiple distributors, track deliveries |

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────┐
│              Frontend (HTML/CSS/JS)          │
│  Landing │ Dashboard │ Chat │ Analytics │    │
│          │ + Charts  │  AI  │ + Reports │    │
└─────────────────┬───────────────────────────┘
                  │ REST API
┌─────────────────▼───────────────────────────┐
│           FastAPI Backend (Python)           │
│  Inventory │ Predictions │ Orders │ Chat    │
│  Service   │ Service     │ Service│ NLP Svc │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│           AWS Infrastructure                │
│  EC2/Lambda │ API Gateway │ DynamoDB │ S3   │
└─────────────────────────────────────────────┘
```

---

## 🛠 Tech Stack

### Backend
- **Python 3.11** + **FastAPI** — High-performance async API framework
- **Pydantic** — Data validation and serialization
- **boto3** — AWS SDK for DynamoDB & S3
- **Mangum** — AWS Lambda adapter for FastAPI

### Frontend
- **Vanilla HTML/CSS/JS** — Fast, no-framework approach
- **Chart.js** — Interactive data visualizations
- **Google Fonts (Inter)** — Premium typography
- **CSS Glassmorphism** — Modern dark-mode design

### AWS Services
- **Amazon EC2** — Application hosting
- **Amazon API Gateway** — API management & routing
- **Amazon DynamoDB** — NoSQL database for inventory data
- **Amazon S3** — Static assets & media storage
- **AWS Lambda** — Serverless compute (via Mangum)

---

## 🚀 Setup & Run

### Prerequisites
- Python 3.11+
- pip

### Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/kmvenkatakrishna/medhira_ai_kirana_connect.git
cd medhira_ai_kirana_connect

# 2. Create virtual environment
python -m venv venv

# 3. Activate (Windows)
venv\Scripts\activate
# Or (Linux/Mac)
source venv/bin/activate

# 4. Install dependencies
pip install -r backend/requirements.txt

# 5. Start the server
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

### Access Points
| Page | URL |
|------|-----|
| 🏠 Landing Page | http://localhost:8000/static/index.html |
| 📊 Dashboard | http://localhost:8000/static/dashboard.html |
| 💬 AI Chat | http://localhost:8000/static/chat.html |
| 📈 Analytics | http://localhost:8000/static/analytics.html |
| 📋 Orders | http://localhost:8000/static/orders.html |
| 📝 API Docs | http://localhost:8000/docs |

---

## 📖 API Documentation

### Endpoints Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/api/v1/stores` | List all stores |
| GET | `/api/v1/stores/{id}/inventory` | Get inventory |
| GET | `/api/v1/stores/{id}/inventory/low-stock` | Low stock alerts |
| GET | `/api/v1/stores/{id}/predictions` | Demand forecasts |
| GET | `/api/v1/stores/{id}/orders` | List orders |
| POST | `/api/v1/stores/{id}/orders/generate` | Auto-generate order |
| GET | `/api/v1/stores/{id}/reports/daily` | Daily sales report |
| GET | `/api/v1/stores/{id}/analytics/summary` | Full analytics |
| POST | `/api/v1/chat` | AI Chat (NLP) |
| GET | `/api/v1/products` | Product catalog |
| GET | `/api/v1/distributors` | Distributor list |

Interactive API docs available at: **http://localhost:8000/docs**

### Chat API Example

```bash
POST /api/v1/chat
{
    "message": "check milk stock",
    "store_id": "S001"
}

# Response:
{
    "response": "✅ Amul Milk (500ml)\n📦 Current Stock: 91 packets\n...",
    "intent": "check_inventory",
    "entities": {"product": "Amul Milk (500ml)", "product_id": "P011"},
    "suggestions": ["Predict demand for Amul Milk", "Check all inventory"]
}
```

---

## 📸 Screenshots

### Landing Page
Premium dark-mode landing with floating cards showing live data

### Inventory Dashboard
Real-time stock levels, charts, category breakdown, low-stock alerts

### AI Chat Interface
WhatsApp-style chat with NLP-powered responses, suggestion buttons

### Analytics
30-day sales trends, top products, AI demand predictions

### Orders Management
Order tracking with status pipeline, auto-generation from low stock

---

## ☁️ AWS Deployment

### Using EC2

```bash
# SSH into EC2 instance
ssh -i key.pem ec2-user@<public-ip>

# Install Python & setup
sudo yum install python3.11 -y
git clone <repo>
cd medhira_ai_kirana_connect
python3.11 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt

# Run with gunicorn
pip install gunicorn
gunicorn backend.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

### DynamoDB Table Setup

```python
# Run the table creation script
python deploy/setup_dynamodb.py
```

### Environment Variables

```bash
export AWS_REGION=ap-south-1
export USE_LOCAL_DATA=false  # Switch to DynamoDB
export S3_BUCKET=kirana-connect-media
```

---

## 👥 Team

**Medhira AI** — Built with ❤️ for India's Kirana stores

---

## 📄 License

MIT License — See [LICENSE](LICENSE) for details.
