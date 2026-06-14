# 👓 AI-Powered Eyewear Order Management System

An intelligent Order Management Platform for eyewear brands that automates the complete order lifecycle, predicts SLA breaches, manages lens inventory, and provides real-time operational insights using AI.

## 🚀 Overview

Eyewear orders are more complex than standard e-commerce orders because each order includes:

* Prescription Details
* Lens Type
* Lens Index
* Lens Coating
* Frame Selection
* Manufacturing & Quality Control Stages

This system streamlines the entire fulfillment workflow from **Order Placement → Processing → Quality Check → Delivery**, while using AI to predict delays and optimize operations.

---

## ✨ Key Features

### 📦 Order Lifecycle Management

* Create and manage eyewear orders
* Track order status in real time
* Complete workflow management
* Delay reason logging
* Quality Control (QC) re-order handling

### 🏭 Lens Inventory Management

* Track in-house lens inventory
* Check lens availability instantly
* Low stock monitoring
* Inventory allocation for orders
* Smart inventory visibility

### 📊 Real-Time Dashboard

* Active order monitoring
* SLA countdown tracking
* Breach alerts
* Status-based filtering
* Lens type filtering
* Store location filtering

### 🤖 AI-Powered Intelligence

* TAT (Turn Around Time) prediction
* SLA breach prediction
* Intelligent order insights
* Delay risk analysis
* Automated recommendations

### 🔔 Alert System

* Email notifications
* WhatsApp alerts
* SLA breach warnings
* Low inventory alerts

---

## 🛠️ Tech Stack

### Frontend

* React.js / Next.js
* Tailwind CSS
* Axios
* Recharts
* Lucide Icons

### Backend

* Python
* FastAPI
* SQLAlchemy

### Database

* MySQL
* Redis

### AI & Machine Learning

* Scikit-Learn
* Random Forest
* Gradient Boosting
* OpenAI API

### Notifications

* Twilio WhatsApp API
* SendGrid Email API

### Deployment

* Docker
* Railway
* AWS

---

## 📂 Project Structure

```bash
eyewear-order-management/
│
├── backend/
│   ├── app/
│   ├── api/
│   ├── services/
│   ├── models/
│   └── ml/
│
├── frontend/
│   ├── pages/
│   ├── components/
│   ├── services/
│   └── styles/
│
├── docker-compose.yml
├── README.md
├── ARCHITECTURE.md
└── DEPLOYMENT.md
```

---

## 🔄 Order Workflow

```text
Order Created
      ↓
Inventory Check
      ↓
Order Confirmed
      ↓
Lens Processing
      ↓
Frame Assembly
      ↓
Quality Check
      ↓
Packaging
      ↓
Delivered
```

If QC fails:

```text
Quality Check Failed
        ↓
Reorder Triggered
        ↓
Reprocessing
        ↓
Quality Check
        ↓
Delivered
```

---

## 🧠 AI Features

### TAT Prediction

Predicts order completion time using:

* Lens Type
* Lens Index
* Coating
* Store Location
* Historical Orders
* Current Processing Stage

### SLA Breach Detection

The AI model continuously evaluates:

* Current Order Stage
* Processing Delays
* Historical Trends
* Inventory Availability

and predicts potential SLA violations before they happen.

---

## 📈 Dashboard Metrics

* Total Orders
* Pending Orders
* Processing Orders
* Delivered Orders
* SLA Breach Rate
* Active Alerts
* Inventory Status
* Low Stock Items

---

## 🔌 API Endpoints

### Orders

```http
POST   /api/orders
GET    /api/orders
GET    /api/orders/{id}
PUT    /api/orders/{id}
```

### Inventory

```http
GET    /api/inventory
POST   /api/inventory
GET    /api/inventory/low-stock
```

### Dashboard

```http
GET    /api/dashboard/stats
GET    /api/dashboard/orders
```

---

## ⚙️ Installation

### Backend

```bash
cd backend

python -m venv venv

venv\Scripts\activate

pip install -r requirements.txt

uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend

npm install

npm run dev
```

---

## 🌐 Application URLs

Frontend:

```text
http://localhost:3000
```

Backend:

```text
http://localhost:8000
```

Swagger API Docs:

```text
http://localhost:8000/docs
```

---

## 🎯 Business Benefits

* Faster order fulfillment
* Reduced SLA breaches
* Better inventory utilization
* Improved customer satisfaction
* Automated operational monitoring
* AI-driven decision making

---

## 📸 Demo Scenarios

1. Create Order
2. Check Inventory Availability
3. Update Order Status
4. Monitor SLA Countdown
5. Trigger AI Breach Prediction
6. Receive Alert Notification
7. Complete Delivery

