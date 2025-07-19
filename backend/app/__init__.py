# backend/app/__init__.py

from flask import Flask
from app.extensions import ma, db, limiter, migrate
from app.blueprints import register_blueprints
from flask_cors import CORS
from flask_talisman import Talisman
from config import config_by_name
from app.utils.request_logger import register_logging
from app.utils.error_handlers import register_error_handlers
import os
from dotenv import load_dotenv

load_dotenv()

def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "development")
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # Minimal but essential security headers
    Talisman(
        app,
        content_security_policy={
            'default-src': ["'self'"],
            'script-src': ["'self'", 'https://unpkg.com'],
            'style-src': ["'self'", 'https://unpkg.com'],
            'img-src': ["'self'", "data:", "https:", "https://cdn-images-3.listennotes.com"],
            'font-src': ["'self'", 'https://fonts.gstatic.com'],
            'frame-src': ["'none'"],
            'object-src': ["'none'"],
        },
        force_https=config_name == "production",  # Auto-enable HTTPS in production
        strict_transport_security=True,
        strict_transport_security_max_age=31536000,
        referrer_policy='strict-origin-when-cross-origin'
    )

    # initialize extensions
    ma.init_app(app)
    db.init_app(app)
    limiter.init_app(app)
    migrate.init_app(app, db)

    
    # secure CORS configuration for frontend-backend communication
    CORS(app, 
         origins=os.getenv("CORS_ORIGINS", "").split(","), # Allow both local and Docker network access
         supports_credentials=True,
         allow_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    )
    
    register_logging(app)
    
    register_error_handlers(app)
    register_blueprints(app)

    return app