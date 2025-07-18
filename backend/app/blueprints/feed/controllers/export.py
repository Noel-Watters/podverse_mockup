# app/blueprints/feed/controllers/export.py

from flask import request, Response
from datetime import datetime
from app.blueprints.feed.services import get_feeds_for_export, get_feed_by_id
from app.utils.export_logging import create_export_log_simple, finalize_export_log
from app.utils.file_system_helpers import ensure_export_directory
from app.utils.export_response import generate_export_response
from app.utils.query_params import get_sorting_params, get_search_query
from app.utils.request_logger import get_logger, log_database_operation
from app.utils.auth import get_current_auth0_id
from app.blueprints.feed.schemas import feed_export_schema
from app.utils.error_exceptions import ValidationError, NotFoundError, DatabaseError
from app.utils.redis_lock import redis_lock, RedisLockError
import os
import traceback
from typing import Dict, Any, List, Optional

logger = get_logger(__name__)

# Helper functions
def _sanitize_user_id(user_id: str) -> str:
    """Sanitize user ID for use in filenames."""
    return user_id.replace('@', '_').replace('.', '_')

def _generate_filename(prefix: str, user_id: str, feed_id: Optional[int] = None) -> str:
    """Generate a unique filename with timestamp and user ID."""
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')
    sanitized_user_id = _sanitize_user_id(user_id)
    
    if feed_id:
        return f"{prefix}_{feed_id}_export_{timestamp}_{sanitized_user_id}"
    return f"{prefix}_export_{timestamp}_{sanitized_user_id}"

def _create_export_log_with_filters(export_type: str, filters: Dict[str, Any], export_by: str) -> Any:
    """Create export log with common parameters."""
    return create_export_log_simple(export_type=export_type, filters=filters, export_by=export_by)

def _finalize_export_success(export_log_id: int, file_path: str, format: str, **kwargs) -> None:
    """Finalize export log with success status."""
    finalize_export_log(export_log_id, status="success", file_path=file_path, format=format, **kwargs)

def _finalize_export_failure(export_log_id: int, error_message: str) -> None:
    """Finalize export log with failure status."""
    finalize_export_log(export_log_id, status="failed", error_message=error_message)

def _generate_export_response_with_path(export_data: List[Dict], filename: str, format: str, headers: Optional[Dict] = None) -> tuple[Response, str]:
    """Generate export response and return both response and file path."""
    response = generate_export_response(export_data, filename, headers)
    export_dir = ensure_export_directory()
    file_extension = f".{format}" if format else ""
    absolute_file_path = os.path.abspath(os.path.join(export_dir, f"{filename}{file_extension}"))
    return response, absolute_file_path

# Controllers
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

            export_log = _create_export_log_with_filters(
                export_type="feeds",
                filters={"feed_id": feed_id},
                export_by=get_current_auth0_id()
            )

            feed = get_feed_by_id(feed_id)
            if not feed:
                raise NotFoundError("Feed not found")

            export_data = [feed_export_schema.dump(feed)]
            user_id = get_current_auth0_id()
            filename = _generate_filename("feed", user_id, feed_id)
            headers = {field: field for field in feed_export_schema.fields}
            format = request.args.get("format", "csv")
            
            response, file_path = _generate_export_response_with_path(export_data, filename, format, headers)
            _finalize_export_success(export_log.id, file_path, format)
            return response

    except (NotFoundError, ValidationError, RedisLockError):
        raise
    except Exception as e:
        logger.error(f"Export error: {str(e)}")
        if export_log:
            _finalize_export_failure(export_log.id, str(e))
        raise DatabaseError("Failed to export single feed")


def bulk_export_feeds_controller() -> Response:
    """Export multiple feeds with Redis locking and error handling."""
    export_log = None
    try:
        sort_by, sort_order = get_sorting_params(request, ['id', 'url', 'updated_at'], default_field='id')
        search = get_search_query(request)
        format = request.args.get("format", "csv")
        export_by = request.args.get("export_by") or get_current_auth0_id()
        feed_id = request.args.get("id", type=int)
        podcast_index_id = request.args.get("podcast_index_id", type=int)

        if format not in ["csv", "json"]:
            raise ValidationError("Invalid format. Use 'csv' or 'json'")

        # Use Redis lock to prevent concurrent bulk exports
        lock_name = f"bulk_export_feeds_{export_by}"
        with redis_lock(lock_name, timeout=600) as (acquired, error):  # 10 minutes timeout
            if not acquired:
                logger.warning(f"Bulk export skipped for user {export_by}: {error or 'already exporting'}")
                raise ValidationError("Bulk export is already in progress. Please try again in a few minutes.")

            export_log = _create_export_log_with_filters(
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
            
            filename = _generate_filename("feeds", export_by)
            response, file_path = _generate_export_response_with_path(feeds, filename, format)
            _finalize_export_success(export_log.id, file_path, format, feeds_count=len(feeds))
            return response

    except (ValidationError, RedisLockError):
        raise
    except Exception as e:
        logger.error(f"Error in bulk_export_feeds: {str(e)}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        if export_log:
            _finalize_export_failure(export_log.id, str(e))
        raise DatabaseError("Failed to export feeds")
