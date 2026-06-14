from sqlalchemy.orm import Session
from app.models.database import LensInventory, LensType, CoatingType

class InventoryService:
    def __init__(self, db: Session):
        self.db = db
    
    def check_availability(self, lens_power: str, lens_type: LensType, 
                          lens_index: str, coating: CoatingType):
        """Check if specific lens is in stock"""
        item = self.db.query(LensInventory).filter(
            LensInventory.lens_power == lens_power,
            LensInventory.lens_type == lens_type,
            LensInventory.lens_index == lens_index,
            LensInventory.coating == coating
        ).first()
        
        return {
            "available": item.stock_quantity > 0 if item else False,
            "quantity": item.stock_quantity if item else 0,
            "reorder_level": item.reorder_level if item else 5
        }
    
    def add_stock(self, lens_power: str, lens_type: LensType, 
                  lens_index: str, coating: CoatingType, quantity: int):
        """Add lens stock"""
        item = self.db.query(LensInventory).filter(
            LensInventory.lens_power == lens_power,
            LensInventory.lens_type == lens_type,
            LensInventory.lens_index == lens_index,
            LensInventory.coating == coating
        ).first()
        
        if item:
            item.stock_quantity += quantity
        else:
            item = LensInventory(
                lens_power=lens_power,
                lens_type=lens_type,
                lens_index=lens_index,
                coating=coating,
                stock_quantity=quantity
            )
            self.db.add(item)
        
        self.db.commit()
        return item
    
    def get_low_stock_items(self):
        """Get items below reorder level"""
        return self.db.query(LensInventory).filter(
            LensInventory.stock_quantity <= LensInventory.reorder_level
        ).all()
    
    def get_inventory_summary(self):
        """Get inventory dashboard summary"""
        items = self.db.query(LensInventory).all()
        
        return {
            "total_items": len(items),
            "total_quantity": sum(item.stock_quantity for item in items),
            "low_stock_items": len([i for i in items if i.stock_quantity <= i.reorder_level]),
            "by_lens_type": self._group_by_lens_type(items)
        }
    
    @staticmethod
    def _group_by_lens_type(items):
        grouped = {}
        for item in items:
            if item.lens_type not in grouped:
                grouped[item.lens_type] = 0
            grouped[item.lens_type] += item.stock_quantity
        return grouped