from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.models.database import (
    Order, OrderStatus, LensType, CoatingType, OrderStatusLog,
    LensInventory, InventoryAllocation, SLAMetrics, Alert
)
from app.schemas.order import OrderCreate, OrderUpdate
from app.services.alert_service import AlertService
import uuid

class OrderService:
    def __init__(self, db: Session):
        self.db = db
        self.alert_service = AlertService(db)
    
    def create_order(self, order_data: OrderCreate) -> Order:
        """Create a new order and check inventory"""
        order_id = f"ORD-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
        
        # Get SLA based on lens type
        sla_metric = self.db.query(SLAMetrics).filter(
            SLAMetrics.lens_type == order_data.lens_type
        ).first()
        sla_hours = sla_metric.sla_hours if sla_metric else 48
        
        expected_delivery = datetime.utcnow() + timedelta(hours=sla_hours)
        
        # Create order
        db_order = Order(
            order_id=order_id,
            customer_name=order_data.customer_name,
            customer_email=order_data.customer_email,
            customer_phone=order_data.customer_phone,
            left_eye_power=order_data.left_eye_power,
            right_eye_power=order_data.right_eye_power,
            cylinder=order_data.cylinder,
            axis=order_data.axis,
            lens_type=order_data.lens_type,
            lens_index=order_data.lens_index,
            coating=order_data.coating,
            frame_type=order_data.frame_type,
            source=order_data.source,
            store_location=order_data.store_location,
            status=OrderStatus.PENDING,
            expected_delivery_date=expected_delivery,
            sla_hours=sla_hours
        )
        
        self.db.add(db_order)
        self.db.commit()
        self.db.refresh(db_order)
        
        # Check inventory and allocate if available
        self._check_and_allocate_inventory(db_order)
        
        return db_order
    
    def _check_and_allocate_inventory(self, order: Order):
        """Check if lens is in stock and allocate"""
        # Check for both eyes
        for eye_power in [order.left_eye_power, order.right_eye_power]:
            power_str = f"{eye_power:+.2f}"
            
            inventory_item = self.db.query(LensInventory).filter(
                LensInventory.lens_power == power_str,
                LensInventory.lens_type == order.lens_type,
                LensInventory.lens_index == order.lens_index,
                LensInventory.coating == order.coating
            ).first()
            
            if inventory_item and inventory_item.stock_quantity > 0:
                # Allocate
                allocation = InventoryAllocation(
                    order_id=order.id,
                    inventory_id=inventory_item.id,
                    quantity=1
                )
                inventory_item.stock_quantity -= 1
                self.db.add(allocation)
                order.status = OrderStatus.CONFIRMED
        
        self.db.commit()
    
    def update_order_status(self, order_id: int, update_data: OrderUpdate, updated_by: str):
        """Update order status and log the change"""
        order = self.db.query(Order).filter(Order.id == order_id).first()
        
        if not order:
            return None
        
        old_status = order.status
        
        if update_data.status:
            order.status = update_data.status
        
        if update_data.notes:
            order.notes = update_data.notes
        
        if update_data.qc_fail_reason:
            order.qc_fail_reason = update_data.qc_fail_reason
        
        order.updated_at = datetime.utcnow()
        
        # Log status change
        status_log = OrderStatusLog(
            order_id=order.id,
            old_status=old_status,
            new_status=order.status,
            reason=update_data.notes or update_data.qc_fail_reason,
            updated_by=updated_by
        )
        
        self.db.add(status_log)
        self.db.commit()
        
        # Check if breach alert needed
        if self._check_sla_breach(order):
            self.alert_service.create_breach_alert(order)
        
        return order
    
    def _check_sla_breach(self, order: Order) -> bool:
        """Check if order is breaching SLA"""
        if order.status in [OrderStatus.DELIVERED, OrderStatus.CANCELLED]:
            return False
        
        time_remaining = order.expected_delivery_date - datetime.utcnow()
        return time_remaining.total_seconds() <= 0
    
    def get_order(self, order_id: int):
        return self.db.query(Order).filter(Order.id == order_id).first()
    
    def list_orders(self, status: OrderStatus = None, lens_type: LensType = None, 
                    location: str = None, skip: int = 0, limit: int = 50):
        query = self.db.query(Order)
        
        if status:
            query = query.filter(Order.status == status)
        if lens_type:
            query = query.filter(Order.lens_type == lens_type)
        if location:
            query = query.filter(Order.store_location == location)
        
        return query.offset(skip).limit(limit).all()
    
    def get_sla_status(self, order_id: int):
        """Get SLA status and breach prediction"""
        order = self.get_order(order_id)
        if not order:
            return None
        
        time_remaining = order.expected_delivery_date - datetime.utcnow()
        hours_remaining = time_remaining.total_seconds() / 3600
        breach_probability = self._predict_breach(order)
        
        return {
            "order_id": order.order_id,
            "status": order.status,
            "sla_hours": order.sla_hours,
            "hours_remaining": max(0, hours_remaining),
            "expected_delivery": order.expected_delivery_date,
            "breach_probability": breach_probability,
            "is_breached": hours_remaining <= 0
        }
    
    def _predict_breach(self, order: Order) -> float:
        """Predict breach probability using ML"""
        # Will be integrated with ML service
        return 0.0