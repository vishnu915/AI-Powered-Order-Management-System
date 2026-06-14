import joblib
import numpy as np
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.database import Order, OrderStatus, SLAMetrics
import os

class MLService:
    def __init__(self, model_path: str = "./ml/models/tat_predictor.pkl"):
        self.model_path = model_path
        self.model = self._load_model()
    
    def _load_model(self):
        """Load pre-trained TAT prediction model"""
        if os.path.exists(self.model_path):
            return joblib.load(self.model_path)
        return None
    
    def predict_tat(self, order: Order) -> float:
        """Predict Turn Around Time in hours"""
        if not self.model:
            return order.sla_hours
        
        # Extract features
        features = self._extract_features(order)
        
        # Predict
        tat_hours = self.model.predict([features])[0]
        return max(1, tat_hours)
    
    def predict_breach_probability(self, order: Order, db: Session) -> float:
        """Predict probability of SLA breach (0-1)"""
        if not self.model:
            return 0.0
        
        features = self._extract_features(order)
        
        # Use probability prediction
        try:
            probabilities = self.model.predict_proba([features])
            # Assuming 1 = breach, 0 = no breach
            return probabilities[0][1] if len(probabilities[0]) > 1 else 0.0
        except:
            return 0.0
    
    def _extract_features(self, order: Order) -> list:
        """Extract features for ML model"""
        # Features: lens_type, coating, lens_index, source, hour_of_day, day_of_week
        features = [
            self._encode_lens_type(order.lens_type),
            self._encode_coating(order.coating),
            self._encode_lens_index(order.lens_index),
            self._encode_source(order.source),
            datetime.utcnow().hour,
            datetime.utcnow().weekday()
        ]
        return features
    
    @staticmethod
    def _encode_lens_type(lens_type):
        mapping = {
            "single_vision": 0,
            "bifocal": 1,
            "progressive": 2,
            "photochromic": 3
        }
        return mapping.get(lens_type, 0)
    
    @staticmethod
    def _encode_coating(coating):
        mapping = {
            "anti_reflective": 0,
            "scratch_resistant": 1,
            "blue_light": 2,
            "uv_protection": 3,
            "none": 4
        }
        return mapping.get(coating, 4)
    
    @staticmethod
    def _encode_lens_index(lens_index):
        mapping = {
            "1.5": 0,
            "1.56": 1,
            "1.61": 2,
            "1.67": 3,
            "1.74": 4
        }
        return mapping.get(lens_index, 0)
    
    @staticmethod
    def _encode_source(source):
        mapping = {
            "online": 0,
            "store": 1,
            "partner": 2
        }
        return mapping.get(source, 0)