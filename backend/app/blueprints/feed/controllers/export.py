# app/blueprints/feed/controllers/export.py

from flask import request, Response
from app.blueprints.feed.services import get_feeds_for_export, get_feed_by_id
from app.utils.export_utils import *
from app.utils.query_params import get_sorting_params, get_search_query
from app.utils.request_logger import get_logger, log_database_operation
from app.blueprints.feed.schemas import feed_export_schema
from app.utils.error_exceptions import ValidationError, NotFoundError, DatabaseError
from app.utils.redis_lock import redis_lock, RedisLockError
import traceback

logger = get_logger(__name__)

def export_single_feed_controller(feed_id: int) -> Response:
    """Export a single feed with Redis locking and error handling."""
    export_log = None
    try:
        logger.info(f"Exporting single feed: ID {feed_id}")
        log_database_operation(logger, "READ", "feeds", f"export_single_{feed_id}")

        # Use Redis lock to prevent concurrent exports of the same feed
        lock_name = f"export_single_feed_{feed_id}"
        with redis_lock(lock_name, timeout=300) as (acquired, error):  # 5 minutes timeout
            if not acquired:
                logger.warning(f"Export skipped for feed {feed_id}: {error or 'already being exported'}")
                raise ValidationError("Feed is already being exported. Please try again in a few minutes.")

            format, export_by = get_export_format_and_user()
            export_log = create_export_log_with_filters(
                export_type="feeds",
                filters={"feed_id": feed_id},
                export_by=export_by
            )

            feed = get_feed_by_id(feed_id)
            if not feed:
                raise NotFoundError("Feed not found")

            export_data = [feed_export_schema.dump(feed)]
            filename = generate_export_filename("feed", export_by, feed_id)
            headers = create_export_headers_from_schema(feed_export_schema.fields)
            format, export_by = get_export_format_and_user()
            
            response, file_path = generate_export_response_with_path(export_data, filename, format, headers)
            finalize_export_success(export_log.id, file_path, format)
            return response

    except (NotFoundError, ValidationError, RedisLockError):
        raise
    except Exception as e:
        logger.error(f"Export error: {str(e)}")
        if export_log:
            finalize_export_failure(export_log.id, str(e))
        raise DatabaseError("Failed to export single feed")


def bulk_export_feeds_controller() -> Response:
    """Export multiple feeds with Redis locking and error handling."""
    export_log = None
    try:
        sort_by, sort_order = get_sorting_params(request, ['id', 'url', 'updated_at'], default_field='id')
        search = get_search_query(request)
        format, export_by = get_export_format_and_user()
        feed_id = request.args.get("id", type=int)
        podcast_index_id = request.args.get("podcast_index_id", type=int)

        validate_export_format(format)

        # Use Redis lock to prevent concurrent bulk exports
        lock_name = f"bulk_export_feeds_{export_by}"
        with redis_lock(lock_name, timeout=600) as (acquired, error):  # 10 minutes timeout
            if not acquired:
                logger.warning(f"Bulk export skipped for user {export_by}: {error or 'already exporting'}")
                raise ValidationError("Bulk export is already in progress. Please try again in a few minutes.")

            export_log = create_export_log_with_filters(
                export_type="feeds",
                filters={"format": format, "export_by": export_by, "feed_id": feed_id, "podcast_index_id": podcast_index_id},
                export_by=export_by
            )

            feeds = get_feeds_for_export(
                search=search, 
                sort_by=sort_by, 
                sort_order=sort_order, 
                feed_id=feed_id, 
                podcast_index_id=podcast_index_id
            )
            
            filename = generate_export_filename("feeds", export_by)
            response, file_path = generate_export_response_with_path(feeds, filename, format)
            finalize_export_success(export_log.id, file_path, format, feeds_count=len(feeds))
            return response

    except (ValidationError, RedisLockError):
        raise
    except Exception as e:
        logger.error(f"Error in bulk_export_feeds: {str(e)}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        if export_log:
            finalize_export_failure(export_log.id, str(e))
        raise DatabaseError("Failed to export feeds")
