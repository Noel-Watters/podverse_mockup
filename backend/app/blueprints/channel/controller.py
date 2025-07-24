# app/blueprints/channel/controller.py

from app.blueprints.channel.services import get_channels_list, get_channel_detail, get_channels_for_export, get_channels_by_feed_ids
from app.blueprints.channel.schemas import channels_schema, channel_exports_schema, channel_detail_schema

from app.utils.error_exceptions import ValidationError, NotFoundError, DatabaseError
from app.utils.request_logger import get_logger, log_database_operation
from app.utils.export_utils import *
import traceback

logger = get_logger(__name__)

def list_channels():
    """List channels with pagination, filtering, and search capabilities."""
    try:
        logger.info(f"Listing channels - page: {page}, limit: {limit}, sort: {sort_by} {sort_order}, search: {search or 'none'}, id: {channel_id}, podcast_index_id: {podcast_index_id}")
        log_database_operation(logger, "READ", "channels", f"list_p{page}_l{limit}")

        channels, meta = get_channels_list(search, sort_by, sort_order, page, limit, channel_id, podcast_index_id)

        result = {
            "data": channels_schema.dump(channels),
            "meta": {
                "total": meta['total_items'],
                "limit": limit,
                "offset": (page - 1) * limit
            }
        }
        
        logger.info(f"Successfully listed {len(channels)} channels")
        return result
        
    except ValidationError as e:
        logger.warning(f"Validation error in list_channels: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in list_channels: {str(e)}")
        raise DatabaseError("Failed to retrieve channels")

def export_channels_controller(search, sort_by, sort_order, max_rows, export_by, filters):
    """
    Export channels as CSV with optional filtering and sorting.
    Reuses the same filtering logic as list_channels but without pagination.
    """
    try:
        # Create export log
        log = create_export_log_with_filters(
            source="channels",
            filters=filters,
            export_by=export_by
        )

        logger.info(f"Exporting channels - sort: {sort_by} {sort_order}, search: {search or 'none'}, max_rows: {max_rows}, id: {filters.get("id")}, podcast_index_id: {filters.get("podcast_index_id")}")
        log_database_operation(logger, "READ", "channels", f"export_max_{max_rows}")

        # Get and serialize channels
        channels = get_channels_for_export(search, sort_by, sort_order, max_rows, filters.get("id"), filters.get("podcast_index_id"))
        export_data = channel_exports_schema.dump(channels)

        # Generate filename and headers
        filename = generate_export_filename("channels", export_by)
        headers = create_export_headers_from_schema(channel_exports_schema.fields)
        
        # Create export response
        response, file_path = generate_export_response_with_path(export_data, filename, filters.get("format"), headers)
        finalize_export_success(log.id, file_path, filters.get("format"), channels_count=len(export_data))
        logger.info(f"Generated export file: {filename} with {len(export_data)} records")
        return response

    except ValidationError as e:
        logger.warning(f"Validation error in export_channels: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in export_channels: {str(e)}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        if log:
            finalize_export_failure(log.id, str(e))
        raise DatabaseError("Failed to export channels")

def get_channel_by_id(channel_id):
    try:   
        logger.info(f"Retrieving channel details for ID: {channel_id}")
        log_database_operation(logger, "READ", "channels", channel_id)
        
        channel = get_channel_detail(channel_id)
        
        result = channel_detail_schema.dump(channel)
        logger.info(f"Successfully retrieved channel: {channel_id} - {channel.title}")
        
        return result
        
    except NotFoundError:
        raise
    except ValidationError as e:
        logger.warning(f"Validation error in get_channel_by_id for ID {channel_id}: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_channel_by_id for ID {channel_id}: {str(e)}")
        raise DatabaseError("Failed to retrieve channel")


def get_channels_by_feed():
    """Get channels by feed IDs. Accepts a comma-separated list of feed IDs and returns all channels associated with those feeds."""
    try:
        logger.info(f"Retrieving channels by feed IDs: {feed_ids}, max_ids: {max_ids}")
        log_database_operation(logger, "READ", "channels", f"by_feed_ids_{len(feed_ids)}")
        
        channels = get_channels_by_feed_ids(feed_ids, max_ids)
        data = channels_schema.dump(channels)
        found = {channel.feed_id for channel in channels}
        
        result = {
            "data": data,
            "meta": {
                "total": len(channels),
                "requested_feed_ids": feed_ids,
                "found_feed_ids": list(found),
                "missing_feed_ids": list(set(feed_ids) - found)
            }
        }
        
        logger.info(f"Successfully retrieved {len(channels)} channels for {len(feed_ids)} feed IDs")
        return jsonify(result)
        
    except ValidationError as e:
        logger.warning(f"Validation error in get_channels_by_feed: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_channels_by_feed: {str(e)}")
        raise DatabaseError("Failed to retrieve channels by feed IDs")