import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, GradientBoostingClassifier
from sklearn.preprocessing import LabelEncoder
import joblib
from datetime import datetime, timedelta
import os

class TATPredictor:
    """TAT (Turn Around Time) prediction model for orders"""
    
    def __init__(self):
        self.regressor = None  # TAT prediction
        self.classifier = None  # Breach prediction
        self.encoders = {}
    
    def train(self, data_path: str = None):
        """Train the model with historical data"""
        
        # Generate synthetic data for demo (replace with real data)
        df = self._generate_synthetic_data() if not data_path else pd.read_csv(data_path)
        
        # Feature engineering
        X, y_tat, y_breach = self._prepare_features(df)
        
        # Split data
        X_train, X_test, y_tat_train, y_tat_test, y_breach_train, y_breach_test = train_test_split(
            X, y_tat, y_breach, test_size=0.2, random_state=42
        )
        
        # Train TAT regressor
        self.regressor = RandomForestRegressor(n_estimators=100, random_state=42)
        self.regressor.fit(X_train, y_tat_train)
        
        # Train breach classifier
        self.classifier = GradientBoostingClassifier(n_estimators=100, random_state=42)
        self.classifier.fit(X_train, y_breach_train)
        
        # Evaluate
        tat_score = self.regressor.score(X_test, y_tat_test)
        breach_score = self.classifier.score(X_test, y_breach_test)
        
        print(f"TAT Model R² Score: {tat_score:.4f}")
        print(f"Breach Classifier Accuracy: {breach_score:.4f}")
        
        return self
    
    def predict_tat(self, features: dict) -> float:
        """Predict TAT in hours"""
        if not self.regressor:
            raise ValueError("Model not trained yet")
        
        X = self._extract_features_dict(features)
        return max(1, self.regressor.predict([X])[0])
    
    def predict_breach(self, features: dict) -> float:
        """Predict breach probability (0-1)"""
        if not self.classifier:
            raise ValueError("Model not trained yet")
        
        X = self._extract_features_dict(features)
        probabilities = self.classifier.predict_proba([X])
        return probabilities[0][1]  # Probability of breach
    
    def _generate_synthetic_data(self, n_samples: int = 1000) -> pd.DataFrame:
        """Generate synthetic order data for training"""
        np.random.seed(42)
        
        lens_types = ['single_vision', 'bifocal', 'progressive', 'photochromic']
        coatings = ['anti_reflective', 'scratch_resistant', 'blue_light', 'uv_protection', 'none']
        sources = ['online', 'store', 'partner']
        lens_indices = ['1.5', '1.56', '1.61', '1.67', '1.74']
        
        data = {
            'lens_type': np.random.choice(lens_types, n_samples),
            'coating': np.random.choice(coatings, n_samples),
            'source': np.random.choice(sources, n_samples),
            'lens_index': np.random.choice(lens_indices, n_samples),
            'hour_of_day': np.random.randint(0, 24, n_samples),
            'day_of_week': np.random.randint(0, 7, n_samples),
            'tat_hours': np.random.uniform(24, 72, n_samples),
            'was_breached': np.random.choice([0, 1], n_samples, p=[0.7, 0.3])
        }
        
        return pd.DataFrame(data)
    
    def _prepare_features(self, df: pd.DataFrame):
        """Prepare features for training"""
        df_copy = df.copy()
        
        # Encode categorical features
        categorical_cols = ['lens_type', 'coating', 'source', 'lens_index']
        for col in categorical_cols:
            encoder = LabelEncoder()
            df_copy[col] = encoder.fit_transform(df_copy[col])
            self.encoders[col] = encoder
        
        X = df_copy[['lens_type', 'coating', 'source', 'lens_index', 'hour_of_day', 'day_of_week']]
        y_tat = df_copy['tat_hours']
        y_breach = df_copy['was_breached']
        
        return X, y_tat, y_breach
    
    def _extract_features_dict(self, features: dict) -> list:
        """Extract and encode features from dict"""
        encoded_features = []
        
        # Encode categorical
        for col in ['lens_type', 'coating', 'source', 'lens_index']:
            encoder = self.encoders.get(col)
            val = features.get(col, 'unknown')
            if encoder:
                try:
                    encoded_features.append(encoder.transform([val])[0])
                except:
                    encoded_features.append(0)
            else:
                encoded_features.append(0)
        
        # Add numeric features
        encoded_features.append(features.get('hour_of_day', datetime.utcnow().hour))
        encoded_features.append(features.get('day_of_week', datetime.utcnow().weekday()))
        
        return encoded_features
    
    def save(self, path: str):
        """Save model to disk"""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump({
            'regressor': self.regressor,
            'classifier': self.classifier,
            'encoders': self.encoders
        }, path)
        print(f"Model saved to {path}")
    
    def load(self, path: str):
        """Load model from disk"""
        if os.path.exists(path):
            data = joblib.load(path)
            self.regressor = data['regressor']
            self.classifier = data['classifier']
            self.encoders = data['encoders']
            print(f"Model loaded from {path}")
            return self
        raise FileNotFoundError(f"Model not found at {path}")

# Training script
if __name__ == "__main__":
    predictor = TATPredictor()
    predictor.train()
    predictor.save("./models/tat_predictor.pkl")