# app/blueprints/feed/services/bulk_service.py

from app.models.feed import Feed, FeedFlagStatus
from app.extensions import db
from app.utils.request_logger import get_logger, log_database_operation
from app.utils.security_logger import log_error
from app.utils.error_exceptions import ValidationError, DatabaseError
from datetime import datetime
import traceback

logger = get_logger(__name__)

def bulk_update_feeds(feed_ids: list, updates: dict):
    """Update multiple feeds with the provided changes.
    
    Args:
        feed_ids (list): List of feed IDs to update
        updates (dict): Dictionary of fields to update with their new values
        
    Returns:
        dict: Update results with counts:
            - "updated": Number of successfully updated feeds
            - "not_found": Number of feeds not found
            - "total_requested": Total number of feeds requested for update
    """
    updated_count = 0
    not_found_count = 0
    results = []
    
    try:
        logger.info(f"Starting bulk update for {len(feed_ids)} feeds")
        log_database_operation(logger, "UPDATE", "feeds", f"bulk_update_{len(feed_ids)}")
        
        # Validate updates
        valid_fields = {
            'feed_flag_status_id', 
            'parsing_priority', 
            'container_id' # internal grouping like regions etc
        }
        if not set(updates.keys()).issubset(valid_fields): # set to check if all keys are in the valid fields
            invalid_fields = set(updates.keys()) - valid_fields
            raise ValidationError(f"Invalid update fields: {invalid_fields}")
        
        # Validate feed_flag_status_id if provided
        if 'feed_flag_status_id' in updates:
            flag_status = db.session.get(FeedFlagStatus, updates['feed_flag_status_id'])
            if not flag_status:
                raise ValidationError(f"Invalid feed_flag_status_id: {updates['feed_flag_status_id']}")
        
        # go through each feed and update the feed object
        for feed_id in feed_ids:
            feed = db.session.get(Feed, feed_id)
            if not feed:
                not_found_count += 1
                logger.warning(f"Feed not found: ID {feed_id}")
                results.append({"feed_id": feed_id, "status": "not_found"})
                continue

            for field, value in updates.items():
                if hasattr(feed, field):
                    setattr(feed, field, value)

            feed.updated_at = datetime.utcnow()
            updated_count += 1
            results.append({"feed_id": feed_id, "status": "updated"})

        db.session.commit()
        
        logger.info(f"Bulk update completed: {updated_count} updated, {not_found_count} not found")
        return {
            "updated": updated_count,
            "not_found": not_found_count,
            "total_requested": len(feed_ids),
            "results": results
        }
        
    except ValidationError:
        raise
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error in bulk_update_feeds: {str(e)}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        log_error("bulk_update_feeds", "unknown", e)
        raise DatabaseError(f"Failed to bulk update feeds: {str(e)}") 