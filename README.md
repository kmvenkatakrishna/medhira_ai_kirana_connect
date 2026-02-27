# KiranaConnect: AI Inventory Agent

KiranaConnect is an AI-powered inventory management assistant accessible through WhatsApp, specifically designed for local Kirana store owners. It requires minimal technical knowledge and zero infrastructure investment, leveraging AWS Serverless technologies for high scalability and low cost.

This repository contains the prototype built for the 7-day development window.

## Problem Statement
Small retail (Kirana) stores struggle with manual inventory tracking, leading to stockouts of fast-moving items, overstocking of slow movers, and capital tied up in inefficient inventory. Most digital solutions are either too complex, require expensive hardware, or demand significant behavior change from store owners.

## Solution Overview
KiranaConnect provides a frictionless experience using WhatsApp—an interface Kirana owners already use daily. 
It uses Natural Language Processing (simulated in this prototype) to understand inventory queries and updates, and predictive analytics to suggest reorders.

## Architecture & Technologies
This prototype is built on AWS Infrastructure:
- **Backend**: Python 3.11 with FastAPI, wrapped using Mangum for AWS Lambda compatibility.
- **Frontend**: Vanilla HTML/CSS/JS (for fast, lightweight deployment via AWS Amplify or S3).
- **Database**: Amazon DynamoDB (NoSQL for high performance).
- **Storage**: Amazon S3 (for media/receipt uploads).
- **Infrastructure as Code**: AWS SAM (`template.yaml`).

## Repository Structure
```text
.
├── backend/               # FastAPI Backend Code
│   ├── main.py            # API Entrypoint
│   ├── requirements.txt   # Python Dependencies
│   ├── routers/           # REST API endpoints (Inventory, WhatsApp Mock, Analytics)
│   └── services/          # DynamoDB and S3 integration wrappers
├── frontend/              # Web application (Dashboard & Chat Simulator)
│   ├── index.html         # Dashboard showing real-time metrics
│   ├── chat.html          # WhatsApp UX Simulator
│   ├── style.css          # Premium Glassmorphism styling
│   └── app.js             # API Integration
└── template.yaml          # AWS SAM Template for backend deployment
```

---

## 🚀 How to Run Locally

### 1. Backend (FastAPI)
1. Navigate to the `backend/` directory:
   ```bash
   cd backend
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the development server (Note: The prototype uses in-memory mock data fallbacks if DynamoDB is unavailable, but boto3 will attempt to find credentials):
   ```bash
   uvicorn main:app --reload
   ```
   > The API will be available at `http://127.0.0.1:8000`. You can view Swagger documentation at `http://127.0.0.1:8000/docs`.

### 2. Frontend (UI & Simulator)
1. Simply open `frontend/index.html` in your web browser. Or, use a tool like Live Server.
2. The UI is designed to communicate with the local backend running on `http://localhost:8000`.
3. Try typing "Bought 50 Milk packets" in the Mock WhatsApp simulator!

---

## ☁️ How to Deploy on AWS

### Backend Deployment (AWS API Gateway + Lambda + DynamoDB)
Prerequisites: AWS CLI installed and configured, AWS SAM CLI installed.

1. Build the serverless application:
   ```bash
   sam build
   ```
2. Deploy the application:
   ```bash
   sam deploy --guided
   ```
   - Follow the prompts. Provide a stack name (e.g., `kiranaconnect-backend`).
   - SAM will automatically create the DynamoDB tables, S3 bucket, Lambda function, and API Gateway.
   - Once complete, copy the output `KiranaApiUrl`.

### Frontend Deployment (AWS Amplify)
1. Open `frontend/app.js` and update `API_BASE_URL` to point to your new `KiranaApiUrl` from the SAM output.
2. Go to the **AWS Amplify Console**.
3. Create a new app and choose "Deploy without Git provider" or connect this repository.
4. If deploying manually, zip the contents of the `frontend/` folder and upload it to Amplify.
5. Amplify will provide a live URL (e.g., `https://main.xxxxxx.amplifyapp.com`).

---

## 🎥 Video Demo Submission Guide
When recording the demo for submission:
1. **Show the Dashboard**: Highlight the "Out of Stock" alerts and the total inventory value.
2. **Show the Chat Simulator**: This is the core workflow! Type "Bought 10 Parle G" and show how the inventory automatically updates. Ask "Check stock" to demonstrate the NLP flow.
3. **Show the Predictions**: Point out the AI prediction table suggesting how many days until an item runs out.
4. **Mention AWS**: Briefly show the `template.yaml` to prove it is architected for AWS Lambda and DynamoDB.
