# app/blueprints/feed/controllers/parsing.py

from app.utils.request_logger import get_logger, log_database_operation
from app.utils.error_exceptions import ValidationError, NotFoundError, DatabaseError
from app.utils.auth import get_current_auth0_id
from app.blueprints.feed.services import parse_and_update_feed, bulk_reparse_feeds
from flask import request, current_app
import threading

logger = get_logger(__name__)

# Helper functions
def maybe_run_async(target_func, *args, **kwargs):
    async_mode = request.args.get('async', '').lower() == 'true'
    if request.is_json:
        try:
            async_mode = async_mode or (request.get_json(silent=True) or {}).get('async', False)
        except Exception:
            pass

    if async_mode:
        app = current_app._get_current_object()
        
        # Capture request data before starting async thread
        request_data = None
        if request.is_json:
            try:
                request_data = request.get_json()
            except Exception:
                pass

        def runner():
            with app.app_context():
                try:
                    # Pass request data as payload if available
                    if request_data is not None:
                        target_func(payload=request_data, *args, **kwargs)
                    else:
                        target_func(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Async task failed: {str(e)}")

        threading.Thread(target=runner).start()
        return {"status": "queued"}

    return target_func(*args, **kwargs)


# Controllers
def reparse_feed_controller(feed_id: int) -> dict:
    return maybe_run_async(reparse_feed_controller_sync, feed_id)

def reparse_feed_controller_sync(feed_id: int) -> dict:
    """Synchronous implementation of feed reparse controller. 
    Returns:
        dict: Parsing result with status and metadata"""
        
    logger.info(f"Starting reparse for feed ID: {feed_id}")
    log_database_operation(logger, "UPDATE", "feeds", feed_id)
    
    auth0_id = get_current_auth0_id()
    logger.info(f"Reparsing feed {feed_id} by {'system' if auth0_id == 'system@podverse.com' else f'user {auth0_id}'}")
    
    from app.blueprints.feed.services import get_feed_by_id
    
    feed = get_feed_by_id(feed_id)
    if not feed:
        raise NotFoundError("Feed not found")
        
    if feed.is_parsing:
        logger.info(f"Feed {feed_id} is already being parsed — skipping reparse")
        raise ValidationError("Feed is already being parsed", status_code=409)

    if feed.flag_status.status.lower() not in ["active", "always-parse"]:
        logger.info(f"Skipping reparse — Feed {feed_id} not eligible (status={feed.flag_status.status})")
        raise ValidationError("Feed is not eligible for parsing", status_code=400)


    try:
        result = parse_and_update_feed(feed_id)
        logger.info(f"Reparse {'completed' if result.get('status') == 'success' else 'failed'} for feed ID: {feed_id}")
        return result
            
    except Exception as e:
        logger.error(f"Error reparsing feed {feed_id}: {str(e)}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise DatabaseError("Failed to reparse feed")

def bulk_reparse_feeds_controller() -> dict:
    return maybe_run_async(bulk_reparse_feeds_controller_sync)

def bulk_reparse_feeds_controller_sync(payload: dict = None) -> dict:
    logger.info("Starting bulk feed reparse")
    log_database_operation(logger, "UPDATE", "feeds", "bulk_reparse_attempt")

    data = payload or request.get_json()
    feed_ids = data.get("feed_ids")

    if not isinstance(feed_ids, list) or not feed_ids:
        raise ValidationError("feed_ids must be a non-empty list")

    result = bulk_reparse_feeds(feed_ids)

    logger.info(f"Bulk reparse completed - Success: {result['success']}, Failed: {result['failed']}, Not found: {result['not_found']}, Already parsing: {result['already_parsing']}")
    return result