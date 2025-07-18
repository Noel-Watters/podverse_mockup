# app/blueprints/feed/services/query_service.py

from app.models.feed import Feed, FeedFlagStatus, FeedLog
from app.models.channel import Channel
from app.extensions import db
from app.utils.request_logger import get_logger, log_database_operation
from app.utils.security_logger import log_error
from app.utils.query_helpers import paginate_query, apply_sorting
from app.utils.error_exceptions import NotFoundError, ValidationError, DatabaseError
from sqlalchemy import or_
import traceback
from .node_trigger import normalize_feed_url

logger = get_logger(__name__)

def get_all_feeds(page=1, limit=10, parsing_priority=None, is_parsing=None, status=None, feed_id=None, podcast_index_id=None, sort_by="id", sort_order="desc", search=None):
    """
    Get all feeds with pagination and return structured response. 
    """
    try:
        # Create base query with left join to Channel for title search
        query = db.session.query(Feed).join(FeedFlagStatus).outerjoin(Channel)
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
        log_error("get_all_feeds", "unknown", e)
        raise DatabaseError(f"Failed to retrieve feeds: {str(e)}")


def get_feed_by_id(feed_id: int):
    """Get a single feed by its ID or raise an error if it doesn't exist."""
    feed = db.session.get(Feed, feed_id)
    log_database_operation(logger, "READ", "feeds", record_id=feed_id)
    if not feed:
        logger.warning(f"Feed not found: ID {feed_id}")
        raise NotFoundError("Feed not found")
    return feed


def get_feed_logs(feed_id: int):
    """Get all logs for a specific feed, sorted by finished_at."""
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
        log_error("get_feed_logs", "unknown", e)
        raise DatabaseError(f"Failed to retrieve feed logs: {str(e)}") 