# app/blueprints/__init__.py

from flask import Blueprint

from app.blueprints.docs import docs_bp
from app.blueprints.channel import channel_bp
from app.blueprints.health import health_bp
from app.blueprints.feed import feed_bp
from app.blueprints.export_logs import export_logs_bp
from app.blueprints.item import item_bp
from app.blueprints.stats import stats_bp
from app.blueprints.report_builder import report_builder_bp


def register_blueprints(app):
    # Top-level /admin blueprint
    admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

    # All routes below will become /admin/<something>
    admin_bp.register_blueprint(channel_bp, url_prefix="/channels")
    admin_bp.register_blueprint(feed_bp, url_prefix="/feeds")
    admin_bp.register_blueprint(export_logs_bp, url_prefix="/export_logs")
    admin_bp.register_blueprint(item_bp, url_prefix="/items")
    admin_bp.register_blueprint(stats_bp, url_prefix="/stats")
    admin_bp.register_blueprint(docs_bp, url_prefix="/docs") # should i hide in production? if app.env != "production":
    admin_bp.register_blueprint(report_builder_bp, url_prefix="/reports")

    # Register the grouped admin routes
    app.register_blueprint(admin_bp)

    # Global routes (not under /admin)
    app.register_blueprint(health_bp)