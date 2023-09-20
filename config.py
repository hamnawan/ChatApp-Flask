# config.py
from datetime import timedelta


class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///your_database.db'
    SECRET_KEY = 'your-secret-key'
    JWT_SECRET_KEY = 'your-jwt-secret-key'
    JWT_EXPIRATION_DELTA = timedelta(hours=1)
