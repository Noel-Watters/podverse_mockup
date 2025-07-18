# app/blueprints/feed/services/export_service.py

from app.models.feed import Feed, FeedFlagStatus
from app.models.channel import Channel
from app.extensions import db
from app.utils.request_logger import get_logger, log_database_operation
from app.utils.security_logger import log_error
from app.utils.query_helpers import apply_sorting
from app.utils.error_exceptions import ValidationError, DatabaseError
from app.blueprints.feed.schemas import feeds_export_schema
from sqlalchemy import or_
import traceback
from .node_trigger import normalize_feed_url

logger = get_logger(__name__)

def get_feeds_for_export(search=None, sort_by='id', sort_order='asc', max_rows=None, feed_id=None, podcast_index_id=None):
    """Retrieve feeds for export with optional search and sorting."""
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
        log_error("get_feeds_for_export", "unknown", e)
        raise DatabaseError(f"Failed to retrieve feeds for export: {str(e)}") 