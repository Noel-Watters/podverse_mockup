#app/blueprints/feed/routes.py

from flask import jsonify
from . import feed_bp
from app.utils.request_logger import get_logger, log_request_start, log_request_end
from app.extensions import limiter
from app.utils.auth import requires_auth
from app.utils.error_handlers import handle_errors
from app.utils.audit_decorators import audit_admin_access
from .controllers import *
from app.utils.redis_lock import is_locked

logger = get_logger(__name__)

@feed_bp.before_request
def before_request():
    log_request_start(logger)

@feed_bp.after_request
def after_request(response):
    return log_request_end(logger, response)

def is_auto_reparse_running() -> bool:
    return is_locked("auto_reparse_all")


@feed_bp.route('/<int:feed_id>/reparse', methods=['POST'])
@handle_errors
#@audit_admin_access(action="REPARSE_FEED", resource="feed")
#@requires_auth
@limiter.limit("10 per minute")
def reparse_feed(feed_id: int):
    """
    Reparse a specific feed by ID.
    
    This endpoint can be run synchronously or asynchronously based on query parameters.
    When run asynchronously, it returns immediately with a "queued" status.
    """
    result = reparse_feed_controller(feed_id)
    # Return 202 for async mode, 200 for sync mode
    status_code = 202 if result.get("status") == "queued" else 200
    return jsonify(result), status_code


@feed_bp.route('', methods=['GET'])
@limiter.limit("80 per minute")  
@handle_errors
#@audit_admin_access(action="GET_FEEDS", resource="feed")
#@requires_auth
def get_feeds():
    """
    Get all feeds with pagination, filtering, and search capabilities. See API.md for query params and status codes.
    """
    result = get_all_feeds_controller()
    return jsonify(result), 200
   
    
@feed_bp.route('/<int:feed_id>', methods=['GET'])
@limiter.limit("80 per minute")  
@handle_errors
#@audit_admin_access(action="GET_FEED", resource="feed")
#@requires_auth
def get_feed_by_id(feed_id):
    """
    Get a single feed by ID with detailed information. See API.md for status codes.
    """
    result = get_feed_by_id_controller(feed_id)
    return jsonify(result), 200
    
    
@feed_bp.route('/<int:feed_id>/export', methods=['GET'])
@limiter.limit("10 per minute")  # Protect against large download spam
#@audit_admin_access(action="EXPORT_FEED", resource="feed")
#@requires_auth
@handle_errors
def export_single_feed(feed_id):
    """
    Export a single feed as CSV/JSON.
    
    This endpoint generates export files for a single feed with all relevant
    metadata, parsing history, and error information.
    """
    result = export_single_feed_controller(feed_id)
    # Export controllers return Response objects directly, don't jsonify them
    return result


@feed_bp.route('/<int:feed_id>/logs', methods=['GET'])
@limiter.limit("80 per minute")
#@audit_admin_access(action="GET_FEED_LOGS", resource="feed")
#@requires_auth
@handle_errors
def get_feed_logs(feed_id):
    """
    Get logs for a specific feed.
    
    This endpoint retrieves all parsing logs for a feed, providing a complete
    history of parsing attempts, successes, failures, and error messages.
    """
    result = get_feed_logs_controller(feed_id)
    return jsonify(result), 200


#MARK: bulk endpoints   
@feed_bp.route('/export', methods=['GET'])
@limiter.limit("10 per minute")  
#@audit_admin_access(action="EXPORT_FEEDS", resource="feed")
#@requires_auth
@handle_errors
def bulk_export_feeds():
    """Export feeds in bulk. See API.md for query params and status codes."""
    result = bulk_export_feeds_controller()
    return result


@feed_bp.route('/bulk-update', methods=['POST'])
@limiter.limit("4 per minute")  
#@audit_admin_access(action="UPDATE_FEEDS", resource="feed")
#@requires_auth
@handle_errors
def bulk_update_feeds():
    """
    Update status/properties of multiple feeds.
    """
    result = bulk_update_feeds_controller()
    # Return 202 for async mode, 200 for sync mode
    status_code = 202 if result.get("status") == "queued" else 200
    return jsonify(result), status_code


@feed_bp.route('/bulk-reparse', methods=['POST'])
@limiter.limit("4 per minute")  
#@audit_admin_access(action="REPARSE_FEEDS", resource="feed")
#@requires_auth
@handle_errors
def bulk_reparse_feeds():
    """
    This endpoint processes bulk reparse requests and provides detailed results for each feed.
    It can run synchronously (default) or asynchronously based on query parameters.
    """
    result = bulk_reparse_feeds_controller()
    # Return 202 for async mode, 200 for sync mode
    status_code = 202 if result.get("status") == "queued" else 200
    return jsonify(result), status_code


@feed_bp.route('/auto-reparse-status', methods=['GET'])
@limiter.limit("10 per minute")  
#@audit_admin_access(action="GET_AUTO_REPARSE_STATUS", resource="feed")
#@requires_auth
@handle_errors
def auto_reparse_status():
    """
    Check if auto_reparse_all task is currently running.
    
    This endpoint provides status information about the automatic reparse
    task that runs periodically to update feeds.
    """
    is_running = is_auto_reparse_running()
    return jsonify({
        "auto_reparse_running": is_running,
        "status": "running" if is_running else "idle"
    }), 200