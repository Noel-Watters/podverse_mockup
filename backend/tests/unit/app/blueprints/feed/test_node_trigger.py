# tests/unit/app/blueprints/feed/test_node_trigger.py

import pytest
from unittest.mock import MagicMock, patch, Mock
import requests

# ---- Fixtures ----
@pytest.fixture
def mock_session():
    with patch("app.blueprints.feed.services.node_trigger.db.session") as mock:
        yield mock

@pytest.fixture
def mock_logger():
    with patch("app.blueprints.feed.services.node_trigger.logger") as mock:
        yield mock

@pytest.fixture
def mock_requests():
    with patch("app.blueprints.feed.services.node_trigger.requests") as mock:
        yield mock

@pytest.fixture
def mock_time():
    with patch("app.blueprints.feed.services.node_trigger.time") as mock:
        yield mock

# ---- get_flag_status_id Tests ----
def test_get_flag_status_id_success(mock_session):
    """Test get_flag_status_id when flag status exists."""
    from app.blueprints.feed.services.node_trigger import get_flag_status_id
    
    # Mock FeedFlagStatus record
    mock_flag_status = Mock()
    mock_flag_status.id = 2
    
    mock_query = MagicMock()
    mock_session.query.return_value = mock_query
    mock_query.filter_by.return_value.first.return_value = mock_flag_status
    
    result = get_flag_status_id("active")
    
    assert result == 2
    mock_session.query.assert_called_once()
    mock_query.filter_by.assert_called_once_with(status="active")

def test_get_flag_status_id_not_found(mock_session):
    """Test get_flag_status_id when flag status doesn't exist."""
    from app.blueprints.feed.services.node_trigger import get_flag_status_id
    
    mock_query = MagicMock()
    mock_session.query.return_value = mock_query
    mock_query.filter_by.return_value.first.return_value = None
    
    with pytest.raises(RuntimeError, match="FeedFlagStatus 'inactive' not found"):
        get_flag_status_id("inactive")

# ---- normalize_feed_url Tests ----
def test_normalize_feed_url_basic():
    """Test normalize_feed_url with basic URL."""
    from app.blueprints.feed.services.node_trigger import normalize_feed_url
    
    url = "http://example.com/feed.xml"
    result = normalize_feed_url(url)
    
    assert result == "https://example.com/feed.xml"

def test_normalize_feed_url_with_trailing_slash():
    """Test normalize_feed_url with trailing slash."""
    from app.blueprints.feed.services.node_trigger import normalize_feed_url
    
    url = "https://example.com/feed.xml/"
    result = normalize_feed_url(url)
    
    assert result == "https://example.com/feed.xml"

def test_normalize_feed_url_with_uppercase_host():
    """Test normalize_feed_url with uppercase host."""
    from app.blueprints.feed.services.node_trigger import normalize_feed_url
    
    url = "https://EXAMPLE.COM/feed.xml"
    result = normalize_feed_url(url)
    
    assert result == "https://example.com/feed.xml"

def test_normalize_feed_url_with_query_params():
    """Test normalize_feed_url with query parameters."""
    from app.blueprints.feed.services.node_trigger import normalize_feed_url
    
    url = "http://example.com/feed.xml?param=value"
    result = normalize_feed_url(url)
    
    # Should remove query parameters
    assert result == "https://example.com/feed.xml"

def test_normalize_feed_url_with_fragment():
    """Test normalize_feed_url with fragment."""
    from app.blueprints.feed.services.node_trigger import normalize_feed_url
    
    url = "http://example.com/feed.xml#section"
    result = normalize_feed_url(url)
    
    # Should remove fragment
    assert result == "https://example.com/feed.xml"


# ---- trigger_node_parser Tests ----
def test_trigger_node_parser_success(mock_requests):
    """Test trigger_node_parser with successful response."""
    from app.blueprints.feed.services.node_trigger import trigger_node_parser
    
    # Mock successful response
    mock_response = MagicMock()
    mock_response.json.return_value = {"success": True, "message": "Parsing started"}
    mock_response.raise_for_status.return_value = None
    
    mock_requests.post.return_value = mock_response
    
    result = trigger_node_parser("https://example.com/feed.xml")
    
    assert result == {"success": True, "message": "Parsing started"}
    mock_requests.post.assert_called_once_with(
        "http://parse-service:3001/trigger-parse",
        json={"url": "https://example.com/feed.xml"},
        timeout=5
    )

def test_trigger_node_parser_with_podcast_index_id(mock_requests):
    """Test trigger_node_parser with podcast_index_id."""
    from app.blueprints.feed.services.node_trigger import trigger_node_parser
    
    # Mock successful response
    mock_response = MagicMock()
    mock_response.json.return_value = {"success": True, "message": "Parsing started"}
    mock_response.raise_for_status.return_value = None
    
    mock_requests.post.return_value = mock_response
    
    result = trigger_node_parser("https://example.com/feed.xml", podcast_index_id=12345)
    
    assert result == {"success": True, "message": "Parsing started"}
    mock_requests.post.assert_called_once_with(
        "http://parse-service:3001/trigger-parse",
        json={"url": "https://example.com/feed.xml", "podcast_index_id": 12345},
        timeout=5
    )

def test_trigger_node_parser_with_retry_success(mock_requests, mock_time):
    """Test trigger_node_parser with retry on first failure."""
    from app.blueprints.feed.services.node_trigger import trigger_node_parser
    
    # Mock first request fails, second succeeds
    mock_response = MagicMock()
    mock_response.json.return_value = {"success": True, "message": "Parsing started"}
    mock_response.raise_for_status.return_value = None
    
    mock_requests.post.side_effect = [
        requests.ConnectionError("Connection failed"),
        mock_response
    ]
    
    result = trigger_node_parser("https://example.com/feed.xml")
    
    assert result == {"success": True, "message": "Parsing started"}
    assert mock_requests.post.call_count == 2
    mock_time.sleep.assert_called_once()

def test_trigger_node_parser_with_retry_failure(mock_requests, mock_time):
    """Test trigger_node_parser with retry failure."""
    from app.blueprints.feed.services.node_trigger import trigger_node_parser
    
    # Mock both requests fail
    mock_requests.post.side_effect = [
        requests.ConnectionError("Connection failed"),
        requests.ConnectionError("Connection failed again")
    ]
    
    with pytest.raises(requests.ConnectionError, match="Connection failed again"):
        trigger_node_parser("https://example.com/feed.xml")
    
    assert mock_requests.post.call_count == 2
    assert mock_time.sleep.call_count == 1

def test_trigger_node_parser_timeout_error(mock_requests):
    """Test trigger_node_parser with timeout error."""
    from app.blueprints.feed.services.node_trigger import trigger_node_parser
    
    mock_requests.post.side_effect = requests.Timeout("Request timed out")
    
    with pytest.raises(requests.Timeout, match="Request timed out"):
        trigger_node_parser("https://example.com/feed.xml")

def test_trigger_node_parser_http_error(mock_requests):
    """Test trigger_node_parser with HTTP error."""
    from app.blueprints.feed.services.node_trigger import trigger_node_parser
    
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.reason = "Internal Server Error"
    
    mock_requests.post.side_effect = requests.HTTPError("HTTP Error", response=mock_response)
    
    with pytest.raises(requests.HTTPError, match="HTTP Error"):
        trigger_node_parser("https://example.com/feed.xml")

def test_trigger_node_parser_connection_error(mock_requests):
    """Test trigger_node_parser with connection error."""
    from app.blueprints.feed.services.node_trigger import trigger_node_parser
    
    mock_requests.post.side_effect = requests.ConnectionError("Connection refused")
    
    with pytest.raises(requests.ConnectionError, match="Connection refused"):
        trigger_node_parser("https://example.com/feed.xml")