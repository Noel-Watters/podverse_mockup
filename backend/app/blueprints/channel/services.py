# app/blueprints/channel/services.py

from sqlalchemy.orm import joinedload
from app.extensions import db
from app.models.channel import Channel
from app.models.channel import ChannelCategory
from app.utils.request_logger import get_logger, log_database_operation
from app.utils.query_helpers import apply_sorting, paginate_query
from app.utils.error_exceptions import NotFoundError, DatabaseError

logger = get_logger(__name__)

def channel_eagerload_options():
    """
    Use eager loading to fetch related medium and feed data in a single query (prevents N+1 query problem by joining related tables immediately)
    """
    return (
        joinedload(Channel.medium),
        joinedload(Channel.feed),
        joinedload(Channel.stats),
        joinedload(Channel.categories).joinedload(ChannelCategory.category)
    )
    

def get_channels_list(search, sort_by, sort_order, page, limit, channel_id=None, podcast_index_id=None):
    """
    Retrieve a paginated list of channels with optional search and filtering.
    Eager loads related feed, medium, categories, and stats.
    
    Args:
        search: Search term to filter by title only
        sort_by: Field to sort by
        sort_order: Sort order (asc/desc)
        page: Page number for pagination
        limit: Number of items per page
        channel_id: Optional filter by specific channel ID
        podcast_index_id: Optional filter by specific podcast index ID
    """
    try:
        query = db.session.query(Channel).options(*channel_eagerload_options())
        log_database_operation(logger, "READ", "channels", f"page_{page}_limit_{limit}")
        
        # Apply dedicated filters
        if channel_id is not None:
            query = query.filter(Channel.id == channel_id)
            logger.info(f"Filtering channels by ID: {channel_id}")
        
        if podcast_index_id is not None:
            query = query.filter(Channel.podcast_index_id == podcast_index_id)
            logger.info(f"Filtering channels by podcast_index_id: {podcast_index_id}")
        
        # Apply search filter (title only)
        if search:
            query = query.filter(Channel.title.ilike(f"%{search}%"))
            logger.info(f"Applying search filter for channels title: {search}")
        
        query = apply_sorting(query, Channel, sort_by, sort_order)
        logger.info(f"Applying sort: {sort_by} {sort_order}")
        
        channels, meta = paginate_query(query, page, limit)
        
        logger.info(f"Retrieved {len(channels)} channels for page {page} with search: {search or 'none'}")
        return channels, meta
        
    except Exception as e:
        logger.error(f"Error retrieving channels list: {str(e)}")
        raise DatabaseError(f"Failed to retrieve channels: {str(e)}")


def get_channels_for_export(search=None, sort_by='id', sort_order='asc', max_rows=10000, channel_id=None, podcast_index_id=None):
    """
    Retrieve channels for export with optional search and filtering.
    No pagination, but limited to max_rows for performance.
    Eager loads related feed, medium, categories, and stats.
    
    Args:
        search: Optional search term to filter by title
        sort_by: Field to sort by (default: 'id')
        sort_order: Sort order (default: 'asc')
        max_rows: Maximum number of rows to export (default: 10000)
        channel_id: Optional filter by specific channel ID
        podcast_index_id: Optional filter by specific podcast index ID
        
    Returns:
        List of Channel objects
    """
    try:
        query = db.session.query(Channel).options(*channel_eagerload_options())
        log_database_operation(logger, "READ", "channels", f"export_max_{max_rows}")
        
        # Apply dedicated filters
        if channel_id is not None:
            query = query.filter(Channel.id == channel_id)
            logger.info(f"Filtering export by channel ID: {channel_id}")
        
        if podcast_index_id is not None:
            query = query.filter(Channel.podcast_index_id == podcast_index_id)
            logger.info(f"Filtering export by podcast_index_id: {podcast_index_id}")
        
        # Apply search filter (title only)
        if search:
            query = query.filter(Channel.title.ilike(f"%{search}%"))
            logger.info(f"Applying search filter for export: {search}")
        
        query = apply_sorting(query, Channel, sort_by, sort_order)
        logger.info(f"Export query with sort: {sort_by} {sort_order}")
        
        # Limit to max_rows for performance
        query = query.limit(max_rows)
        
        channels = query.all()
        
        logger.info(f"Retrieved {len(channels)} channels for export with search: {search or 'none'}")
        if len(channels) == max_rows:
            logger.warning(f"Export hit max_rows limit of {max_rows} - results may be truncated")
        
        return channels
        
    except Exception as e:
        logger.error(f"Error retrieving channels for export: {str(e)}")
        raise DatabaseError(f"Failed to retrieve channels for export: {str(e)}")

def get_channel_detail(channel_id):
    """
    Get detailed channel information by ID.
    Using stats_aggregated_channel lets the admin see how popular the channel is 
    without needing to sum up raw events every time.
    """
    try:
        log_database_operation(logger, "READ", "channels", channel_id)
        
        channel = db.session.query(Channel).options(*channel_eagerload_options()).filter_by(id=channel_id).first()

        if not channel:
            logger.warning(f"Channel with ID {channel_id} not found")
            raise NotFoundError(f"Channel with ID {channel_id} not found")

        logger.info(f"Retrieved channel details for ID: {channel_id} - Title: {channel.title}")
        return channel
        
    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error retrieving channel detail for ID {channel_id}: {str(e)}")
        raise DatabaseError(f"Failed to retrieve channel detail: {str(e)}")


def get_channels_by_feed_ids(feed_ids, max_ids=100):
    """
    Retrieve channels by feed IDs with eager loading of related data.
    
    Args:
        feed_ids: List of feed IDs to filter by
        max_ids: Maximum number of feed IDs allowed per request (default: 100)
        
    Returns:
        List of Channel objects matching the feed IDs
    """
    try:
        # Validate input
        if not feed_ids:
            logger.info("No feed IDs provided, returning empty list")
            return []
        
        if len(feed_ids) > max_ids:
            logger.warning(f"Too many feed IDs requested: {len(feed_ids)}, limiting to {max_ids}")
            feed_ids = feed_ids[:max_ids]
        
        log_database_operation(logger, "READ", "channels", f"by_feed_ids_{len(feed_ids)}")
        
        # Query channels with eager loading
        channels = db.session.query(Channel).options(*channel_eagerload_options()).filter(
            Channel.feed_id.in_(feed_ids)
        ).all()
        
        logger.info(f"Retrieved {len(channels)} channels for {len(feed_ids)} feed IDs")
        
        # Log which feed IDs were found/not found for debugging
        found_feed_ids = {channel.feed_id for channel in channels}
        missing_feed_ids = set(feed_ids) - found_feed_ids
        if missing_feed_ids:
            logger.info(f"Feed IDs not found: {missing_feed_ids}")
        
        return channels
        
    except Exception as e:
        logger.error(f"Error retrieving channels by feed IDs: {str(e)}")
        raise DatabaseError(f"Failed to retrieve channels by feed IDs: {str(e)}")
    