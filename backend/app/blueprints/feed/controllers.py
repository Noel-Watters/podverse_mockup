#app/blueprints/feed/controllers.py

from flask import request, _request_ctx_stack, Response
from app.blueprints.feed.services import (
    parse_and_update_feed,
    get_all_feeds,
    get_feed_by_id,
    get_feeds_for_export,
    bulk_update_feeds,
    bulk_reparse_feeds,
    get_feed_logs
)
from app.blueprints.feed.schemas import feeds_schema, feed_schema, feed_export_schema, feed_logs_schema
from app.utils.query_params import get_pagination_params, get_sorting_params, get_search_query
from app.utils.error_exceptions import ValidationError, NotFoundError, DatabaseError
from app.utils.request_logger import get_logger, log_database_operation
from app.utils.export_response import generate_export_response
from datetime import datetime
from app.utils.export_logging import create_export_log_simple, finalize_export_log   
import traceback

logger = get_logger(__name__)


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


def get_json_or_400(required_keys: list[str]) -> dict:
    """Extract and validate JSON request data with required keys."""
    if not request.is_json:
        raise ValidationError("Request must contain JSON data")
    data = request.get_json()
    if not data:
        raise ValidationError("Request body is required")
    for key in required_keys:
        if key not in data:
            raise ValidationError(f"{key} is required")
    return data


def maybe_run_async(target_func, *args, **kwargs):
    """Run function asynchronously if async mode is requested."""
    async_mode = request.args.get('async', '').lower() == 'true'
    if request.is_json:
        async_mode = async_mode or request.json.get('async', False)
    
    if async_mode:
        import threading
        from flask import current_app
        
        def runner():
            with current_app.app_context():
                try:
                    target_func(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Async task failed: {str(e)}")
        
        threading.Thread(target=runner).start()
        return {"status": "queued"}
    
    return target_func(*args, **kwargs)


def reparse_feed_controller(feed_id: int) -> dict:
    """Controller to handle feed reparsing with optional async mode. """
    return maybe_run_async(reparse_feed_controller_sync, feed_id)


def reparse_feed_controller_sync(feed_id: int) -> dict:
    """Synchronous implementation of feed reparse controller. 
    Returns:
        dict: Parsing result with status and metadata"""
    logger.info(f"Starting reparse for feed ID: {feed_id}")
    log_database_operation(logger, "UPDATE", "feeds", feed_id)
    
    # Get the current user's Auth0 ID
    auth0_id = get_current_auth0_id()
    if auth0_id != "system@podverse.com":
        logger.info(f"Reparsing feed {feed_id} by user {auth0_id}")
    else:
        logger.info(f"Reparsing feed {feed_id} by system")
    
    # First check if feed exists
    feed = get_feed_by_id(feed_id)
    if not feed:
        logger.warning(f"Feed not found: ID {feed_id}")
        raise NotFoundError("Feed not found")
        
    if feed.is_parsing:
        logger.warning(f"Feed {feed_id} is already being parsed")
        raise ValidationError("Feed is already being parsed", status_code=409)
    
    if feed.flag_status.status.lower() not in ["active", "always-parse"]:
        raise ValidationError("Feed is not eligible for parsing")

    try:
        result = parse_and_update_feed(feed_id)
        if result.get('status') == 'success':
            logger.info(
                f"Successfully completed reparse for feed ID: {feed_id}, "
                f"Channel: {result.get('channel_id')}, Items: {result.get('item_count')}"
            )
        else:
            logger.warning(
                f"Reparse failed for feed ID: {feed_id}, "
                f"Status: {result.get('status')}, Error: {result.get('error')}"
            )
        return result
            
    except Exception as e:
        logger.error(f"Error reparsing feed {feed_id}: {str(e)}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise DatabaseError("Failed to reparse feed")


def get_all_feeds_controller() -> dict:
    """Controller to handle getting all feeds with pagination, filtering, and search."""
    logger.info("Starting feed retrieval")
    log_database_operation(logger, "READ", "feeds", "all_feeds_query")
    
    page, limit = get_pagination_params(request)
    sort_by, sort_order = get_sorting_params(request, allowed_fields=['id', 'url', 'updated_at'], default_field='id')
    search = get_search_query(request)
    
    # filtering params
    parsing_priority = request.args.get("parsing_priority")
    is_parsing = request.args.get("is_parsing")
    status = request.args.get("status")
    feed_id = request.args.get("id", type=int)  
    
    logger.info(f"Fetching feeds - page: {page}, limit: {limit}, - filters: priority={parsing_priority}, parsing={is_parsing}, status={status}, id={feed_id}")
    log_database_operation(logger, "READ", "feeds", f"paginated_query_p{page}_l{limit}")
    
    # Get feeds with pagination from service
    result = get_all_feeds(
        page=page,
        limit=limit,
        parsing_priority=parsing_priority,
        is_parsing=is_parsing,
        status=status,
        feed_id=feed_id,  
        sort_by=sort_by,
        sort_order=sort_order,
        search=search
    )
    
    serialized_data = feeds_schema.dump(result["data"])
    logger.info(f"Successfully retrieved and serialized {len(serialized_data)} feeds")
    
    return {
        "data": serialized_data,
        "meta": result["meta"]
    }
  
    
def get_feed_by_id_controller(feed_id: int) -> dict:
    """Controller to handle getting a single feed by ID."""
    logger.info(f"Fetching feed by ID: {feed_id}")
    log_database_operation(logger, "READ", "feeds", record_id=feed_id)
    
    feed = get_feed_by_id(feed_id)
    if not feed:
        logger.warning(f"Feed not found: ID {feed_id}")
        raise NotFoundError("Feed not found.")
    
    serialized_feed = feed_schema.dump(feed)
    logger.info(f"Feed found and serialized: ID {feed_id}")
    return serialized_feed


def get_feed_logs_controller(feed_id: int) -> dict:
    """
    Controller to handle retrieving logs for a specific feed.
    
    This controller fetches and serializes all logs for a given feed,
    providing a complete history of parsing attempts and results.
    """
    try:
        logger.info(f"Fetching logs for feed ID: {feed_id}")
        log_database_operation(logger, "READ", "feed_logs", f"feed_{feed_id}")

        logs = get_feed_logs(feed_id)
        serialized_logs = feed_logs_schema.dump(logs)
        logger.info(f"Retrieved and serialized {len(serialized_logs)} logs for feed ID {feed_id}")

        return {"logs": serialized_logs}

    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_feed_logs: {str(e)}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise DatabaseError("Failed to retrieve feed logs")


def export_single_feed_controller(feed_id: int) -> Response:
    """
    Controller to handle export of a single feed.
    
    This controller generates export files (CSV/JSON) for a single feed,
    including all relevant metadata and parsing history.
        
    Returns:
        Response: Flask response object with export file
    """
    try:
        logger.info(f"Exporting single feed: ID {feed_id}")
        log_database_operation(logger, "READ", "feeds", f"export_single_{feed_id}")

        feed = get_feed_by_id(feed_id)
        if not feed:
            logger.warning(f"Feed not found for export: ID {feed_id}")
            raise NotFoundError("Feed not found")

        export_data = [feed_export_schema.dump(feed)]

        # Generate filename
        filename = f"feed_{feed_id}_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

        logger.info(f"Generated single feed export file: {filename}")
        return generate_export_response(export_data, filename)

    except NotFoundError:
        raise
    except ValidationError as e:
        logger.warning(f"Validation error in export_single_feed: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in export_single_feed: {str(e)}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise DatabaseError("Failed to export single feed")


def bulk_export_feeds_controller() -> Response:
    """
    Controller to handle bulk export of feeds.

    Returns:
        Response: Flask response object with export file
    """
    export_log = None
    try:
        # Get query parameters
        sort_by, sort_order = get_sorting_params(request, ['id', 'url', 'updated_at'], default_field='id')
        search = get_search_query(request)
        format = request.args.get("format", "csv")
        admin_email = request.args.get("admin_email", "system@podverse.com")
        feed_id = request.args.get("id", type=int)  # Add ID filter parameter
        
        # Validate format
        if format not in ["csv", "json"]:
            raise ValidationError("Invalid format. Use 'csv' or 'json'")
        
        # create export log
        export_log = create_export_log_simple(
            export_type="feeds",
            filters={"format": format, "admin_email": admin_email, "feed_id": feed_id},
            status="pending",
            file_path=None,
            export_by=admin_email
        )

        # Get feeds for export
        feeds = get_feeds_for_export(search=search, sort_by=sort_by, sort_order=sort_order, feed_id=feed_id)
        
        # Generate filename
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"feeds_export_{timestamp}"
        # Generate response
        response = generate_export_response(feeds, filename)
        
        # Update export log with success
        finalize_export_log(
            export_log.id,
            status="success",
            file_path=f"/exports/{filename}.{format}",
            format=format,
            feeds_count=len(feeds)
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error in bulk_export_feeds: {str(e)}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        if export_log:
            finalize_export_log(
                export_log.id,
                status="error",
                error_message=str(e)
            )
        raise DatabaseError("Failed to export feeds")


def bulk_update_feeds_controller() -> dict:
    """Controller to handle bulk update of feeds with optional async mode."""
    return maybe_run_async(bulk_update_feeds_controller_sync)


def bulk_update_feeds_controller_sync() -> dict:
    """Synchronous implementation of bulk update controller."""
    try:
        logger.info("Starting bulk feed update")
        log_database_operation(logger, "UPDATE", "feeds", "bulk_update_attempt")
        
        data = get_json_or_400(["feed_ids", "updates"])
        feed_ids = data["feed_ids"]
        updates = data["updates"]
        
        if not isinstance(feed_ids, list) or not feed_ids:
            raise ValidationError("feed_ids must be a non-empty list")
        
        if not isinstance(updates, dict) or not updates:
            raise ValidationError("updates must be a non-empty object")
        
        logger.info(f"Bulk updating {len(feed_ids)} feeds with updates: {list(updates.keys())}")
        
        result = bulk_update_feeds(feed_ids, updates)
        
        logger.info(f"Bulk update completed - Updated: {result['updated']}, Not found: {result['not_found']}")
        
        return result

    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in bulk_update_feeds: {str(e)}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise DatabaseError("Failed to bulk update feeds")


def bulk_reparse_feeds_controller() -> dict:
    """Controller to handle bulk reparse of feeds with optional async mode."""
    return maybe_run_async(bulk_reparse_feeds_controller_sync)


def bulk_reparse_feeds_controller_sync() -> dict:
    """Synchronous implementation of bulk reparse controller."""
    try:
        logger.info("Starting bulk feed reparse")
        log_database_operation(logger, "UPDATE", "feeds", "bulk_reparse_attempt")
        
        data = get_json_or_400(["feed_ids"])
        feed_ids = data["feed_ids"]
        
        if not isinstance(feed_ids, list) or not feed_ids:
            raise ValidationError("feed_ids must be a non-empty list")
        
        # Process the bulk reparse synchronously
        result = bulk_reparse_feeds(feed_ids)
        
        logger.info(f"Bulk reparse completed - Success: {result['success']}, Failed: {result['failed']}, Not found: {result['not_found']}, Already parsing: {result['already_parsing']}")
        
        return result

    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in bulk_reparse_feeds: {str(e)}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise DatabaseError("Failed to bulk reparse feeds")