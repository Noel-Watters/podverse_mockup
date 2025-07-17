#app/blueprints/feed/routes.py

from flask import jsonify, request
from . import feed_bp
from app.utils.request_logger import get_logger, log_request_start, log_request_end
from app.utils.error_exceptions import ValidationError, NotFoundError, DatabaseError
from app.extensions import limiter
from app.utils.auth import requires_auth
from .controllers import (
    reparse_feed_controller, 
    get_all_feeds_controller, 
    get_feed_by_id_controller, 
    bulk_export_feeds_controller, 
    export_single_feed_controller, 
    bulk_update_feeds_controller, 
    bulk_reparse_feeds_controller,
    get_feed_logs_controller
)
from app.utils.redis_lock import is_locked
import traceback


logger = get_logger(__name__)

@feed_bp.before_request
def before_request():
    """Log the start of every request to feed endpoints"""
    log_request_start(logger)

@feed_bp.after_request
def after_request(response):
    """Log the end of every request to feed endpoints"""
    return log_request_end(logger, response)

def is_auto_reparse_running() -> bool:
    """
    Check if the auto_reparse_all task is currently running.
    
    Returns:
        bool: True if auto_reparse_all is currently running, False otherwise
    """
    return is_locked("auto_reparse_all")


@feed_bp.route('/<int:feed_id>/reparse', methods=['POST'])
def reparse_feed(feed_id: int):
    """
    Reparse a specific feed by ID.
    
    This endpoint can be run synchronously or asynchronously based on query parameters.
    When run asynchronously, it returns immediately with a "queued" status.
    
    Query Parameters:
        async (bool): If true, run the reparse asynchronously (default: false)
        
    Request Body (optional):
        async (bool): Alternative way to specify async mode
        
    Returns:
        JSON response with parsing status and metadata:
        
        Synchronous mode (default):
            - status: "success" or "error"
            - message: Description of the result
            - feed_id: ID of the processed feed
            - Additional fields from parser service response
            
        Asynchronous mode:
            - status: "queued"
        
    Status Codes:
        200: Reparse completed successfully (synchronous mode)
        202: Reparse queued for async execution (asynchronous mode)
        409: Feed is already being parsed
        404: Feed not found
        400: Feed not eligible for parsing
    """
    try:
        result = reparse_feed_controller(feed_id)
        # Return 202 for async mode, 200 for sync mode
        status_code = 202 if result.get("status") == "queued" else 200
        return jsonify(result), status_code
    except ValidationError as e:
        logger.warning(f"Validation error in reparse_feed: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in reparse_feed: {str(e)}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise DatabaseError("Failed to reparse feed")


@feed_bp.route('', methods=['GET'])
@limiter.limit("80 per minute")  
#@requires_auth
def get_feeds():
    """
    Get all feeds with pagination, filtering, and search capabilities.
    
    Query Parameters:
        page (int): Page number for pagination (default: 1)
        limit (int): Number of items per page (default: 10)
        sort_by (str): Field to sort by (id, url, updated_at) (default: id)
        sort_order (str): Sort order (asc, desc) (default: desc)
        search (str): Search term for ID, URL, title, or podcast_index_id
        parsing_priority (int): Filter by parsing priority
        is_parsing (bool): Filter by parsing status
        status (str): Filter by feed flag status
        id (int): Filter by specific feed ID
        podcast_index_id (int): Filter by podcast index ID
        
    Returns:
        JSON response with feeds data and pagination metadata
        
    Status Codes:
        200: Success
        400: Invalid query parameters
    """
    try:
        result = get_all_feeds_controller()
        return jsonify(result), 200
    except ValidationError as e:
        logger.warning(f"Validation error in get_feeds: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_feeds: {str(e)}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise DatabaseError("Failed to retrieve feeds")
   
    
@feed_bp.route('/<int:feed_id>', methods=['GET'])
@limiter.limit("80 per minute")  
#@requires_auth
def get_feed_by_id(feed_id):
    """
    Get a single feed by ID with detailed information.
    
    Args:
        feed_id (int): The ID of the feed to retrieve
        
    Returns:
        JSON response with detailed feed information including recent logs
        
    Status Codes:
        200: Success
        404: Feed not found
    """
    try:
        result = get_feed_by_id_controller(feed_id)
        return jsonify(result), 200
    except NotFoundError:
        raise
    except ValidationError as e:
        logger.warning(f"Validation error in get_feed_by_id: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_feed_by_id: {str(e)}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise DatabaseError("Failed to retrieve feed")
    
    
@feed_bp.route('/<int:feed_id>/export', methods=['GET'])
@limiter.limit("5 per minute")  # Protect against large download spam
#@requires_auth
def export_single_feed(feed_id):
    """
    Export a single feed as CSV/JSON.
    
    This endpoint generates export files for a single feed with all relevant
    metadata, parsing history, and error information.
    
    Args:
        feed_id (int): The ID of the feed to export
        
    Returns:
        File response with export data
        
    Status Codes:
        200: Export successful
        404: Feed not found
        400: Export failed
    """
    try:
        return export_single_feed_controller(feed_id)
    except NotFoundError:
        raise
    except ValidationError as e:
        logger.warning(f"Validation error in export_single_feed: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in export_single_feed: {str(e)}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise DatabaseError("Failed to export feed")


@feed_bp.route('/<int:feed_id>/logs', methods=['GET'])
@limiter.limit("80 per minute")
#@requires_auth
def get_feed_logs(feed_id):
    """
    Get logs for a specific feed.
    
    This endpoint retrieves all parsing logs for a feed, providing a complete
    history of parsing attempts, successes, failures, and error messages.
    
    Args:
        feed_id (int): The ID of the feed to get logs for
        
    Returns:
        JSON response with logs data
        
    Status Codes:
        200: Success
        404: Feed not found
    """
    try:
        result = get_feed_logs_controller(feed_id)
        return jsonify(result), 200
    except NotFoundError:
        raise
    except ValidationError as e:
        logger.warning(f"Validation error in get_feed_logs: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_feed_logs: {str(e)}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise DatabaseError("Failed to retrieve feed logs")

#MARK: bulk endpoints   
@feed_bp.route('/export', methods=['GET'])
@limiter.limit("5 per minute")  
#@requires_auth
def bulk_export_feeds():
    """
    Export feeds in bulk as CSV/JSON.
    
    This endpoint handles bulk export operations with performance optimizations
    and comprehensive logging. It supports filtering and search capabilities.
    
    Query Parameters:
        format (str): Export format (csv, json) (default: csv)
        export_by (str): Email for export tracking (default: system@podverse.com)
        sort_by (str): Field to sort by (id, url, updated_at) (default: id)
        sort_order (str): Sort order (asc, desc) (default: asc)
        search (str): Search term for filtering feeds
        id (int): Filter by specific feed ID
        podcast_index_id (int): Filter by podcast index ID
        
    Returns:
        File response with export data
        
    Status Codes:
        200: Export successful
        400: Invalid parameters or export failed
    """
    try:
        return bulk_export_feeds_controller()
    except ValidationError as e:
        logger.warning(f"Validation error in bulk_export_feeds: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in bulk_export_feeds: {str(e)}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise DatabaseError("Failed to export feeds")


@feed_bp.route('/bulk-update', methods=['POST'])
@limiter.limit("4 per minute")  
#@requires_auth
def bulk_update_feeds():
    """
    Update status/properties of multiple feeds.
    
    This endpoint allows bulk updates of feed properties with validation
    and detailed result reporting. It can run synchronously (default) or asynchronously.
    
    Query Parameters:
        async (bool): If true, run the update asynchronously (default: false)
        
    Request Body (JSON):
        feed_ids (list): List of feed IDs to update
        updates (dict): Dictionary of fields to update with new values
            - feed_flag_status_id (int): New flag status ID
            - parsing_priority (int): New parsing priority
            - container_id (str): New container ID
        async (bool): Alternative way to specify async mode
            
    Returns:
        JSON response with update results:
        
        Synchronous mode (default):
            - updated: Number of successfully updated feeds
            - not_found: Number of feeds not found
            - results: List of individual results for each feed
            - total_requested: Total number of feeds requested
            
        Asynchronous mode:
            - status: "queued"
        
    Status Codes:
        200: Update completed (synchronous) or queued (asynchronous)
        202: Update queued for async execution
        400: Invalid request data
    """
    try:
        result = bulk_update_feeds_controller()
        # Return 202 for async mode, 200 for sync mode
        status_code = 202 if result.get("status") == "queued" else 200
        return jsonify(result), status_code
    except ValidationError as e:
        logger.warning(f"Validation error in bulk_update_feeds: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in bulk_update_feeds: {str(e)}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise DatabaseError("Failed to bulk update feeds")


@feed_bp.route('/bulk-reparse', methods=['POST'])
@limiter.limit("4 per minute")  
#@requires_auth
def bulk_reparse_feeds():
    """
    Trigger reparse for multiple feeds.
    
    This endpoint processes bulk reparse requests and provides detailed results for each feed.
    It can run synchronously (default) or asynchronously based on query parameters.
    
    Query Parameters:
        async (bool): If true, run the reparse asynchronously (default: false)
        
    Request Body (JSON):
        feed_ids (list): List of feed IDs to reparse
        async (bool): Alternative way to specify async mode
        
    Returns:
        JSON response with reparse results:
        
        Synchronous mode (default):
            - success: Number of successfully queued reparses
            - failed: Number of failed reparses
            - not_found: Number of feeds not found
            - already_parsing: Number of feeds already being parsed
            - results: List of individual results for each feed
            - total_requested: Total number of feeds requested
            
        Asynchronous mode:
            - status: "queued"
            
    Status Codes:
        200: Reparse processing completed (synchronous) or queued (asynchronous)
        202: Reparse queued for async execution
        400: Invalid request data
    """
    try:
        result = bulk_reparse_feeds_controller()
        # Return 202 for async mode, 200 for sync mode
        status_code = 202 if result.get("status") == "queued" else 200
        return jsonify(result), status_code
    except ValidationError as e:
        logger.warning(f"Validation error in bulk_reparse_feeds: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in bulk_reparse_feeds: {str(e)}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise DatabaseError("Failed to bulk reparse feeds")


@feed_bp.route('/auto-reparse-status', methods=['GET'])
@limiter.limit("10 per minute")  
#@requires_auth
def auto_reparse_status():
    """
    Check if auto_reparse_all task is currently running.
    
    This endpoint provides status information about the automatic reparse
    task that runs periodically to update feeds.
    
    Returns:
        JSON response with auto reparse status:
            - auto_reparse_running (bool): Whether the task is currently running
            - status (str): "running" or "idle"
            
    Status Codes:
        200: Success
    """
    try:
        is_running = is_auto_reparse_running()
        
        return jsonify({
            "auto_reparse_running": is_running,
            "status": "running" if is_running else "idle"
        }), 200
    except Exception as e:
        logger.error(f"Error checking auto_reparse_status: {str(e)}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise DatabaseError("Failed to check auto reparse status")