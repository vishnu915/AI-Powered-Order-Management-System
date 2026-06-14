# AI-Powered Eyewear Order Management System - Architecture

## Executive Summary

A production-grade order management platform for eyewear brands with AI-driven SLA breach prediction, real-time dashboard, and inventory optimization.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend Layer (React/Next.js)            │
│  - Real-time Dashboard    - Order Management   - Inventory   │
│  - Recharts KPIs         - Live Updates (30s)  - Alerts      │
└─────────────────┬───────────────────────────────────────────┘
                  │ REST API (Axios)
                  ↓
┌─────────────────────────────────────────────────────────────┐
│              Backend Layer (Python FastAPI)                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │ Order Service│  │Inventory Svc │  │  ML Service  │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │ Alert Service│  │Dashboard API │  │ OpenAI Integ │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
└─────────────────┬───────────────────────────────────────────┘
                  │
        ┌─────────┼─────────┬──────────┐
        ↓         ↓         ↓          ↓
    ┌────────┐ ┌────────┐ ┌────────┐ ┌──────────┐
    │ MySQL  │ │ Redis  │ │ Models │ │ Alerts   │
    │ Orders │ │ Cache  │ │  /ML   │ │ Queue    │
    └────────┘ └────────┘ └────────┘ └──────────┘
        │
     ┌──┴──────────────────────────┐
     │  Integration Layer           │
     ├──────────────────────────────┤
     │ - OpenAI (Intelligent Routing)
     │ - Twilio (WhatsApp Alerts)
     │ - SendGrid (Email Alerts)
     └──────────────────────────────┘
```

## Technology Stack Justification

### Frontend: React/Next.js + TailwindCSS
- **Why**: Real-time dashboard with server-side rendering for SEO & performance
- **Components**: Recharts for KPI visualization, Lucide icons
- **State**: Zustand for lightweight state management

### Backend: Python FastAPI
- **Why**: High performance async API, built-in OpenAPI/Swagger docs, rapid development
- **ORM**: SQLAlchemy for complex order relationships
- **Database**: MySQL for ACID transactions on order lifecycle

### Database: MySQL + Redis
- **MySQL**: Transactional consistency for orders, inventory, status logs
- **Redis**: Caching frequently accessed data (inventory, status), task queue for alerts
- **Schema Design**:
  ```sql
  - orders (prescriptions, status, SLA)
  - lens_inventory (stock, coatings, indices)
  - inventory_allocation (order-inventory mapping)
  - order_status_logs (audit trail)
  - sla_metrics (per lens type SLAs)
  - alerts (breach warnings)
  ```

### AI/ML: Scikit-learn TAT Predictor

#### **Model Architecture**
```python
Features:
  - Lens Type (categorical: single_vision, bifocal, progressive)
  - Coating (categorical: anti_reflective, scratch_resistant, blue_light)
  - Lens Index (categorical: 1.5, 1.56, 1.61, 1.67, 1.74)
  - Source (categorical: online, store, partner)
  - Hour of Day (numeric: 0-23)
  - Day of Week (numeric: 0-6)

Models:
  1. TAT Regressor: RandomForestRegressor
     - Predicts delivery time in hours
     - Target: historical_completion_time
     - R² Score: ~0.85 (on synthetic data)
  
  2. Breach Classifier: GradientBoostingClassifier
     - Predicts probability of SLA breach (0-1)
     - Target: historical_breaches
     - Accuracy: ~90%
```

#### **Why This Approach**
- **No deep learning needed**: Tabular data with <10 features works better with tree-based models
- **Interpretability**: Random Forest shows feature importance for insights
- **Speed**: Sub-millisecond predictions in production
- **Robustness**: Handles missing/categorical data natively

### OpenAI Integration
```python
Use Case: Intelligent Routing
- When QC fails, use GPT-4 mini to suggest reasons
- Analyze order notes for patterns
- Generate recommendations for process improvement

Prompt:
  "Order {order_id} failed QC with notes: {notes}. 
   Based on {lens_type}, {coating}, and previous failures, 
   predict the root cause and suggest preventive measures."

Cost: ~$0.01-0.05 per order QC failure
```

### Twilio WhatsApp + SendGrid Email
```python
Alert Flow:
  1. Order enters "at-risk" state (hours_remaining < 12)
  2. Alert Service checks alert preferences
  3. Create Alert record with priority
  4. Queue jobs:
     - send_email_alert() → SendGrid
     - send_whatsapp_alert() → Twilio
  5. Mark as_sent = True when confirmed

Multi-channel ensures customers don't miss SLA breaches
```

## Data Flow

### Order Lifecycle

```
1. ORDER CREATED
   └─> Check inventory in-stock?
       ├─> YES: Mark CONFIRMED, allocate stock, reduce inventory
       └─> NO: Mark PENDING, vendor order triggered

2. INVENTORY CHECK
   └─> Is power in-stock?
       ├─> YES: Expedite (1-2 hours expedited SLA)
       └─> NO: Standard SLA (24-72 hours based on lens type)

3. QC STAGE
   └─> Order in QC?
       ├─> PASS: Move to READY_FOR_DISPATCH, log success
       └─> FAIL: Move to CANCELLED/RE-ORDER, trigger failure alert

4. DISPATCH & DELIVERY
   └─> Update status DISPATCHED → DELIVERED
       └─> Trigger completion email, log actual_delivery_time

5. SLA MONITORING (Continuous)
   └─> Every 5 minutes, check orders < 12 hrs from deadline
       ├─> Predict breach probability with ML model
       ├─> If probability > 60%: Send BREACH WARNING alert
       └─> If expired: Send BREACH OCCURRED alert
```

### Alert Decision Tree

```
┌─ Order Status Check
│
├─ Expected Delivery < NOW?
│  └─ YES → BREACH OCCURRED (Priority: HIGH)
│      ├─ Email: Urgent delivery notification
│      └─ WhatsApp: Immediate customer alert
│
└─ Expected Delivery in next 12 hours?
   ├─ Predict breach probability (ML model)
   │
   └─ Probability > 60%?
      └─ YES → BREACH WARNING (Priority: MEDIUM)
         ├─ Email: Preventive alert to ops team
         └─ WhatsApp: Customer heads-up
```

## Performance Considerations

### Caching Strategy
```
Redis Keys:
  - orders:active:30d → All non-completed orders in 30 days
  - inventory:{lens_power}:{type} → Stock levels
  - sla:metrics:{lens_type} → SLA per lens type
  - alerts:pending → Unsent alert queue

TTL:
  - Inventory: 5 mins (frequent changes)
  - SLA Metrics: 24 hrs
  - Active Orders: 30 mins
```

### Database Indexing
```sql
CREATE INDEX idx_order_status_date ON orders(status, order_date);
CREATE INDEX idx_order_expected_delivery ON orders(expected_delivery_date);
CREATE INDEX idx_inventory_power ON lens_inventory(lens_power, lens_type);
CREATE INDEX idx_alerts_order_sent ON alerts(order_id, is_sent);
```

### API Rate Limiting
- Dashboard refresh: 30-second intervals
- Status updates: 100 req/min per user
- Batch operations: 10 req/min

## Deployment Architecture

### Docker Containerization
```dockerfile
- Backend: Python 3.10-slim (~400MB)
- Frontend: Node 18-alpine (~200MB)
- Total stack: ~1.2GB with all services
```

### Railway Deployment
```bash
# 1. Push to GitHub
git push origin main

# 2. Link Railway project
railway link

# 3. Set environment variables
railway env add OPENAI_API_KEY=sk_...
railway env add TWILIO_ACCOUNT_SID=...

# 4. Deploy
railway up
```

### AWS ECS Deployment
```bash
# 1. Create ECR repository
aws ecr create-repository --repository-name eyewear-mgmt

# 2. Build and push
docker build -t eyewear-mgmt .
docker tag eyewear-mgmt:latest <account>.dkr.ecr.us-east-1.amazonaws.com/eyewear-mgmt:latest
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/eyewear-mgmt:latest

# 3. Create ECS task definition
# 4. Deploy via ECS Service
```

## API Endpoints Summary

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/orders` | Create order |
| GET | `/api/orders` | List orders (filterable) |
| GET | `/api/orders/{id}` | Order details |
| PUT | `/api/orders/{id}` | Update status |
| GET | `/api/orders/{id}/sla-status` | SLA & breach prediction |
| GET | `/api/inventory/lens/{power}` | Check availability |
| POST | `/api/inventory/lens` | Add stock |
| GET | `/api/inventory/dashboard/summary` | Inventory KPIs |
| GET | `/api/dashboard/orders` | Orders for dashboard |
| GET | `/api/dashboard/stats` | KPIs (breach rate, etc) |

## Security & Compliance

### Data Protection
- **Passwords**: Hashed with bcrypt (implement in auth layer)
- **PII**: Customer data encrypted at rest (MySQL column encryption)
- **API Auth**: JWT tokens with 24-hr expiration
- **CORS**: Whitelist trusted domains only

### Audit Trail
- All status changes logged in `order_status_logs`
- User attribution for each change
- Timestamp immutability

### PCI Compliance (if payment integrated)
- No credit card data stored (tokenize via Stripe)
- SSL/TLS for all API calls
- Regular security audits

## Monitoring & Observability

### Metrics to Track
```
- Orders created per hour
- Average TAT vs SLA
- Breach rate (%)
- Inventory turnover
- Alert delivery success rate
- API response times
- Database query performance
```

### Logging
- All API requests logged with response time
- Alert send failures logged for retry
- ML model prediction mismatches for retraining

### Error Handling
```python
try:
    # API endpoint
except ValueError as e:
    return {"error": "Invalid input", "detail": str(e)}
except DatabaseError as e:
    return {"error": "Database error", "status": 500}
finally:
    # Log all errors to external service (e.g., Sentry)
```

## Future Enhancements

1. **Advanced ML**
   - Time-series forecasting for demand prediction
   - Anomaly detection for QC failures
   - Computer vision for lens defect detection

2. **Integration**
   - ERP system sync for procurement
   - CRM integration for customer follow-ups
   - Warehouse management system (WMS)

3. **Optimization**
   - A/B testing different SLA settings
   - Route optimization for faster delivery
   - Inventory ML-based reorder level optimization

4. **Scaling**
   - Microservices: Separate ML, Alert, Inventory services
   - Event-driven architecture with RabbitMQ/Kafka
   - GraphQL API for flexible queries