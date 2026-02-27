import os
from typing import Optional

class Config:
    # Database
    DATABASE_URL: str = "sqlite:///./tickets_v3.db"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # Application
    APP_NAME: str = "IT Support Portal"
    VERSION: str = "1.0.0"
    
    # Paths
    TEMPLATES_DIR: str = "templates"
    STATIC_DIR: str = "static"
    
    # Default Users
    DEFAULT_USERS = [
        {"username": "staff", "password": "password123"},
        {"username": "it", "password": "itadmin123"}
    ]
    
    # Sample Tickets
    SAMPLE_TICKETS = [
        {"name": "John Doe", "issue": "Computer won't start", "status": "Open", "priority": "High"},
        {"name": "Jane Smith", "issue": "Email not working", "status": "In Progress", "priority": "Medium"},
        {"name": "Bob Johnson", "issue": "Printer offline", "status": "Closed", "priority": "Low"}
    ]

# Create global config instance
config = Config()