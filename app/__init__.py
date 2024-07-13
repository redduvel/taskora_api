# app/__init__.py
from flask import Flask
from app.config.config import Config
from app.services.database import init_db
from flask_jwt_extended import JWTManager

from app.api.auth.routes import auth_blueprint


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    jwt = JWTManager(app)
    init_db(app)

    # Регистрация blueprints
    app.register_blueprint(auth_blueprint, url_prefix = '/auth')

    return app