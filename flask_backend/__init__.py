from flask import Flask
from flask_cors import CORS
from flask_backend.Config import Config
from flask_backend.model import db
from flask_backend.routes import auth_bp

def create_app():
    # Initialize Flask app
    app = Flask(__name__)
    CORS(app)

    # Configure app from Config.py
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)

    # Register Blueprints
    app.register_blueprint(auth_bp)

    return app
