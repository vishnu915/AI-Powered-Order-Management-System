from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.database import get_db, LensType, CoatingType
from app.services.inventory_service import InventoryService
from pydantic import BaseModel

router = APIRouter(prefix="/api/inventory", tags=["inventory"])

class LensStockRequest(BaseModel):
    lens_power: str
    lens_type: LensType
    lens_index: str
    coating: CoatingType
    quantity: int

@router.get("/lens/{lens_power}")
def check_lens_availability(
    lens_power: str,
    lens_type: LensType,
    lens_index: str,
    coating: CoatingType,
    db: Session = Depends(get_db)
):
    """Check if specific lens is available"""
    service = InventoryService(db)
    availability = service.check_availability(lens_power, lens_type, lens_index, coating)
    return availability

@router.post("/lens")
def add_lens_stock(stock_request: LensStockRequest, db: Session = Depends(get_db)):
    """Add lens to inventory"""
    service = InventoryService(db)
    item = service.add_stock(
        stock_request.lens_power,
        stock_request.lens_type,
        stock_request.lens_index,
        stock_request.coating,
        stock_request.quantity
    )
    return {"success": True, "item_id": item.id}

@router.get("/dashboard/summary")
def get_inventory_summary(db: Session = Depends(get_db)):
    """Get inventory dashboard summary"""
    service = InventoryService(db)
    return service.get_inventory_summary()

@router.get("/low-stock")
def get_low_stock_items(db: Session = Depends(get_db)):
    """Get items below reorder level"""
    service = InventoryService(db)
    items = service.get_low_stock_items()
    return [{"id": item.id, "power": item.lens_power, "quantity": item.stock_quantity} for item in items]