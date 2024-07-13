# /app/services/database.py
from flask_pymongo import PyMongo

mongo = PyMongo()

def init_db(app):
    """
    init connection for MongoDB.
    """
    mongo.init_app(app)