#/app/config/config.py
from datetime import timedelta

class Config:
    SECRET_KEY = 'taskora_secret_key'
    JWT_SECRET_KEY = 'taskora_secret_key'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=3)
    MONGO_URI = 'mongodb+srv://admin:admin@cluster0.ofbp53b.mongodb.net/taskora'
    URI_PREFIX = 'api/v1/dev'