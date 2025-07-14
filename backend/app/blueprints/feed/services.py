# app/blueprints/feed/services.py

# NOTE: The real parser (parseRSSFeedAndSaveToDatabase) should be called from the Node service here.
# Current implementation fakes this via Express stub. See: podverse-parse-service/index.js


from app.models.feed import Feed, FeedFlagStatus, FeedLog
from app.models.channel import Channel
from app.extensions import db
from app.utils.request_logger import get_logger, log_database_operation
from app.utils.security_logger import log_network_event, log_error
from app.utils.query_helpers import paginate_query, apply_sorting
from app.utils.error_exceptions import NotFoundError, ValidationError, DatabaseError, ParseError
from datetime import datetime
import xml.etree.ElementTree as ET
from flask import current_app
from werkzeug.datastructures import FileStorage
from sqlalchemy import or_
import requests
from app.blueprints.feed.schemas import feeds_export_schema
import traceback

logger = get_logger(__name__)
import time

def get_flag_status_id(status: str) -> int:
        """
        Get the ID of a feed flag status by its status string.
        """
        from app.models.feed import FeedFlagStatus
        record = db.session.query(FeedFlagStatus).filter_by(status=status).first()
        if not record:
            raise RuntimeError(f"FeedFlagStatus '{status}' not found")
        return record.id

def trigger_node_parser(url: str, podcast_index_id: int):
    for attempt in range(2):  # 1 retry
        try:
            response = requests.post("http://parse-service:3001/trigger-parse", json={
                "url": url,
                "podcast_index_id": podcast_index_id
            }, timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            if attempt == 1:
                raise
            time.sleep(1)


def create_single_feed(url: str, parsing_priority: int = 0):
    logger.info(f"Creating single feed with URL: {url}")
    log_database_operation(logger, "CREATE", "feeds", f"single_feed_{url}")
    
    try:
        # Check if feed already exists
        existing_feed = db.session.query(Feed).filter_by(url=url).first()
        if existing_feed:
            logger.warning(f"Feed already exists: {url}")
            raise ValidationError(f"Feed with URL '{url}' already exists")
        
        active_flag_id = get_flag_status_id("active")
        
        
        feed = Feed(
            url=url,
            feed_flag_status_id=active_flag_id,
            parsing_priority=parsing_priority,
            is_parsing=False
        )
        
        db.session.add(feed)
        db.session.commit()
        logger.info(f"Successfully created feed: ID {feed.id}, URL: {url}")
        log_database_operation(logger, "CREATE", "feeds", f"success_{feed.id}")

        # Trigger parsing via Node
        parse_result = None
        if feed.podcast_index_id:
            try:
                parse_result = trigger_node_parser(feed.url, feed.podcast_index_id)
            except Exception as e:
                logger.warning(f"Parse trigger failed for feed {feed.id}: {e}")
                parse_result = {"status": "error", "error": str(e)}
        
        return feed, parse_result

    except ValidationError:
        raise
    except Exception as e:
        db.session.rollback()
        log_error("create_single_feed", e)
        raise DatabaseError(f"Failed to create feed: {str(e)}")


def parse_and_update_feed_object(feed: Feed) -> dict:
    logger.info(f"Calling Node trigger for feed {feed.id}")
    
    if feed.is_parsing:
        return {"status": "error", "message": "Already parsing"}, 409

    try:
        feed.is_parsing = True
        db.session.commit()
        db.session.refresh(feed)
    except Exception as e:
        logger.error(f"Failed to set is_parsing flag: {e}")
        raise DatabaseError("Failed to mark feed as parsing")

    result = None
    try:
        response = requests.post("http://parse-service:3001/trigger-parse", json={
            "url": feed.url,
            "podcast_index_id": feed.podcast_index_id
        }, timeout=5)
        response.raise_for_status()
        result = response.json()
        is_success = result.get("success", False)
        message = result.get("message", None)
        http_status = response.status_code

    except Exception as e:
        logger.error(f"Error calling Node trigger: {str(e)}")
        result = {"status": "error", "error": str(e), "feed_id": feed.id}
        is_success = False
        message = str(e)
        http_status = None

    finally:
        log = FeedLog(
            feed_id=feed.id,
            http_status=http_status,
            is_success=is_success,
            parse_error_message=message,
            finished_at=datetime.utcnow(),
            parsed_by="flask",
            raw_result=str(result)[:255],
            parsed_item_count=10 # fake count
        )
        db.session.add(log)
        feed.is_parsing = False
        db.session.commit()

    return result


def parse_and_update_feed(feed_id: int):
    """Public function for single feed reparse (does DB lookup)"""
    feed = db.session.get(Feed, feed_id)
    if not feed:
        raise NotFoundError("Feed not found")
    
    return parse_and_update_feed_object(feed)
        

def get_all_feeds(page=1, limit=10, parsing_priority=None, is_parsing=None, status=None, feed_id=None, sort_by="id", sort_order="desc", search=None):
    """
    Get all feeds with pagination and return structured response
    """
    try:
        # Create base query with left join to Channel for title search
        query = db.session.query(Feed).join(FeedFlagStatus).outerjoin(Channel).order_by(Feed.id.desc())
        log_database_operation(logger, "READ", "feeds", f"page_{page}_limit_{limit}")
             
        if status:
            query = query.filter(FeedFlagStatus.status == status)
            logger.info(f"Filtering feeds by status: {status}")

        if parsing_priority is not None:
            query = query.filter(Feed.parsing_priority == int(parsing_priority))
            logger.info(f"Filtering feeds by parsing_priority: {parsing_priority}")

        if is_parsing is not None:
            if isinstance(is_parsing, str):
                is_parsing = is_parsing.lower() == "true"
            query = query.filter(Feed.is_parsing == is_parsing)
            logger.info(f"Filtering feeds by is_parsing: {is_parsing}")
            
        if feed_id is not None:
            query = query.filter(Feed.id == feed_id)
            logger.info(f"Filtering feeds by ID: {feed_id}")
            
        if search:
            # Enhanced search: ID (exact), URL (partial), or Channel title (partial)
            search_conditions = []
            
            try:
                search_id = int(search)
                search_conditions.append(Feed.id == search_id)
            except ValueError:
                pass  # Not a valid integer, skip ID search
            
            # Always add URL and channel title searches
            search_conditions.append(Feed.url.ilike(f"%{search}%"))
            search_conditions.append(Channel.title.ilike(f"%{search}%"))
            
            # Combine with OR
            query = query.filter(or_(*search_conditions))
            logger.info(f"Filtering feeds by search term (ID/URL/title): {search}")
            
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
        log_error("get_all_feeds", e)
        raise DatabaseError(f"Failed to retrieve feeds: {str(e)}")


def get_feed_by_id(feed_id: int):
    feed = db.session.get(Feed, feed_id)
    log_database_operation(logger, "READ", "feeds", record_id=feed_id)
    if not feed:
        logger.warning(f"Feed not found: ID {feed_id}")
        raise NotFoundError("Feed not found")
    return feed

def get_feed_logs(feed_id: int):
    """
    Get all logs for a specific feed, sorted by finished_at
    
    Args:
        feed_id (int): ID of the feed to get logs for
        
    Returns:
        list: List of FeedLog objects
        
    Raises:
        NotFoundError: If feed doesn't exist
        DatabaseError: If database operation fails
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
        log_error("get_feed_logs", e)
        raise DatabaseError(f"Failed to retrieve feed logs: {str(e)}")
 


#MARK: bulk endpoints

def get_feeds_for_export(search=None, sort_by='id', sort_order='asc', max_rows=10000):
    """
    Retrieve feeds for export with optional search and sorting.
    No pagination, but limited to max_rows for performance.
    
    Args:
        search: Optional search term to filter by ID (exact), URL (partial), or channel title (partial)
        sort_by: Field to sort by (default: 'id')
        sort_order: Sort order (default: 'asc')
        max_rows: Maximum number of rows to export (default: 10000)
        
    Returns:
        List of Feed objects
    """
    try:
        # Create base query with left join to Channel for title search
        query = db.session.query(Feed).join(FeedFlagStatus).outerjoin(Channel).order_by(Feed.id.desc())
        log_database_operation(logger, "READ", "feeds", f"export_max_{max_rows}")
             
        if search:
            # Enhanced search: ID (exact), URL (partial), or Channel title (partial)
            search_conditions = []
            
            # Try to parse as integer for ID search
            try:
                search_id = int(search)
                search_conditions.append(Feed.id == search_id)
            except ValueError:
                pass  # Not a valid integer, skip ID search
            
            # Always add URL and channel title searches
            search_conditions.append(Feed.url.ilike(f"%{search}%"))
            search_conditions.append(Channel.title.ilike(f"%{search}%"))
            
            # Combine with OR
            query = query.filter(or_(*search_conditions))
            logger.info(f"Export query with search: {search}")
            
        # Safe dynamic sorting
        query = apply_sorting(query, Feed, sort_by, sort_order)
        logger.info(f"Export query with sort: {sort_by} {sort_order}")
        
        # Limit rows max_rows for performance
        feeds = query.limit(max_rows).all()
        logger.info(f"Retrieved {len(feeds)} feeds for export with search: {search or 'none'}")
        
        serialized_feeds = feeds_export_schema.dump(feeds)
        
        return serialized_feeds
        
    except Exception as e:
        log_error("get_feeds_for_export", e)
        raise DatabaseError(f"Failed to retrieve feeds for export: {str(e)}")


def bulk_update_feeds(feed_ids: list, updates: dict):
    """
    Update multiple feeds with the provided changes
    
    Args:
        feed_ids: List of feed IDs to update
        updates: Dictionary of fields to update
        
    Returns:
        dict: Update results with counts
    """
    updated_count = 0
    not_found_count = 0
    
    try:
        logger.info(f"Starting bulk update for {len(feed_ids)} feeds")
        log_database_operation(logger, "UPDATE", "feeds", f"bulk_update_{len(feed_ids)}")
        
        # Validate updates
        valid_fields = {'feed_flag_status_id', 'parsing_priority', 'is_parsing'}
        if not set(updates.keys()).issubset(valid_fields):
            invalid_fields = set(updates.keys()) - valid_fields
            raise ValidationError(f"Invalid update fields: {invalid_fields}")
        
        # Validate feed_flag_status_id if provided
        if 'feed_flag_status_id' in updates:
            flag_status = db.session.get(FeedFlagStatus, updates['feed_flag_status_id'])
            if not flag_status:
                raise ValidationError(f"Invalid feed_flag_status_id: {updates['feed_flag_status_id']}")
        
        # Update feeds
        for feed_id in feed_ids:
            feed = db.session.get(Feed, feed_id)
            if not feed:
                not_found_count += 1
                logger.warning(f"Feed not found: ID {feed_id}")
                continue
            
            # Apply updates
            for field, value in updates.items():
                if hasattr(feed, field):
                    setattr(feed, field, value)
            
            feed.updated_at = datetime.utcnow()
            updated_count += 1
        
        db.session.commit()
        
        logger.info(f"Bulk update completed: {updated_count} updated, {not_found_count} not found")
        return {
            "updated": updated_count,
            "not_found": not_found_count,
            "total_requested": len(feed_ids)
        }
        
    except ValidationError:
        raise
    except Exception as e:
        db.session.rollback()
        log_error("bulk_update_feeds", e)
        raise DatabaseError(f"Failed to bulk update feeds: {str(e)}")


def bulk_reparse_feeds(feed_ids: list) -> dict:
    """
    Reparse multiple feeds in bulk
    """
    results = {"success": 0, "failed": 0, "not_found": 0, "already_parsing": 0, "results": []}
    for feed_id in feed_ids:
        try:
            feed = get_feed_by_id(feed_id)
            
            if feed.flag_status.status.lower() not in ["active", "always-parse"]:
                results["results"].append({"feed_id": feed_id, "status": "skipped_flag"})
                continue
            if feed.is_parsing:
                results["already_parsing"] += 1
                results["results"].append({"feed_id": feed_id, "status": "already_parsing"})
                continue
            result = parse_and_update_feed(feed_id)
            if result.get("status") == "success":
                results["success"] += 1
            else:
                results["failed"] += 1
            results["results"].append({"feed_id": feed_id, "status": result.get("status")})
        except NotFoundError:
            results["not_found"] += 1
            results["results"].append({"feed_id": feed_id, "status": "not_found"})
    results["total_requested"] = len(feed_ids)
    return results
