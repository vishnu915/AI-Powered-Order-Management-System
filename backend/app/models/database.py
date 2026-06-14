from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean, Enum as SQLEnum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import enum

# Database connection
DATABASE_URL = "mysql+pymysql://root:password@localhost:3306/eyewear_db"
engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_recycle=3600)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    LENS_ORDERED = "lens_ordered"
    QC_PASS = "qc_pass"
    QC_FAIL = "qc_fail"
    READY_FOR_DISPATCH = "ready_for_dispatch"
    DISPATCHED = "dispatched"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class LensType(str, enum.Enum):
    SINGLE_VISION = "single_vision"
    BIFOCAL = "bifocal"
    PROGRESSIVE = "progressive"
    PHOTOCHROMIC = "photochromic"

class CoatingType(str, enum.Enum):
    ANTI_REFLECTIVE = "anti_reflective"
    SCRATCH_RESISTANT = "scratch_resistant"
    BLUE_LIGHT = "blue_light"
    UV_PROTECTION = "uv_protection"
    NONE = "none"

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String(50), unique=True, index=True)
    customer_name = Column(String(100))
    customer_email = Column(String(100))
    customer_phone = Column(String(20))
    
    # Prescription
    left_eye_power = Column(Float)
    right_eye_power = Column(Float)
    cylinder = Column(Float, nullable=True)
    axis = Column(Float, nullable=True)
    
    # Lens Details
    lens_type = Column(SQLEnum(LensType))
    lens_index = Column(String(20))  # 1.5, 1.56, 1.61, 1.67, 1.74
    coating = Column(SQLEnum(CoatingType))
    frame_type = Column(String(100))
    
    # Order Details
    source = Column(String(50))  # online, store, partner
    store_location = Column(String(100))
    status = Column(SQLEnum(OrderStatus), default=OrderStatus.PENDING)
    
    # SLA & Timing
    order_date = Column(DateTime, default=datetime.utcnow)
    expected_delivery_date = Column(DateTime)
    actual_delivery_date = Column(DateTime, nullable=True)
    sla_hours = Column(Integer)  # SLA in hours based on lens type
    
    # Notes
    notes = Column(Text, nullable=True)
    qc_fail_reason = Column(Text, nullable=True)
    
    # Tracking
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    inventory_items = relationship("InventoryAllocation", back_populates="order")
    status_logs = relationship("OrderStatusLog", back_populates="order")
    alerts = relationship("Alert", back_populates="order")

class LensInventory(Base):
    __tablename__ = "lens_inventory"
    
    id = Column(Integer, primary_key=True, index=True)
    lens_power = Column(String(20), index=True)  # e.g., "+1.5", "-2.75"
    lens_type = Column(SQLEnum(LensType))
    lens_index = Column(String(20))
    coating = Column(SQLEnum(CoatingType))
    stock_quantity = Column(Integer, default=0)
    reorder_level = Column(Integer, default=5)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    allocations = relationship("InventoryAllocation", back_populates="inventory")

class InventoryAllocation(Base):
    __tablename__ = "inventory_allocation"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    inventory_id = Column(Integer, ForeignKey("lens_inventory.id"))
    quantity = Column(Integer)
    allocated_at = Column(DateTime, default=datetime.utcnow)
    
    order = relationship("Order", back_populates="inventory_items")
    inventory = relationship("LensInventory", back_populates="allocations")

class OrderStatusLog(Base):
    __tablename__ = "order_status_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    old_status = Column(SQLEnum(OrderStatus))
    new_status = Column(SQLEnum(OrderStatus))
    reason = Column(Text, nullable=True)
    updated_by = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    order = relationship("Order", back_populates="status_logs")

class SLAMetrics(Base):
    __tablename__ = "sla_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    lens_type = Column(SQLEnum(LensType), unique=True)
    sla_hours = Column(Integer)  # Hours for delivery
    avg_completion_time = Column(Float)  # Average hours to complete
    breach_percentage = Column(Float)  # Historical breach %

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    alert_type = Column(String(50))  # breach_warning, breach_occurred, qc_failure
    message = Column(Text)
    priority = Column(String(20))  # high, medium, low
    is_sent = Column(Boolean, default=False)
    sent_via = Column(String(50), nullable=True)  # email, whatsapp, both
    created_at = Column(DateTime, default=datetime.utcnow)
    sent_at = Column(DateTime, nullable=True)
    
    order = relationship("Order", back_populates="alerts")

# Create tables
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()