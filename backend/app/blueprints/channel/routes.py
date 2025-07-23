# app/blueprints/channel/routes.py

from flask import request, jsonify
from . import channel_bp
from app.blueprints.channel.controller import *
from app.utils.request_logger import get_logger, log_request_start, log_request_end
from app.utils.query_params import get_pagination_params, get_sorting_params, get_search_query, get_multi_filter_param
from app.extensions import limiter
from app.utils.error_handlers import handle_errors
from app.utils.audit_decorators import audit_admin_access
from app.utils.export_utils import *

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
     # Get query parameters
    page, limit = get_pagination_params(request)
    sort_by, sort_order = get_sorting_params(request, ['id', 'title'], default_field='id')
    search = get_search_query(request)
    channel_id = request.args.get("id", type=int)  
    podcast_index_id = request.args.get("podcast_index_id", type=int)
    
    result = list_channels_controller(search, sort_by, sort_order, page, limit, channel_id, podcast_index_id)
    return jsonify(result)


@channel_bp.route('/export', methods=['GET'])
@limiter.limit("10 per minute")  # Lower rate limit for exports
@handle_errors
#@requires_auth
@audit_admin_access(action="EXPORT_CHANNELS", resource="channel")
def export_channels_route():
    # Get export format and user
    export_format, export_by = get_export_format_and_user()
    sort_by, sort_order = get_sorting_params(request, ['id', 'title'], default_field='id')
    search = get_search_query(request)
    channel_id = request.args.get("id", type=int)
    podcast_index_id = request.args.get("podcast_index_id", type=int)
    # Get max_rows parameter (defaults to 10000)-optional
    max_rows = request.args.get('max_rows', default=10000, type=int)
    if max_rows <= 0 or max_rows > 50000:  
        max_rows = 10000
    filters = request.args.to_dict()
    return export_channels_controller(search, sort_by, sort_order, max_rows, export_by, filters)


@channel_bp.route('/<int:channel_id>', methods=['GET'])
@limiter.limit("30 per minute")
@handle_errors
#@requires_auth
@audit_admin_access(action="GET_CHANNEL", resource="channel")
def get_single_channel(channel_id):
    data = get_channel_by_id_controller(channel_id)
    return jsonify(data)


@channel_bp.route('/by-feed', methods=['GET'])
@limiter.limit("30 per minute")
@handle_errors
#@requires_auth
@audit_admin_access(action="GET_CHANNELS_BY_FEED", resource="channel")
def get_channels_by_feed_route():
     # Get feed IDs from query parameter
    feed_ids = get_multi_filter_param(request, 'feed_ids', type_func=int)
    max_ids = request.args.get('max_ids', default=100, type=int)
    result = get_channels_by_feed_controller(feed_ids, max_ids)
    return jsonify(result)