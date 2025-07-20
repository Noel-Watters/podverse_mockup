# app/blueprints/channel/routes.py

from . import channel_bp
from app.blueprints.channel.controller import list_channels, get_channel_by_id, export_channels, get_channels_by_feed
from app.utils.auth import requires_auth
from app.utils.request_logger import get_logger, log_request_start, log_request_end
from app.extensions import limiter
from app.utils.error_handlers import handle_errors
from flask import jsonify
from app.utils.audit_decorators import audit_admin_access

logger = get_logger(__name__)

@channel_bp.before_request
def before_request():
    """Log the start of every request to channel endpoints"""
    log_request_start(logger)

@channel_bp.after_request
def after_request(response):
    """Log the end of every request to channel endpoints"""
    return log_request_end(logger, response)

@channel_bp.route('', methods=['GET'])
@limiter.limit("30 per minute")
@handle_errors
#@requires_auth
@audit_admin_access(action="GET_CHANNELS", resource="channel")
def get_all_channels():
    """Get all channels with pagination and filtering"""
    return list_channels()


@channel_bp.route('/export', methods=['GET'])
@limiter.limit("10 per minute")  # Lower rate limit for exports
@handle_errors
#@requires_auth
@audit_admin_access(action="EXPORT_CHANNELS", resource="channel")
def export_channels_route():
    """Export channels as CSV/JSON/OPML"""
    return export_channels()


@channel_bp.route('/<int:channel_id>', methods=['GET'])
@limiter.limit("30 per minute")
@handle_errors
#@requires_auth
@audit_admin_access(action="GET_CHANNEL", resource="channel")
def get_single_channel(channel_id):
    """Get a single channel by ID"""
    return get_channel_by_id(channel_id)


@channel_bp.route('/by-feed', methods=['GET'])
@limiter.limit("30 per minute")
@handle_errors
#@requires_auth
@audit_admin_access(action="GET_CHANNELS_BY_FEED", resource="channel")
def get_channels_by_feed_route():
    """Get channels by feed IDs"""
    result = get_channels_by_feed()
    return jsonify(result), 200