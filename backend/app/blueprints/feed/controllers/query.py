from app.utils.request_logger import get_logger, log_database_operation
from app.blueprints.feed.services import get_feed_logs, get_feed_by_id, get_all_feeds
from app.blueprints.feed.schemas import feed_schema, feed_logs_schema, feeds_schema
from app.utils.query_params import get_pagination_params, get_sorting_params, get_search_query
from app.utils.error_exceptions import NotFoundError
from flask import request

logger = get_logger(__name__)

# Controllers
def get_feed_logs_controller(feed_id: int) -> dict:
    log_database_operation(logger, "READ", "feed_logs", f"feed_{feed_id}")
    logs = get_feed_logs(feed_id)
    serialized_logs = feed_logs_schema.dump(logs)
    logger.info(f"Retrieved and serialized {len(serialized_logs)} logs for feed ID {feed_id}")
    return {"logs": serialized_logs}


def get_feed_by_id_controller(feed_id: int) -> dict:
    log_database_operation(logger, "READ", "feeds", record_id=feed_id)
    feed = get_feed_by_id(feed_id)
    if not feed:
        logger.warning(f"Feed not found: ID {feed_id}")
        raise NotFoundError("Feed not found.")
    return feed_schema.dump(feed)


def get_all_feeds_controller() -> dict:
    page, limit = get_pagination_params(request)
    sort_by, sort_order = get_sorting_params(request, allowed_fields=['id', 'url', 'updated_at'], default_field='id')
    search = get_search_query(request)
    parsing_priority = request.args.get("parsing_priority")
    is_parsing = request.args.get("is_parsing")
    status = request.args.get("status")
    feed_id = request.args.get("id", type=int)
    podcast_index_id = request.args.get("podcast_index_id", type=int)

    log_database_operation(logger, "READ", "feeds", f"paginated_query_p{page}_l{limit}")

    result = get_all_feeds(
        page=page,
        limit=limit,
        parsing_priority=parsing_priority,
        is_parsing=is_parsing,
        status=status,
        feed_id=feed_id,
        podcast_index_id=podcast_index_id,
        sort_by=sort_by,
        sort_order=sort_order,
        search=search
    )

    return {
        "data": feeds_schema.dump(result["data"]),
        "meta": result["meta"]
    }
