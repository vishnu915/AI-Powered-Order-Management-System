from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.models.database import get_db, OrderStatus, LensType
from app.schemas.order import OrderCreate, OrderUpdate, OrderResponse, OrderDetailResponse
from app.services.order_service import OrderService
from app.services.ml_service import MLService
from typing import List, Optional

router = APIRouter(prefix="/api/orders", tags=["orders"])

@router.post("", response_model=OrderResponse)
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    """Create a new order"""
    service = OrderService(db)
    db_order = service.create_order(order)
    return db_order

@router.get("", response_model=List[OrderResponse])
def list_orders(
    status: Optional[OrderStatus] = Query(None),
    lens_type: Optional[LensType] = Query(None),
    location: Optional[str] = Query(None),
    skip: int = Query(0),
    limit: int = Query(50),
    db: Session = Depends(get_db)
):
    """List orders with filters"""
    service = OrderService(db)
    orders = service.list_orders(status, lens_type, location, skip, limit)
    return orders

@router.get("/{order_id}", response_model=OrderDetailResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    """Get order details"""
    service = OrderService(db)
    order = service.get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.put("/{order_id}", response_model=OrderDetailResponse)
def update_order(order_id: int, update: OrderUpdate, db: Session = Depends(get_db)):
    """Update order status"""
    service = OrderService(db)
    order = service.update_order_status(order_id, update, "admin")
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.get("/{order_id}/sla-status")
def get_sla_status(order_id: int, db: Session = Depends(get_db)):
    """Get SLA status and breach prediction"""
    service = OrderService(db)
    ml_service = MLService()
    order = service.get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    sla_status = service.get_sla_status(order_id)
    predicted_tat = ml_service.predict_tat(order)
    breach_probability = ml_service.predict_breach_probability(order, db)
    
    return {
        **sla_status,
        "predicted_tat_hours": predicted_tat,
        "breach_probability": breach_probability
    }