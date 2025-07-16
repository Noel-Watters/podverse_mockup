# app/blueprints/feed/services.py

# NOTE: The real parser (parseRSSFeedAndSaveToDatabase) should be called from the Node service here.
# Current implementation fakes this via Express stub. See: podverse-parse-service/index.js


from app.models.feed import Feed, FeedFlagStatus, FeedLog
from app.models.channel import Channel
from app.extensions import db
from app.utils.request_logger import get_logger, log_database_operation
from app.utils.security_logger import log_error
from app.utils.query_helpers import paginate_query, apply_sorting
from app.utils.error_exceptions import NotFoundError, ValidationError, DatabaseError
from datetime import datetime
import urllib.parse
from sqlalchemy import or_
import requests
from app.blueprints.feed.schemas import feeds_export_schema
from flask import _request_ctx_stack
import traceback
import random

logger = get_logger(__name__)
import time

#HELPER FUNCTIONS
def get_flag_status_id(status: str) -> int:
    """
    Get the ID of a feed flag status by its status string.
    Args:
        status (str): The status string to look up    
    Returns:
        int: The ID of the FeedFlagStatus record

    """
    from app.models.feed import FeedFlagStatus
    record = db.session.query(FeedFlagStatus).filter_by(status=status).first()
    if not record:
        raise RuntimeError(f"FeedFlagStatus '{status}' not found")
    return record.id

def get_current_auth0_id() -> str:
    """
    Get the current user's Auth0 ID from the Flask request context.
    
    Returns:
        str: The Auth0 user ID (sub claim) or "flask" as fallback
    """
    try:
        if hasattr(_request_ctx_stack.top, 'current_user'):
            return _request_ctx_stack.top.current_user.get('sub', 'flask')
    except Exception:
        pass
    return 'flask'

def normalize_feed_url(url: str) -> str: 
    """
    Normalize a feed URL for consistent storage and comparison.
    - Force HTTPS
    - Remove trailing slashes
    - Lowercase the scheme and host
    
    Args:
        url (str): The URL to normalize
        
    Returns:
        str: The normalized URL
    """
    parsed = urllib.parse.urlparse(url.strip())
    scheme = 'https'
    # Normalize host to lowercase
    netloc = parsed.netloc.lower()
    # Normalize path (remove trailing slash)
    path = parsed.path.rstrip('/')
    # Reconstruct URL
    normalized_url = urllib.parse.urlunparse((
        scheme,
        netloc,
        path,
        '',  # params
        '',  # query
        ''   # fragment
    ))
    return normalized_url

def trigger_node_parser(url: str, podcast_index_id: int = None):
    """
    Trigger the Node.js parser service to parse a feed.
    
    Args:
        url (str): The feed URL to parse
        podcast_index_id (int, optional): The podcast index ID
        
    Returns:
        dict: The response from the parser service
        
    Raises:
        requests.RequestException: If the request fails after retries
    """
    for attempt in range(2):  # 1 retry
        try:
            payload = {"url": url}
            if podcast_index_id is not None:
                payload["podcast_index_id"] = podcast_index_id
                            
            response = requests.post("http://parse-service:3001/trigger-parse", json=payload, timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            if attempt == 1:
                raise
            time.sleep(1)


#SERVICE FUNCTIONS

def parse_and_update_feed_object(feed: Feed) -> dict:
    """
    Parse and update a feed object by calling the Node.js parser service.
    
    This function:
    1. Checks if the feed is already being parsed
    2. Sets the parsing flag and start time
    3. Calls the Node.js parser service
    4. Logs the result and updates the feed status
    5. Handles errors and rollback on failure
    
    Args:
        feed (Feed): The feed object to parse
        
    Returns:
        dict: The parsing result with status and metadata
        
    Raises:
        ValidationError: If feed is already parsing or not eligible
        DatabaseError: If database operations fail
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
                message = "Parser request timed out"
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

    except Exception as e:
        logger.error(f"Error calling Node trigger: {str(e)}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        result = {"status": "error", "error": str(e), "feed_id": feed.id}
        is_success = False
        message = str(e)
        http_status = None

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
    """
    Public function for single feed reparse (does DB lookup).
    
    Args:
        feed_id (int): The ID of the feed to parse
        
    Returns:
        dict: The parsing result
        
    Raises:
        NotFoundError: If the feed is not found
    """
    feed = db.session.get(Feed, feed_id)
    if not feed:
        raise NotFoundError("Feed not found")
    
    return parse_and_update_feed_object(feed)
        

def get_all_feeds(page=1, limit=10, parsing_priority=None, is_parsing=None, status=None, feed_id=None, podcast_index_id=None, sort_by="id", sort_order="desc", search=None):
    """
    Get all feeds with pagination and return structured response.
    
    This function supports:
    - Pagination with page and limit parameters
    - Filtering by parsing priority, parsing status, feed status, feed ID, and podcast index ID
    - Search functionality across feed ID, URL, channel title, and podcast index ID
    - Dynamic sorting with validation
    - Comprehensive error handling and logging
    
    Args:
        page (int): Page number for pagination (default: 1)
        limit (int): Number of items per page (default: 10)
        parsing_priority (int, optional): Filter by parsing priority
        is_parsing (bool, optional): Filter by parsing status
        status (str, optional): Filter by feed flag status
        feed_id (int, optional): Filter by specific feed ID
        podcast_index_id (int, optional): Filter by podcast index ID
        sort_by (str): Field to sort by (default: "id")
        sort_order (str): Sort order - "asc" or "desc" (default: "desc")
        search (str, optional): Search term for ID, URL, title, or podcast_index_id
        
    Returns:
        dict: Dictionary containing "data" (list of feeds) and "meta" (pagination info)
        
    Raises:
        ValidationError: If parameters are invalid
        DatabaseError: If database operations fail
    """
    try:
        # Create base query with left join to Channel for title search
        query = db.session.query(Feed).join(FeedFlagStatus).outerjoin(Channel).order_by(Feed.id.desc())
        log_database_operation(logger, "READ", "feeds", f"page_{page}_limit_{limit}")
             
        if status:
            query = query.filter(FeedFlagStatus.status == status)
            logger.info(f"Filtering feeds by status: {status}")

        if parsing_priority is not None:
            try:
                priority_int = int(parsing_priority)
                if priority_int < 0:
                    raise ValidationError("parsing_priority must be non-negative")
                query = query.filter(Feed.parsing_priority == priority_int)
                logger.info(f"Filtering feeds by parsing_priority: {priority_int}")
            except (ValueError, TypeError):
                raise ValidationError("parsing_priority must be a valid integer")

        if is_parsing is not None:
            if isinstance(is_parsing, str):
                is_parsing = is_parsing.lower() == "true"
            query = query.filter(Feed.is_parsing == is_parsing)
            logger.info(f"Filtering feeds by is_parsing: {is_parsing}")
            
        if feed_id is not None:
            query = query.filter(Feed.id == feed_id)
            logger.info(f"Filtering feeds by ID: {feed_id}")
            
        if podcast_index_id is not None:
            try:
                podcast_index_int = int(podcast_index_id)
                if podcast_index_int < 0:
                    raise ValidationError("podcast_index_id must be non-negative")
                query = query.filter(Channel.podcast_index_id == podcast_index_int)
                logger.info(f"Filtering feeds by podcast_index_id: {podcast_index_int}")
            except (ValueError, TypeError):
                raise ValidationError("podcast_index_id must be a valid integer")
            
        if search:
            # Enhanced search: ID (exact), URL (exact), Channel title (partial), or podcast_index_id (exact)
            search_conditions = []
            
            normalized_search = search.strip()
            try:
                search_id = int(normalized_search)
                search_conditions.append(Feed.id == search_id)
                search_conditions.append(Channel.podcast_index_id == search_id)
            except ValueError:
                pass  # Not a valid integer, skip ID and podcast_index_id search
            
            # Exact URL match (normalized)
            if normalized_search.startswith("http"):
                normalized_url = normalize_feed_url(normalized_search)
                search_conditions.append(Feed.url == normalized_url)
            else:
                # Partial match fallback
                search_conditions.append(Feed.url.ilike(f"%{normalized_search}%"))
                search_conditions.append(Channel.title.ilike(f"%{normalized_search}%"))

            # Combine with OR
            query = query.filter(or_(*search_conditions))
            logger.info(f"Filtering feeds by search term (ID/URL/title/podcast_index_id): {search}")
            
        # Safe dynamic sorting
        query = apply_sorting(query, Feed, sort_by, sort_order)
        # Use existing pagination helper
        feeds, pagination_meta = paginate_query(query, page, limit)
        
        logger.info(f"Retrieved {len(feeds)} feeds for page {page}")
        return {
            "data": feeds,
            "meta": pagination_meta
        }
        
    except Exception as e:
        logger.error(f"Error in get_all_feeds: {str(e)}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        log_error("get_all_feeds", e)
        raise DatabaseError(f"Failed to retrieve feeds: {str(e)}")


def get_feed_by_id(feed_id: int):
    """
    Get a single feed by its ID.
    
    Args:
        feed_id (int): The ID of the feed to retrieve
        
    Returns:
        Feed: The feed object
        
    Raises:
        NotFoundError: If the feed is not found
    """
    feed = db.session.get(Feed, feed_id)
    log_database_operation(logger, "READ", "feeds", record_id=feed_id)
    if not feed:
        logger.warning(f"Feed not found: ID {feed_id}")
        raise NotFoundError("Feed not found")
    return feed


def get_feed_logs(feed_id: int):
    """
    Get all logs for a specific feed, sorted by finished_at.
    
    Args:
        feed_id (int): ID of the feed to get logs for
        
    Returns:
        list: List of FeedLog objects sorted by finished_at (descending)
        
    Raises:
        NotFoundError: If the feed is not found
        DatabaseError: If database operations fail
    """
    try:
        # Check if feed exists
        feed = db.session.get(Feed, feed_id)
        if not feed:
            logger.warning(f"Feed not found when fetching logs: ID {feed_id}")
            raise NotFoundError("Feed not found")

        # Get all logs for the feed, sorted by finished_at
        logs = (
            db.session.query(FeedLog)
            .filter(FeedLog.feed_id == feed_id)
            .order_by(FeedLog.finished_at.desc())
            .all()
        )
        
        logger.info(f"Retrieved {len(logs)} logs for feed ID {feed_id}")
        return logs
        
    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error in get_feed_logs: {str(e)}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        log_error("get_feed_logs", e)
        raise DatabaseError(f"Failed to retrieve feed logs: {str(e)}")
 

#MARK: bulk endpoints

def get_feeds_for_export(search=None, sort_by='id', sort_order='asc', max_rows=None, feed_id=None, podcast_index_id=None):
    """
    Retrieve feeds for export with optional search and sorting.
    
    This function is optimized for export operations:
    - No pagination, but limited to max_rows for performance
    - Eager loading of relationships to avoid N+1 queries
    - Enhanced search functionality 
    - Serialized output ready for export
    
    Args:
        search (str, optional): Search term to filter by ID (exact), URL (partial), or channel title (partial)
        sort_by (str): Field to sort by (default: 'id')
        sort_order (str): Sort order (default: 'asc')
        max_rows (int, optional): Maximum number of rows to export (default: 10000)
        feed_id (int, optional): Optional feed ID to filter by
        podcast_index_id (int, optional): Optional podcast index ID to filter by
        
    Returns:
        list: List of serialized feed dictionaries ready for export
    """
    try:
        # Create base query with eager loading of relationships
        query = db.session.query(Feed).join(FeedFlagStatus).outerjoin(Channel).options(
            db.joinedload(Feed.channels),
            db.joinedload(Feed.logs),
            db.joinedload(Feed.flag_status)
        ).order_by(Feed.id.desc())
        log_database_operation(logger, "READ", "feeds", f"export_max_{max_rows}")
        
        # Add ID filter if provided
        if feed_id is not None:
            query = query.filter(Feed.id == feed_id)
            logger.info(f"Export query filtering by feed ID: {feed_id}")
            
        # Add podcast index ID filter if provided
        if podcast_index_id is not None:
            try:
                podcast_index_int = int(podcast_index_id)
                if podcast_index_int < 0:
                    raise ValidationError("podcast_index_id must be non-negative")
                query = query.filter(Channel.podcast_index_id == podcast_index_int)
                logger.info(f"Export query filtering by podcast_index_id: {podcast_index_int}")
            except (ValueError, TypeError):
                raise ValidationError("podcast_index_id must be a valid integer")
             
        if search:
            # Enhanced search: ID (exact), URL (partial), Channel title (partial), or podcast_index_id (exact)
            search_conditions = []
            normalized_search = search.strip()
            # Try to parse as integer for ID search
            try:
                search_id = int(normalized_search)
                search_conditions.append(Feed.id == search_id)
                search_conditions.append(Channel.podcast_index_id == search_id)
            except ValueError:
                pass  # Not a valid integer, skip ID and podcast_index_id search
            
            # Exact URL match (normalized)
            if normalized_search.startswith("http"):
                normalized_url = normalize_feed_url(normalized_search)
                search_conditions.append(Feed.url == normalized_url)
            else:
                # Partial match fallback
                search_conditions.append(Feed.url.ilike(f"%{normalized_search}%"))
                search_conditions.append(Channel.title.ilike(f"%{normalized_search}%"))
            
            # Combine with OR
            query = query.filter(or_(*search_conditions))
            logger.info(f"Export query with search (ID/URL/title/podcast_index_id): {search}")
            
        # Safe dynamic sorting
        query = apply_sorting(query, Feed, sort_by, sort_order)
        logger.info(f"Export query with sort: {sort_by} {sort_order}")
        
        # Limit rows for performance
        if max_rows is None:
            max_rows = 10000
        feeds = query.limit(max_rows).all()
        logger.info(f"Retrieved {len(feeds)} feeds for export with search: {search or 'none'}")
        
        serialized_feeds = feeds_export_schema.dump(feeds)
        
        return serialized_feeds
        
    except Exception as e:
        logger.error(f"Error in get_feeds_for_export: {str(e)}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        log_error("get_feeds_for_export", e)
        raise DatabaseError(f"Failed to retrieve feeds for export: {str(e)}")


def bulk_update_feeds(feed_ids: list, updates: dict):
    """
    Update multiple feeds with the provided changes.
    
    This function performs bulk updates with validation:
    - Validates that only allowed fields are being updated
    - Validates foreign key references (e.g., feed_flag_status_id)
    - Updates the updated_at timestamp for each modified feed
    - Provides detailed results with counts of successful and failed updates
    
    Args:
        feed_ids (list): List of feed IDs to update
        updates (dict): Dictionary of fields to update with their new values
        
    Returns:
        dict: Update results with counts:
            - "updated": Number of successfully updated feeds
            - "not_found": Number of feeds not found
            - "total_requested": Total number of feeds requested for update
            
    Raises:
        ValidationError: If update fields are invalid or foreign keys don't exist
        DatabaseError: If database operations fail
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
        log_error("bulk_update_feeds", e)
        raise DatabaseError(f"Failed to bulk update feeds: {str(e)}")


# sequential since parsing is async on podverse side
def bulk_reparse_feeds(feed_ids: list) -> dict:
    """
    Reparse multiple feeds in bulk.
    
    This function processes feeds sequentially since parsing is async on the Podverse side.
    It provides detailed results for each feed including success, failure, and skip reasons.
    
    Args:
        feed_ids (list): List of feed IDs to reparse
        
    Returns:
        dict: Reparse results with counts and individual results:
            - "success": Number of successfully queued reparses
            - "failed": Number of failed reparses
            - "not_found": Number of feeds not found
            - "already_parsing": Number of feeds already being parsed
            - "results": List of individual results for each feed
            - "total_requested": Total number of feeds requested for reparse
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
            
            feed = get_feed_by_id(feed_id)
            
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
