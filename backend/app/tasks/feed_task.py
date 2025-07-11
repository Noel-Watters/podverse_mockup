# celery async task for parsing/updating feeds

from celery import shared_task
from celery.app.task import Task
from typing import Dict, List, Any
from app.extensions import db
from app.models import Feed
from app.blueprints.feed.services import parse_and_update_feed_object
from app.utils.error_exceptions import NotFoundError
from app.utils.helpers import get_flag_status_id
from app.utils.redis_lock import redis_lock
from app.utils.request_logger import get_logger
from datetime import datetime, timedelta
from sqlalchemy import and_

logger = get_logger(__name__)

@shared_task(bind=True, max_retries=3, default_retry_delay=60)  # 60 seconds between retries, 3 retries max
def reparse_feed_task(self: Task, feed_id: int) -> Dict[str, int]:
    """
    Celery task to reparse a single feed.
    
    Args:
        self: Celery task instance
        feed_id: ID of the feed to reparse
        
    Returns:
        Dict[str, int]: Dictionary containing number of feeds reparsed
        
    Raises:
        NotFoundError: If feed with given ID doesn't exist
    """
    try:
        # call parse and update feed object in task wrapper so celery can queue and run it
        feed = db.session.get(Feed, feed_id)
        if not feed:
            raise NotFoundError(f"Feed with ID {feed_id} not found")
        return parse_and_update_feed_object(feed)
    except NotFoundError:
        self.retry(exc=NotFoundError)
    except Exception as e:
        self.retry(exc=e)
    return {"reparsed": 1}


@shared_task
def fetch_feed(feed_id):
    # TODO: get feed from db using the id 
    # TODO: call parse_rss_feed(feed.url) 
    # TODO: update feed and items in database
    pass


# Where to use Celery
# In a task module, e.g. tasks.py
# For /feeds/{id}/reparse, call trigger_reparse.delay(feed_id)
# Task sets is_parsing = True, calls feedparser, logs result, resets is_parsing

