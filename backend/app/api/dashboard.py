from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.models.database import get_db, Order, OrderStatus, Alert
from datetime import datetime, timedelta
from typing import Optional

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

@router.get("/orders")
def get_dashboard_orders(
    status: Optional[OrderStatus] = Query(None),
    location: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get orders for dashboard with SLA metrics"""
    query = db.query(Order)
    
    if status:
        query = query.filter(Order.status == status)
    if location:
        query = query.filter(Order.store_location == location)
    
    orders = query.all()
    
    dashboard_orders = []
    for order in orders:
        time_remaining = order.expected_delivery_date - datetime.utcnow()
        hours_remaining = time_remaining.total_seconds() / 3600
        
        dashboard_orders.append({
            "id": order.id,
            "order_id": order.order_id,
            "customer": order.customer_name,
            "lens_type": order.lens_type,
            "status": order.status,
            "location": order.store_location,
            "order_date": order.order_date,
            "expected_delivery": order.expected_delivery_date,
            "hours_remaining": max(0, hours_remaining),
            "is_breached": hours_remaining <= 0,
            "sla_hours": order.sla_hours
        })
    
    return dashboard_orders

@router.get("/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get KPIs and metrics"""
    now = datetime.utcnow()
    
    total_orders = db.query(Order).count()
    pending_orders = db.query(Order).filter(Order.status == OrderStatus.PENDING).count()
    delivered_orders = db.query(Order).filter(Order.status == OrderStatus.DELIVERED).count()
    
    # Breach rate
    breached = db.query(Order).filter(
        Order.expected_delivery_date < now,
        Order.status != OrderStatus.DELIVERED
    ).count()
    breach_rate = (breached / total_orders * 100) if total_orders > 0 else 0
    
    # Recent alerts
    recent_alerts = db.query(Alert).filter(
        Alert.created_at > now - timedelta(hours=24),
        Alert.is_sent == True
    ).count()
    
    return {
        "total_orders": total_orders,
        "pending_orders": pending_orders,
        "delivered_orders": delivered_orders,
        "breach_rate": round(breach_rate, 2),
        "recent_alerts_24h": recent_alerts
    }

@router.get("/status-breakdown")
def get_status_breakdown(db: Session = Depends(get_db)):
    """Get order count by status"""
    statuses = [status for status in OrderStatus]
    breakdown = {}
    
    for status in statuses:
        count = db.query(Order).filter(Order.status == status).count()
        breakdown[status.value] = count
    
    return breakdown