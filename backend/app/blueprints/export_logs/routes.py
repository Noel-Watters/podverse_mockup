# backend/app/blueprints/export_logs/routes.py

from flask import jsonify, request, send_file
from . import export_logs_bp
from app.extensions import limiter
from app.blueprints.export_logs.controller import *
from app.utils.error_handlers import handle_errors

@export_logs_bp.route('/', methods=['GET'])
@handle_errors
#@requires_auth
@limiter.limit("100 per day")
def get_export_logs():
    """Get paginated list of export logs. Supports filtering, pagination, status checks"""
    logs, pagination_metadata = get_export_logs_controller(request)
    return jsonify({
        'logs': logs,
        **pagination_metadata
    })

@export_logs_bp.route('/<int:log_id>', methods=['GET'])
@handle_errors
#@requires_auth
@limiter.limit("100 per day")
def get_export_log(log_id):
    """Get detailed information about a specific export log"""
    log = get_export_log_controller(log_id)
    return jsonify(log)

@export_logs_bp.route('/<int:log_id>/download', methods=['GET'])
@handle_errors
#@requires_auth
@limiter.limit("50 per day")
def download_export_file(log_id):
    """Download the exported file for a specific log.
    This endpoint allows users to download exported files by their log ID.
    It checks if the file exists and is accessible before sending it.
    """
    file_path, filename, file_format = download_export_file_controller(log_id)
    return send_file(
        file_path,
        as_attachment=True,
        download_name=filename,
        mimetype='text/csv' if file_format == 'csv' else 'application/json'
    )
