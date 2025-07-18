# app/blueprints/feed/services/node_trigger.py

import urllib.parse
import requests
import time
from app.utils.request_logger import get_logger
from app.extensions import db

logger = get_logger(__name__)

def get_flag_status_id(status: str) -> int:
    from app.models.feed import FeedFlagStatus
    record = db.session.query(FeedFlagStatus).filter_by(status=status).first()
    if not record:
        raise RuntimeError(f"FeedFlagStatus '{status}' not found")
    return record.id

def normalize_feed_url(url: str) -> str: 
    """
    Normalize a feed URL for consistent storage and comparison.
    - Force HTTPS
    - Remove trailing slashes
    - Lowercase the scheme and host
    
    Args:
        url (str): The URL to normalize
        
    Returns:
        str: The normalized URL
    """
    parsed = urllib.parse.urlparse(url.strip())
    scheme = 'https'
    # Normalize host to lowercase
    netloc = parsed.netloc.lower()
    # Normalize path (remove trailing slash)
    path = parsed.path.rstrip('/')
    # Reconstruct URL
    normalized_url = urllib.parse.urlunparse((
        scheme,
        netloc,
        path,
        '',  # params
        '',  # query
        ''   # fragment
    ))
    return normalized_url

def trigger_node_parser(url: str, podcast_index_id: int = None):
    """
    Trigger the Node.js parser service to parse a feed.
    
    Args:
        url (str): The feed URL to parse
        podcast_index_id (int, optional): The podcast index ID
        
    Returns:
        dict: The response from the parser service
        
    Raises:
        requests.RequestException: If the request fails after retries
    """
    for attempt in range(2):  # 1 retry
        try:
            payload = {"url": url}
            if podcast_index_id is not None:
                payload["podcast_index_id"] = podcast_index_id
                            
            response = requests.post("http://parse-service:3001/trigger-parse", json=payload, timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            if attempt == 1:
                raise
            time.sleep(1) 