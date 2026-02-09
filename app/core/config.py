from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "AI Website Analyzer"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str
    API_V1_PREFIX: str = "/api/v1"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database
    MONGODB_URL: str
    MONGODB_DB_NAME: str = "website_analyzer"
    
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Google Gemini
    GOOGLE_API_KEY: str
    GEMINI_MODEL: str = "gemini-2.0-flash-exp"
    GEMINI_TEMPERATURE: float = 0.7
    GEMINI_MAX_TOKENS: int = 8192
    
    # Google Drive
    GOOGLE_DRIVE_CREDENTIALS_FILE: str = "service-account-key.json"
    GOOGLE_DRIVE_FOLDER_ID: str = ""
    
    # Rate Limiting
    RATE_LIMIT_FREE_USER: int = 1
    RATE_LIMIT_BASIC_USER: int = 10
    RATE_LIMIT_PRO_USER: int = 100
    RATE_LIMIT_ENTERPRISE_USER: int = 1000
    RATE_LIMIT_WINDOW_HOURS: int = 24
    
    # Analysis
    MAX_ANALYSIS_TIME_SECONDS: int = 300
    SCREENSHOT_WIDTH: int = 1920
    SCREENSHOT_HEIGHT: int = 1080
    LIGHTHOUSE_TIMEOUT: int = 60
    
    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = "noreply@websiteanalyzer.com"
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # File Upload
    MAX_UPLOAD_SIZE_MB: int = 10
    
    # Frontend
    FRONTEND_URL: str = "http://localhost:8000"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
