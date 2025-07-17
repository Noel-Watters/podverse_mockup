# app/blueprints/channel/controller.py

import os
from flask import jsonify, request
from app.blueprints.channel.services import get_channels_list, get_channel_detail, get_channels_for_export, get_channels_by_feed_ids
from app.blueprints.channel.schemas import channels_schema, channel_exports_schema, channel_detail_schema
from app.utils.query_params import get_pagination_params, get_sorting_params, get_search_query, get_multi_filter_param
from app.utils.error_exceptions import ValidationError, NotFoundError, DatabaseError
from app.utils.request_logger import get_logger, log_database_operation
from app.utils.export_response import generate_export_response
from datetime import datetime
from app.utils.export_logging import create_export_log_simple, finalize_export_log
from app.services.data_export import ensure_export_directory

logger = get_logger(__name__)

def list_channels():
    try:
        page, limit = get_pagination_params(request)
        sort_by, sort_order = get_sorting_params(request, ['id', 'title'], default_field='id')
        search = get_search_query(request)
        channel_id = request.args.get("id", type=int)  
        podcast_index_id = request.args.get("podcast_index_id", type=int)

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
        return jsonify(result)
        
    except ValidationError as e:
        logger.warning(f"Validation error in list_channels: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in list_channels: {str(e)}")
        raise DatabaseError("Failed to retrieve channels")

def export_channels():
    """
    Export channels as CSV with optional filtering and sorting.
    Reuses the same filtering logic as list_channels but without pagination.
    """
    try:
        export_by = request.args.get("export_by", "system@podverse.com")

        # Create export log
        log = create_export_log_simple(
            export_type="channels",
            filters=request.args.to_dict(),
            export_by=export_by
        )

        # Get query parameters (reuse same logic as list view)
        sort_by, sort_order = get_sorting_params(request, ['id', 'title'], default_field='id')
        search = get_search_query(request)
        channel_id = request.args.get("id", type=int)
        podcast_index_id = request.args.get("podcast_index_id", type=int)
        
        # Get max_rows parameter (optional, defaults to 10000)
        max_rows = request.args.get('max_rows', 10000, type=int)
        if max_rows <= 0 or max_rows > 50000:  
            max_rows = 10000

        logger.info(f"Exporting channels - sort: {sort_by} {sort_order}, search: {search or 'none'}, max_rows: {max_rows}, id: {channel_id}, podcast_index_id: {podcast_index_id}")
        log_database_operation(logger, "READ", "channels", f"export_max_{max_rows}")

        # Get and serialize channels
        channels = get_channels_for_export(search, sort_by, sort_order, max_rows, channel_id, podcast_index_id)
        export_data = channel_exports_schema.dump(channels)

        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"channels_export_{timestamp}.csv"
        
        # get headers from schema
        headers = {field: field for field in channel_exports_schema.fields}
        
        # Create export response
        response = generate_export_response(export_data, filename, headers)
        
        # finalize export log with absolute file path
        export_dir = ensure_export_directory()
        absolute_file_path = os.path.abspath(os.path.join(export_dir, filename))
        finalize_export_log(log.id, status="success", file_path=absolute_file_path, format=request.args.get("format", "csv")) # file name is set in generate_export_response
        logger.info(f"Generated export file: {filename} with {len(export_data)} records")
        return response

    except ValidationError as e:
        logger.warning(f"Validation error in export_channels: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in export_channels: {str(e)}")
        raise DatabaseError("Failed to export channels")

def get_channel_by_id(channel_id):
    try:   
        logger.info(f"Retrieving channel details for ID: {channel_id}")
        log_database_operation(logger, "READ", "channels", channel_id)
        
        channel = get_channel_detail(channel_id)
        
        result = channel_detail_schema.dump(channel)
        logger.info(f"Successfully retrieved channel: {channel_id} - {channel.title}")
        
        return jsonify(result)
        
    except NotFoundError:
        raise
    except ValidationError as e:
        logger.warning(f"Validation error in get_channel_by_id for ID {channel_id}: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_channel_by_id for ID {channel_id}: {str(e)}")
        raise DatabaseError("Failed to retrieve channel")


def get_channels_by_feed():
    """
    Get channels by feed IDs.
    Accepts a comma-separated list of feed IDs and returns all channels associated with those feeds.
    """
    try:
        # Get feed IDs from query parameter
        feed_ids = get_multi_filter_param(request, 'feed_ids', type_func=int)
        max_ids = request.args.get('max_ids', 100, type=int)
        
        logger.info(f"Retrieving channels by feed IDs: {feed_ids}, max_ids: {max_ids}")
        log_database_operation(logger, "READ", "channels", f"by_feed_ids_{len(feed_ids)}")
        
        # Get channels by feed IDs
        channels = get_channels_by_feed_ids(feed_ids, max_ids)
        
        result = {
            "data": channels_schema.dump(channels),
            "meta": {
                "total": len(channels),
                "requested_feed_ids": feed_ids,
                "found_feed_ids": list({channel.feed_id for channel in channels}),
                "missing_feed_ids": list(set(feed_ids) - {channel.feed_id for channel in channels})
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