# KiranaConnect AI — Project Summary

## Problem Statement

India's 12 million+ Kirana (neighborhood grocery) stores face a critical inventory management problem:

- **15-25% revenue loss** from overstocking and stockouts
- **₹50,000+ per year** wasted per store on poor inventory decisions
- **No access** to affordable technology solutions — most rely purely on memory and intuition
- **Perishable goods wastage** from lack of demand forecasting
- **No data-driven decisions** — despite handling ₹2-5 lakh inventory

The FMCG supply chain, worth $600+ billion annually, depends on these stores — yet they operate with almost zero technological support.

---

## Our Solution

**KiranaConnect AI** is an AI-powered inventory management agent accessible through WhatsApp — requiring zero app installation, minimal tech literacy, and no infrastructure investment.

### How It Works

1. **Store owner sends a WhatsApp message** — text, voice note, or photo of a purchase bill
2. **AI processes the input** — NLP/OCR extracts products, quantities, and prices
3. **Inventory updates automatically** — real-time stock tracking
4. **ML predicts demand** — 7-day forecast using sales history, weather, festivals, and trends
5. **Smart alerts & auto-ordering** — low-stock warnings 2-3 days before stockout, one-click orders to distributors

### Key Features

| Feature | Impact |
|---------|--------|
| WhatsApp-based AI Chat | Zero learning curve, works on any phone |
| AI Demand Prediction | 80%+ forecast accuracy, reduces wastage 30% |
| Smart Auto-Ordering | Prevents stockouts, saves 2-3 hours/week |
| Real-time Analytics | Data-driven decisions for the first time |
| OCR Bill Scanning | 10x faster data entry than manual |
| Multi-Language | Hindi, English, Hinglish support |

### AWS Infrastructure

| Service | Usage |
|---------|-------|
| Amazon EC2 | Application server hosting |
| Amazon API Gateway | API management and routing |
| Amazon DynamoDB | NoSQL database for all inventory data |
| Amazon S3 | Static asset and media file storage |
| AWS Lambda | Serverless compute with Mangum adapter |

### Technology Stack

- **Backend**: Python 3.11, FastAPI, boto3, Pydantic
- **Frontend**: HTML5, CSS3, JavaScript, Chart.js
- **AI/ML**: NLP intent classification, demand forecasting simulation
- **Cloud**: AWS (EC2, API Gateway, DynamoDB, S3, Lambda)

---

## Impact & Metrics

| Metric | Target |
|--------|--------|
| Annual savings per store | ₹50,000+ |
| Forecast accuracy | 80%+ for 7-day predictions |
| Time saved daily | 15-30 minutes |
| Stockout reduction | 40%+ |
| Wastage reduction | 30%+ for perishables |
| Addressable market | 12M+ stores, $600B+ revenue |

---

## Live Demo

- **GitHub Repository**: https://github.com/kmvenkatakrishna/medhira_ai_kirana_connect
- **Live Prototype**: [See deployment instructions in README]

---

*Built by Medhira AI — © 2026*
