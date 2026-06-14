from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List
from enum import Enum

class LensType(str, Enum):
    SINGLE_VISION = "single_vision"
    BIFOCAL = "bifocal"
    PROGRESSIVE = "progressive"
    PHOTOCHROMIC = "photochromic"

class CoatingType(str, Enum):
    ANTI_REFLECTIVE = "anti_reflective"
    SCRATCH_RESISTANT = "scratch_resistant"
    BLUE_LIGHT = "blue_light"
    UV_PROTECTION = "uv_protection"
    NONE = "none"

class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    LENS_ORDERED = "lens_ordered"
    QC_PASS = "qc_pass"
    QC_FAIL = "qc_fail"
    READY_FOR_DISPATCH = "ready_for_dispatch"
    DISPATCHED = "dispatched"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class OrderCreate(BaseModel):
    customer_name: str
    customer_email: EmailStr
    customer_phone: str
    
    # Prescription
    left_eye_power: float
    right_eye_power: float
    cylinder: Optional[float] = None
    axis: Optional[float] = None
    
    # Lens Details
    lens_type: LensType
    lens_index: str
    coating: CoatingType
    frame_type: str
    
    # Order Details
    source: str  # online, store, partner
    store_location: str

class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    notes: Optional[str] = None
    qc_fail_reason: Optional[str] = None

class OrderResponse(BaseModel):
    id: int
    order_id: str
    customer_name: str
    customer_email: str
    status: OrderStatus
    lens_type: LensType
    left_eye_power: float
    right_eye_power: float
    order_date: datetime
    expected_delivery_date: datetime
    actual_delivery_date: Optional[datetime]
    sla_hours: int
    
    class Config:
        from_attributes = True

class OrderDetailResponse(OrderResponse):
    customer_phone: str
    lens_index: str
    coating: CoatingType
    frame_type: str
    cylinder: Optional[float]
    axis: Optional[float]
    source: str
    store_location: str
    notes: Optional[str]
    qc_fail_reason: Optional[str]