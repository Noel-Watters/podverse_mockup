# app/blueprints/feed/services/parsing_service.py

from app.models.feed import Feed, FeedLog
from app.extensions import db
from app.utils.request_logger import get_logger
from app.utils.error_exceptions import NotFoundError, DatabaseError
from app.utils.auth import get_current_auth0_id
from datetime import datetime
import requests
import traceback
import random
import time
from .node_trigger import normalize_feed_url

logger = get_logger(__name__)

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
    
    channel = feed.channels[0] if feed.channels else None
    podcast_index_id = channel.podcast_index_id if channel else None

    if feed.is_parsing:
        return {"status": "error", "message": "Already parsing", "feed_id": feed.id}

    # Record start time for logging
    start_time = datetime.utcnow()
    
    # T=ry to start a transaction, but handle the case where one is already active
    transaction_started = False
    try:
        # Try to start a new transaction
        try:
            db.session.begin()
            transaction_started = True
        except Exception as e:
            # Transaction might already be active, continue without starting a new one
            logger.debug(f"Could not start new transaction (might already be active): {e}")
            transaction_started = False
        
        feed.is_parsing = True
        db.session.flush()  # Flush to ensure the change is visible
        
    except Exception as e:
        logger.error(f"Failed to set is_parsing flag: {e}")
        if transaction_started:
            db.session.rollback()
        raise DatabaseError("Failed to mark feed as parsing")

    result = None
    
    payload = {"url": normalize_feed_url(feed.url)}
    if podcast_index_id is not None:
        payload["podcast_index_id"] = podcast_index_id
        
    try:
        # retry 2 times if the request fails - can't do this with background task becaue I don;t own the parser celery task
        for attempt in range(2):
            try:
                response = requests.post("http://parse-service:3001/trigger-parse", json=payload, timeout=5)
                response.raise_for_status()
                break
            except requests.Timeout as e:
                logger.warning(f"Timeout on attempt {attempt + 1}: {e}")
                if attempt == 1:
                    raise
            except requests.ConnectionError as e:
                logger.warning(f"Connection error on attempt {attempt + 1}: {e}")
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
            if message:
                message = f"Parser service error: {message}"
            else:
                message = "Parser service returned an error but no message was provided."

    except Exception as e:
        logger.error(f"Error calling Node trigger: {str(e)}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        
        # Provide more descriptive error messages based on exception type
        if isinstance(e, requests.Timeout):
            message = "Parser request timed out: The parsing service did not respond within the expected time limit."
        elif isinstance(e, requests.ConnectionError):
            message = "Connection error: Unable to connect to the parsing service. The service may be down or unreachable."
        elif isinstance(e, requests.HTTPError):
            if e.response.status_code == 404:
                message = "HTTP 404 Not Found: The requested RSS feed URL could not be located."
            elif e.response.status_code == 403:
                message = "Access Denied: HTTP 403 Forbidden. Server is blocking feed requests."
            elif e.response.status_code == 500:
                message = "Server Error: HTTP 500 Internal Server Error. The parsing service encountered an error."
            else:
                message = f"HTTP Error {e.response.status_code}: {e.response.reason}"
        else:
            message = f"Parsing failed: {str(e)}"
        
        result = {"status": "error", "error": str(e), "feed_id": feed.id}
        is_success = False
        http_status = getattr(e, 'response', {}).status_code if hasattr(e, 'response') else None

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
        try:
            db.session.add(log)
            feed.is_parsing = False
            
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
    elif "status" not in result:
        # If parser didn't return status, determine it from success flag
        if is_success:
            result["status"] = "success"
        else:
            result["status"] = "error"
        result["feed_id"] = feed.id
    
    return result


def parse_and_update_feed(feed_id: int):
    """ Public function for single feed reparse (does DB lookup). """
    feed = db.session.get(Feed, feed_id)
    if not feed:
        raise NotFoundError("Feed not found")
    
    return parse_and_update_feed_object(feed)


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
        try:
            # Try to commit any pending work before processing each feed
            try:
                db.session.commit()
            except Exception as e:
                # No transaction to commit or other error, continue normally
                logger.debug(f"No transaction to commit or commit failed: {e}")
            
            feed = db.session.get(Feed, feed_id)
            if not feed:
                results["not_found"] += 1
                results["results"].append({"feed_id": feed_id, "status": "not_found"})
                continue
                
            if feed.flag_status.status.lower() not in ["active", "always-parse"]:
                results["results"].append({"feed_id": feed_id, "status": "skipped_flag"})
                continue
            if feed.is_parsing:
                results["already_parsing"] += 1
                results["results"].append({"feed_id": feed_id, "status": "already_parsing"})
                continue
                
            result = parse_and_update_feed(feed_id)
            status = result.get("status")
            
            # Handle different status values
            if status == "success":
                results["success"] += 1
            elif status == "error":
                results["failed"] += 1
            else:
                # Default to failed for unknown status
                results["failed"] += 1
                status = "error"
                
            results["results"].append({"feed_id": feed_id, "status": status})
            
        except NotFoundError:
            results["not_found"] += 1
            results["results"].append({"feed_id": feed_id, "status": "not_found"})
        except Exception as e:
            logger.error(f"Error processing feed {feed_id}: {str(e)}")
            logger.error(f"Full traceback: {traceback.format_exc()}")
            results["failed"] += 1
            results["results"].append({"feed_id": feed_id, "status": "error", "error": str(e)})
    
    results["total_requested"] = len(feed_ids)
    return results 