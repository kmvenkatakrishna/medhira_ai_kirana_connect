# Kirana-Connect: Inventory AI Agent - Requirements Document

## Executive Summary

Kirana-Connect is a WhatsApp-based AI agent designed to revolutionize inventory management for millions of local Kirana stores across India. By leveraging AI and data analytics, it solves the critical problem of overstocking and stockouts that cost store owners significant revenue.

## Problem Statement

### Current Challenges
- **Revenue Loss**: Kirana stores lose 15-25% of potential revenue due to poor inventory management
- **Overstocking**: Capital locked in slow-moving inventory, leading to wastage (especially perishables)
- **Stockouts**: Lost sales opportunities when popular items run out during peak demand
- **No Data Analytics**: Store owners rely on intuition rather than data-driven decisions
- **Technology Gap**: Most Kirana owners lack access to sophisticated inventory management systems
- **Limited Resources**: Cannot afford expensive ERP or POS systems

### Market Impact
- 12+ million Kirana stores in India
- Estimated combined annual revenue of $600+ billion
- Average store inventory worth ₹2-5 lakhs
- Typical profit margins of 5-15%

## Solution Overview

Kirana-Connect is an AI-powered inventory management assistant accessible through WhatsApp, requiring minimal technical knowledge and zero infrastructure investment.

### Core Value Proposition
1. **Accessible**: WhatsApp-based interface (no app installation required)
2. **Simple**: Voice notes or photos of purchase receipts
3. **Intelligent**: AI-driven demand prediction
4. **Actionable**: Automated order suggestions to distributors
5. **Affordable**: Subscription-based pricing starting at ₹199/month

## Functional Requirements

### 1. User Input Module

#### 1.1 Photo-Based Input
- **Capability**: Accept photos of purchase receipts, bills, or handwritten notes
- **OCR Requirements**:
  - Support for English and Hindi text
  - Recognize common product names and categories
  - Extract quantities, prices, and dates
  - Handle poor lighting and photo quality
  - Accuracy target: 95%+ for printed text, 85%+ for handwritten

#### 1.2 Voice Note Input
- **Capability**: Process voice messages in Hindi, English, and Hinglish
- **Speech Recognition Requirements**:
  - Support regional accents
  - Handle background noise (typical store environment)
  - Recognize product names, quantities, and categories
  - Accuracy target: 90%+ in controlled conditions, 80%+ in noisy environments

#### 1.3 Text Input
- **Capability**: Accept text messages with inventory details
- **Format Flexibility**:
  - Freeform text: "Bought 100 milk packets today"
  - Structured format: "Item: Milk, Qty: 100, Price: 50"
  - List format with multiple items

### 2. Data Processing Module

#### 2.1 Inventory Tracking
- **Real-time Inventory Database**:
  - Track current stock levels for each SKU
  - Record purchase dates and quantities
  - Monitor sales velocity (items sold per day)
  - Calculate stock-on-hand in real-time

#### 2.2 Product Catalog Management
- **Master Product Database**:
  - 10,000+ common Kirana products
  - Categories: groceries, beverages, snacks, personal care, household
  - Product variants and sizes
  - Regional product variations
  - Auto-suggest feature for new products

#### 2.3 Data Validation
- **Quality Assurance**:
  - Verify extracted data against known patterns
  - Flag unusual entries (e.g., abnormal quantities)
  - Request confirmation for ambiguous entries
  - Learn from user corrections

### 3. AI Prediction Engine

#### 3.1 Demand Forecasting
- **Machine Learning Models**:
  - Time-series analysis (ARIMA, Prophet)
  - Seasonal decomposition
  - Trend detection
  - Historical sales pattern recognition

#### 3.2 External Data Integration
- **Contextual Factors**:
  - **Festival Calendar**: Hindu, Muslim, Christian, regional festivals
  - **Weather Data**: Temperature, rainfall, seasonal changes
  - **Day of Week**: Weekend vs weekday patterns
  - **Local Events**: Melas, fairs, school holidays
  - **Economic Indicators**: Payday cycles, salary dates

#### 3.3 Predictive Accuracy
- **Performance Metrics**:
  - Target accuracy: 80%+ for 7-day forecast
  - Error margin: ±15% for individual SKUs
  - Category-level accuracy: 85%+
  - Continuous learning from actual sales data

### 4. Order Suggestion Module

#### 4.1 Smart Recommendations
- **Automated Order Generation**:
  - Calculate optimal order quantity per SKU
  - Consider lead time (typical 1-3 days)
  - Account for current stock levels
  - Factor in shelf life (for perishables)
  - Budget constraints (if set by owner)

#### 4.2 Distributor Integration
- **Order Fulfillment**:
  - Maintain list of preferred distributors per category
  - Format orders for distributor systems (WhatsApp, email, SMS)
  - Track order status
  - Maintain pricing information from multiple distributors

#### 4.3 Alert System
- **Proactive Notifications**:
  - Low stock alerts (2-3 days before stockout)
  - Overstock warnings (slow-moving items)
  - Price change notifications from distributors
  - Festival/event reminders with demand surge predictions

### 5. Communication Module

#### 5.1 WhatsApp Integration
- **Technical Requirements**:
  - WhatsApp Business API integration
  - Support for text, voice, images
  - Quick reply buttons for common actions
  - List messages for product selection
  - Rich media support (PDFs for reports)

#### 5.2 Conversational AI
- **Natural Language Understanding**:
  - Intent recognition (add stock, check inventory, place order)
  - Entity extraction (product names, quantities, dates)
  - Context maintenance across conversations
  - Multilingual support (English, Hindi, + 5 regional languages)

#### 5.3 User Experience
- **Interaction Design**:
  - Simple onboarding (3-5 minutes)
  - Guided setup wizard
  - Daily/weekly summary reports
  - Interactive inventory queries
  - Help commands and tutorials

### 6. Reporting & Analytics Module

#### 6.1 Dashboard Reports
- **Daily Reports**:
  - Sales summary
  - Top-selling items
  - Slow-moving inventory
  - Stockout incidents

- **Weekly Reports**:
  - Sales trends
  - Profit margins by category
  - Forecast accuracy metrics
  - Inventory turnover ratio

- **Monthly Reports**:
  - Performance comparison (MoM)
  - Seasonal trends
  - Revenue optimization suggestions
  - ROI from using the system

#### 6.2 Visual Analytics
- **Chart Types**:
  - Sales trends (line charts)
  - Category-wise sales (pie charts)
  - Forecast vs actual (comparison charts)
  - Inventory age analysis (histogram)

### 7. Distributor Portal Module

#### 7.1 Distributor Features
- **Order Management**:
  - Receive orders from multiple stores
  - Confirm/modify order quantities
  - Update delivery status
  - Maintain product catalog and pricing

#### 7.2 Analytics for Distributors
- **Insights**:
  - Demand trends across stores
  - Popular products by region
  - Optimal stock levels at distributor warehouses

## Non-Functional Requirements

### 1. Performance
- **Response Time**:
  - OCR processing: < 5 seconds per image
  - Voice transcription: < 8 seconds per 60-second audio
  - Demand prediction: < 10 seconds for 7-day forecast
  - WhatsApp message response: < 3 seconds

- **Scalability**:
  - Support 100,000+ concurrent users
  - Handle 1 million+ messages per day
  - Process 500,000+ images/voice notes daily

### 2. Reliability
- **Uptime**: 99.5% availability (excluding planned maintenance)
- **Data Backup**: Hourly incremental, daily full backups
- **Disaster Recovery**: RPO < 1 hour, RTO < 4 hours
- **Failover**: Automatic failover for critical services

### 3. Security
- **Data Protection**:
  - End-to-end encryption for sensitive data
  - Compliance with Indian data protection regulations
  - Secure storage of business data (ISO 27001 standards)
  - Role-based access control

- **Authentication**:
  - Phone number verification (OTP)
  - Optional PIN for sensitive operations
  - Session management and timeout

### 4. Usability
- **Accessibility**:
  - Low literacy design (voice-first, icon-based)
  - Support for users with basic smartphone skills
  - Works on low-end Android devices (Android 5+)
  - Minimal data usage (< 10 MB/day for typical usage)

- **Localization**:
  - 8+ Indian languages
  - Regional product naming conventions
  - Currency formatting (₹ symbol)
  - Date formats (DD/MM/YYYY)

### 5. Compliance
- **Legal Requirements**:
  - GST compliance (tax calculations)
  - E-invoice compatibility
  - Consumer data protection laws
  - Vendor agreements and terms of service

### 6. Maintainability
- **System Design**:
  - Modular architecture
  - API-first design
  - Comprehensive logging
  - Automated testing (80%+ code coverage)
  - Documentation for all APIs and services

## Technical Constraints

### 1. Platform Limitations
- WhatsApp Business API restrictions on message frequency
- File size limits (16 MB for media)
- Message template approval process

### 2. Connectivity
- Must work on 2G/3G networks (common in rural areas)
- Offline mode for basic inventory tracking
- Data sync when connection restored

### 3. Device Compatibility
- Android 5.0+ (covers 95%+ of target market)
- iOS support (optional, for premium segment)
- Basic feature phones (limited functionality via SMS)

## Success Metrics

### 1. User Adoption
- 10,000 stores onboarded in first 6 months
- 100,000 stores in 18 months
- Daily active user rate: 60%+
- Monthly churn rate: < 10%

### 2. Business Impact
- Average inventory reduction: 20%
- Stockout reduction: 40%
- Revenue increase: 8-12% for active users
- ROI for store owners: 5x within 6 months

### 3. System Performance
- Prediction accuracy: 80%+ within 3 months of usage
- User satisfaction score: 4.2+/5
- Support ticket resolution: 90% within 24 hours

### 4. Financial Metrics
- CAC (Customer Acquisition Cost): < ₹500
- LTV (Lifetime Value): > ₹5,000
- Break-even: 18 months
- Profitability: 25% gross margin by Month 24

## Future Enhancements

### Phase 2 (Months 7-12)
- Credit and payment integration
- Supplier financing options
- Group purchasing power (bulk orders across stores)
- Customer loyalty program integration

### Phase 3 (Months 13-18)
- Competitive intelligence (pricing comparison)
- Promotional calendar and marketing automation
- Integration with POS systems
- Franchise expansion features

### Phase 4 (Months 19-24)
- AI-powered pricing optimization
- Dynamic promotions based on inventory levels
- Supply chain visibility and tracking
- Cross-selling and upselling recommendations

## Assumptions
1. Store owners have WhatsApp-enabled smartphones
2. Reliable internet connectivity (at least 2G)
3. Basic literacy in at least one supported language
4. Willingness to share sales and inventory data
5. Existing relationships with distributors

## Dependencies
1. WhatsApp Business API access
2. Cloud infrastructure (AWS/GCP)
3. Payment gateway integration
4. OCR/NLP service providers
5. Weather and festival calendar data sources
6. Distributor partnerships

## Risks & Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Low user adoption due to trust issues | High | Medium | Free trial, referral programs, local champions |
| Inaccurate predictions harming credibility | High | Medium | Conservative predictions, human-in-loop validation |
| WhatsApp API policy changes | High | Low | Build multi-channel support (SMS, Telegram) |
| Competition from established players | Medium | High | Focus on ease-of-use and Kirana-specific features |
| Data privacy concerns | Medium | Medium | Transparent policies, data anonymization |
| Seasonal demand volatility | Low | High | Continuous model retraining, manual override options |

---

**Document Version**: 1.0  
**Last Updated**: February 2026  
**Owner**: Product Team  
**Status**: Initial Draft
