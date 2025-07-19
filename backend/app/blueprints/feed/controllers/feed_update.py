# app/blueprints/feed/controllers/bulk.py

from app.utils.request_logger import get_logger, log_database_operation
from app.utils.error_exceptions import ValidationError, DatabaseError
from app.blueprints.feed.services import bulk_update_feeds
from flask import request

logger = get_logger(__name__)

def bulk_update_feeds_controller() -> dict:
    """Controller to handle bulk update of feeds."""
    try:
        logger.info("Starting bulk feed update")
        log_database_operation(logger, "UPDATE", "feeds", "bulk_update_attempt")
        
        data = request.get_json()
        if not data:
            raise ValidationError("Request body is required")
        
        feed_ids = data.get("feed_ids")
        updates = data.get("updates")
        
        if not isinstance(feed_ids, list) or not feed_ids:
            raise ValidationError("feed_ids must be a non-empty list")
        
        if not isinstance(updates, dict) or not updates:
            raise ValidationError("updates must be a non-empty object")
        
        logger.info(f"Bulk updating {len(feed_ids)} feeds with updates: {list(updates.keys())}")
        
        result = bulk_update_feeds(feed_ids, updates)
        
        logger.info(f"Bulk update completed - Updated: {result['updated']}, Not found: {result['not_found']}")
        
        return result

    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Bulk update error: {str(e)}")
        raise DatabaseError("Failed to bulk update feeds") 