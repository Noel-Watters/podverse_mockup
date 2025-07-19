# backend/app/blueprints/stats/routes.py

from flask import jsonify
from app.blueprints.stats import stats_bp
from app.utils.request_logger import get_logger, log_request
from app.utils.error_handlers import handle_errors
from app.blueprints.stats.controller import list_channel_stats, get_channel_stat_details_by_id, list_item_stats, get_item_stat_details_by_id

logger = get_logger(__name__)

@handle_errors
@stats_bp.route('/channels', methods=['GET'])
def list_channel_stats_route():

    log_request(logger, 'GET', '/stats/channels')

    # Pass the request into the controller
    data = list_channel_stats()

    return jsonify({
        "data": data["results"],
        "meta": {
            "page": data["page"],
            "per_page": data["per_page"],
            "total": data["total"],
            "view": data["view"]
        }
    }), 200

@handle_errors
@stats_bp.route('/channels/<int:channel_id>', methods=['GET'])
def get_channel_stats_detail(channel_id):

    log_request(logger, 'GET', f'/stats/channels/{channel_id}')
        
    data = get_channel_stat_details_by_id(channel_id)

    return jsonify({"data": data}), 200


@handle_errors
@stats_bp.route('/items', methods=['GET'])
def list_item_stats():

    log_request(logger, 'GET', '/stats/items')

    data = list_item_stats()

    return jsonify({
        "data": data["results"],
        "meta": {
            "page": data["page"],
            "per_page": data["per_page"],
            "total": data["total"],
            "view": data["view"]
        }
}), 200

@handle_errors
@stats_bp.route('/items/<int:item_id>', methods=['GET'])
def get_item_stats_detail(item_id):

    log_request(logger, 'GET', f'/stats/items/{item_id}')

    data = get_item_stat_details_by_id(item_id)

    return jsonify({
        "data": data
    }), 200


