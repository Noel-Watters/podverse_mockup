# backend/app/blueprints/export_logs/routes.py

from flask import jsonify, request, send_file, redirect
from . import export_logs_bp
from app.extensions import limiter
from app.blueprints.export_logs.controller import *
from app.utils.error_handlers import handle_errors
from app.utils.audit_decorators import audit_admin_access
from app.utils.request_logger import get_logger, log_request_start, log_request_end

logger = get_logger(__name__)

@export_logs_bp.before_request
def before_request():
    log_request_start(logger)

@export_logs_bp.after_request
def after_request(response):
    return log_request_end(logger, response)

@export_logs_bp.route('/', methods=['GET'])
@handle_errors
# @requires_auth
@audit_admin_access(action="GET_EXPORT_LOGS", resource="export_logs")
@limiter.limit("100 per day")
def get_export_logs():
    """Get paginated list of export logs. Supports filtering, pagination, status checks"""
    
    page, limit = get_pagination_params(request)
    sort_by, sort_order = get_sorting_params(request, ['created_at', 'completed_at', 'status', 'source', 'format', 'duration'],'created_at','desc')

    filters = {
        "status": request.args.get("status"),
        "source": request.args.get("source"),
        "export_by": request.args.get("export_by"),
        "id": request.args.get("id", type=int),
        "format": request.args.get("format"),
        "has_error": request.args.get("has_error"),
        "min_duration": request.args.get("min_duration", type=float),
        "max_duration": request.args.get("max_duration", type=float),
        "start_date": request.args.get("start_date"),
        "end_date": request.args.get("end_date"),
        "search_term": request.args.get("search_term"),
    }

    logs, pagination_metadata = get_export_logs_controller(
        page, limit, sort_by, sort_order, filters
    )
    return jsonify({'logs': logs, **pagination_metadata})


@export_logs_bp.route('/<int:log_id>', methods=['GET'])
@handle_errors
# @requires_auth
@audit_admin_access(action="GET_EXPORT_LOG", resource="export_logs")
@limiter.limit("100 per day")
def get_export_log(log_id):
    """Get detailed information about a specific export log"""
    log = get_export_log_controller(log_id)
    return jsonify(log)

@export_logs_bp.route('/<int:log_id>/download', methods=['GET'])
@handle_errors
# @requires_auth
@audit_admin_access(action="DOWNLOAD_EXPORT_FILE", resource="export_logs")
@limiter.limit("50 per day")
def download_export_file(log_id):
    """Download the exported file for a specific log.
    This endpoint handles both local files and S3 URLs.
    For S3 URLs, it redirects to the S3 URL.
    For local files, it serves the file directly.
    """
    result = download_export_file_controller(log_id)
    
    # Check if result is a redirect response (for S3 URLs)
    if result["type"] == "redirect":
        return redirect(result["url"])
    
    # Otherwise, it's a local file (file_path, filename, file_format)

    return send_file(
        result["path"],
        as_attachment=True,
        download_name=result["filename"],
        mimetype='text/csv' if result["format"] == 'csv' else 'application/json'
    )