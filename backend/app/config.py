import os
from functools import lru_cache
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API
    app_name: str = "Eyewear Order Management API"
    debug: bool = os.getenv("DEBUG", "False") == "True"
    
    # Database
    mysql_url: str = os.getenv("MYSQL_URL", "mysql+pymysql://root:password@localhost:3306/eyewear_db")
    
    # Redis
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # OpenAI
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    
    # Twilio
    twilio_account_sid: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    twilio_auth_token: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    twilio_phone: str = os.getenv("TWILIO_PHONE", "")
    
    # SendGrid
    sendgrid_api_key: str = os.getenv("SENDGRID_API_KEY", "")
    sendgrid_from_email: str = os.getenv("SENDGRID_FROM_EMAIL", "noreply@eyewear.com")
    
    # ML Model
    ml_model_path: str = os.getenv("ML_MODEL_PATH", "./ml/models/tat_predictor.pkl")
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()