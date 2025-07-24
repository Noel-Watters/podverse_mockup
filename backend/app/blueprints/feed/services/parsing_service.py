# app/blueprints/feed/services/parsing_service.py

from app.models.feed import Feed, FeedLog, FeedFlagStatus
from app.extensions import db
from app.utils.request_logger import get_logger
from app.utils.error_exceptions import NotFoundError, DatabaseError, ValidationError
from app.utils.auth import get_current_auth0_id
from datetime import datetime
import requests, traceback, random, time
from .node_trigger import normalize_feed_url

logger = get_logger(__name__)

def is_feed_eligible_for_reparse(feed) -> bool:
    """
    Returns True if the feed is eligible for reparsing based on its flag_status.status.
    """
    return feed.flag_status.status.lower() in ["active", "always-parse", "parse_error", "fetch_error"] 

def parse_and_update_feed_object(feed: Feed) -> dict:
    """
    Parse and update a feed object by calling the Node.js parser service.
    
    This function:
    1. Checks if the feed is already being parsed
    2. Sets the parsing flag and start time
    3. Calls the Node.js parser service
    4. Logs the result and updates the feed status
    5. Handles errors and rollback on failure
    """
    logger.info(f"Calling Node trigger for feed {feed.id}")
    start_time = datetime.utcnow() # Record start time for logging
    transaction_started = False # T=ry to start a transaction, but handle the case where one is already active
    http_status, message, result, is_success = None, None, None, False

    if feed.is_parsing:
        return {"status": "error", "message": "Already parsing", "feed_id": feed.id}

    try:
        feed.is_parsing = True
        db.session.flush()  # Flush to ensure the change is visible
    except Exception as e:
        logger.error(f"Failed to start transaction: {e}")
        raise DatabaseError("Failed to mark feed as parsing")

    payload = {"url": normalize_feed_url(feed.url)}
    if feed.channels:
        podcast_index_id = feed.channels[0].podcast_index_id
        if podcast_index_id:
            payload["podcast_index_id"] = podcast_index_id
        
    try:
        # retry 2 times if the request fails - can't do this with background task becaue I don;t own the parser celery task
        for attempt in range(2):
            try:
                response = requests.post("http://parse-service:3001/trigger-parse", json=payload, timeout=5)
                response.raise_for_status()
                break
            except Exception as e:
                logger.warning(f"Request error on attempt {attempt + 1}: {e}")
                if attempt == 1:
                    raise
                # exponential backoff with random jitter - base delay doubles on each try
                sleep_time = (2 ** attempt) + random.uniform(0, 1)
                time.sleep(sleep_time)

        result = response.json()
        is_success = result.get("success", False)
        message = result.get("message", None)
        http_status = response.status_code
        # If the parser service returned an error, provide a more descriptive message
        if not is_success:
            message = f"Parser service error: {message or 'No message provided'}"
    except Exception as e:
        logger.error(f"Error calling Node trigger: {str(e)}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        message = f"Parsing failed: {str(e)}"
        http_status = None   
        result = {"status": "error", "message": message, "feed_id": feed.id}
    finally:
        # Get the current user's Auth0 ID
        auth0_id = get_current_auth0_id()
        
        log = FeedLog(
            feed_id=feed.id,
            http_status=http_status,
            is_success=is_success,
            parse_error_message=message,
            started_at=start_time,
            finished_at=datetime.utcnow(),
            parsed_by=auth0_id if auth0_id else "system@podverse.com"
        )
        feed.is_parsing = False
        
        # Reset flag_status if parse succeeded from a failure state
        if is_success and feed.flag_status and feed.flag_status.status in ("parse_error", "fetch_error"):
            active_flag = db.session.query(FeedFlagStatus).filter_by(status="active").first()
            if active_flag:
                feed.flag_status = active_flag
                
        try:
            db.session.add(log)
            
            # Only commit if we started the transaction
            if transaction_started:
                db.session.commit()
            else:
                # If we didn't start the transaction, just flush to ensure changes are visible
                db.session.flush()        
        except Exception as e:
            if transaction_started:
                db.session.rollback()
            logger.error(f"Failed to save log or update feed: {e}")
            logger.error(f"Full traceback: {traceback.format_exc()}")
    
    # Ensure consistent result format
    if result is None:
        result = {"status": "error", "message": "No response from parser", "feed_id": feed.id}
    if "status" not in result:
        # If parser didn't return status, determine it from success flag
        result["status"] = "success" if is_success else "error"
        result["feed_id"] = feed.id
    return result


def parse_and_update_feed(feed_id: int) -> dict:
    """ Public function for single feed reparse (does DB lookup). """
    feed = db.session.get(Feed, feed_id)
    if not feed:
        raise NotFoundError("Feed not found")
    if feed.is_parsing:
        raise ValidationError("Feed is already being parsed", status_code=409)
    if not is_feed_eligible_for_reparse(feed):
        raise ValidationError(f"Feed is not eligible (status: {feed.flag_status.status})", status_code=400)
    
    result = parse_and_update_feed_object(feed)
    try:
        db.session.commit()  # FeedLog gets saved even if object function didn’t start txn
    except Exception as e:
        logger.error(f"Failed to commit after parsing feed {feed_id}: {e}")
        db.session.rollback()
    return result


# sequential since parsing is async on podverse side
def bulk_reparse_feeds(feed_ids: list) -> dict:
    """
    Reparse multiple feeds in bulk.
    
    This function processes feeds sequentially since parsing is async on the Podverse side.
    It provides detailed results for each feed including success, failure, and skip reasons.
    
    Args:
        feed_ids (list): List of feed IDs to reparse
    """
    results = {"success": 0, "failed": 0, "not_found": 0, "already_parsing": 0, "results": []}
    
    for feed_id in feed_ids:
        # Try to commit any pending work before processing each feed
        try:
            db.session.commit()
        except Exception as e:
            # No transaction to commit or other error, continue normally
            logger.debug(f"No transaction to commit or commit failed: {e}")
        
        try:
            result = parse_and_update_feed(feed_id)
            status = result.get("status", "error")
            results["results"].append({"feed_id": feed_id, "status": status})
            if status == "success":
                results["success"] += 1
            elif status == "error":
                results["failed"] += 1
        except NotFoundError:
            results["not_found"] += 1
            results["results"].append({"feed_id": feed_id, "status": "not_found"})
        except ValidationError as e:
            if "already" in str(e).lower():
                results["already_parsing"] += 1
                status = "already_parsing"
            else:
                status = "skipped_flag"
            results["results"].append({"feed_id": feed_id, "status": status})
        except Exception as e:
            logger.error(f"Error parsing feed {feed_id}: {e}")
            results["failed"] += 1
            results["results"].append({"feed_id": feed_id, "status": "error", "error": str(e)})

    results["total_requested"] = len(feed_ids)
    return results
