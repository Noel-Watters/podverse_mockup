# tests/unit/app/blueprints/feed/test_parsing_service.py

import pytest
from unittest.mock import MagicMock, patch, Mock
from datetime import datetime
import requests
from app.utils.error_exceptions import NotFoundError, DatabaseError

# ---- Mock Classes ----

class MockFlagStatus:
    def __init__(self, status="active"):
        self.status = status

class MockFeed:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id', 1)
        self.url = kwargs.get('url', 'https://example.com/feed.xml')
        self.parsing_priority = kwargs.get('parsing_priority', 1)
        self.is_parsing = kwargs.get('is_parsing', False)
        self.created_at = kwargs.get('created_at', datetime.utcnow())
        self.updated_at = kwargs.get('updated_at', datetime.utcnow())
        self.channels = kwargs.get('channels', [])
        self.logs = kwargs.get('logs', [])
        # Add flag_status with default active status
        self.flag_status = kwargs.get('flag_status', MockFlagStatus())

class MockChannel:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id', 1)
        self.title = kwargs.get('title', 'Test Channel')
        self.podcast_index_id = kwargs.get('podcast_index_id', 12345)

class MockFeedLog:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id', 1)
        self.feed_id = kwargs.get('feed_id', 1)
        self.http_status = kwargs.get('http_status', 200)
        self.is_success = kwargs.get('is_success', True)
        self.parse_error_message = kwargs.get('parse_error_message', None)
        self.started_at = kwargs.get('started_at', datetime.utcnow())
        self.finished_at = kwargs.get('finished_at', datetime.utcnow())
        self.parsed_by = kwargs.get('parsed_by', 'test@example.com')

# ---- Fixtures ----

@pytest.fixture
def mock_session():
    with patch("app.blueprints.feed.services.parsing_service.db.session") as mock:
        yield mock

@pytest.fixture
def mock_logger():
    with patch("app.blueprints.feed.services.parsing_service.logger") as mock:
        yield mock

@pytest.fixture
def mock_get_current_auth0_id():
    with patch("app.blueprints.feed.services.parsing_service.get_current_auth0_id") as mock:
        yield mock

@pytest.fixture
def mock_normalize_feed_url():
    with patch("app.blueprints.feed.services.parsing_service.normalize_feed_url") as mock:
        yield mock

@pytest.fixture
def mock_requests():
    with patch("app.blueprints.feed.services.parsing_service.requests") as mock:
        yield mock

@pytest.fixture
def mock_time():
    with patch("app.blueprints.feed.services.parsing_service.time") as mock:
        yield mock

@pytest.fixture
def mock_random():
    with patch("app.blueprints.feed.services.parsing_service.random") as mock:
        yield mock

# ---- parse_and_update_feed_object Tests ----

def test_parse_and_update_feed_object_success(mock_session, mock_get_current_auth0_id, mock_normalize_feed_url, mock_requests):
    """Test successful parse_and_update_feed_object."""
    from app.blueprints.feed.services.parsing_service import parse_and_update_feed_object
    
    # Mock feed
    feed = MockFeed(id=1, is_parsing=False, channels=[MockChannel(podcast_index_id=12345)])
    
    # Mock successful response
    mock_response = MagicMock()
    mock_response.json.return_value = {"success": True, "message": "Parsing started"}
    mock_response.status_code = 200
    mock_requests.post.return_value = mock_response
    
    # Mock URL normalization
    mock_normalize_feed_url.return_value = "https://example.com/feed.xml"
    
    # Mock auth0 ID
    mock_get_current_auth0_id.return_value = "auth0|123456"
    
    # Mock session methods
    mock_session.begin.return_value = None
    mock_session.flush.return_value = None
    mock_session.commit.return_value = None
    
    result = parse_and_update_feed_object(feed)
    
    assert result["status"] == "success"
    assert result["feed_id"] == 1
    
    # Verify log was created
    mock_session.add.assert_called_once()

def test_parse_and_update_feed_object_already_parsing(mock_session):
    """Test parse_and_update_feed_object when feed is already parsing."""
    from app.blueprints.feed.services.parsing_service import parse_and_update_feed_object
    
    feed = MockFeed(id=1, is_parsing=True)
    
    result = parse_and_update_feed_object(feed)
    
    assert result["status"] == "error"
    assert result["message"] == "Already parsing"
    assert result["feed_id"] == 1

def test_parse_and_update_feed_object_without_channel(mock_session, mock_get_current_auth0_id, mock_normalize_feed_url, mock_requests):
    """Test parse_and_update_feed_object without channel."""
    from app.blueprints.feed.services.parsing_service import parse_and_update_feed_object
    
    feed = MockFeed(id=1, is_parsing=False, channels=[])
    
    # Mock successful response
    mock_response = MagicMock()
    mock_response.json.return_value = {"success": True, "message": "Parsing started"}
    mock_response.status_code = 200
    mock_requests.post.return_value = mock_response
    
    mock_normalize_feed_url.return_value = "https://example.com/feed.xml"
    mock_get_current_auth0_id.return_value = "auth0|123456"
    
    result = parse_and_update_feed_object(feed)
    
    assert result["status"] == "success"
    # Should not include podcast_index_id in payload
    mock_requests.post.assert_called_once_with(
        "http://parse-service:3001/trigger-parse",
        json={"url": "https://example.com/feed.xml"},
        timeout=5
    )

def test_parse_and_update_feed_object_parser_error(mock_session, mock_get_current_auth0_id, mock_normalize_feed_url, mock_requests):
    """Test parse_and_update_feed_object with parser service error."""
    from app.blueprints.feed.services.parsing_service import parse_and_update_feed_object
    
    feed = MockFeed(id=1, is_parsing=False)
    
    # Mock parser service error response
    mock_response = MagicMock()
    mock_response.json.return_value = {"success": False, "message": "Invalid RSS feed"}
    mock_response.status_code = 400
    mock_requests.post.return_value = mock_response
    
    mock_normalize_feed_url.return_value = "https://example.com/feed.xml"
    mock_get_current_auth0_id.return_value = "auth0|123456"
    
    result = parse_and_update_feed_object(feed)
    
    assert result["status"] == "error"
    assert "Invalid RSS feed" in result["message"]
    assert feed.is_parsing is False
    
    # Verify error log was created
    mock_session.add.assert_called_once()
    log_call = mock_session.add.call_args[0][0]
    assert log_call.is_success is False
    assert "Invalid RSS feed" in log_call.parse_error_message

def test_parse_and_update_feed_object_timeout_error(mock_session, mock_get_current_auth0_id, mock_normalize_feed_url, mock_requests):
    """Test parse_and_update_feed_object with timeout error."""
    from app.blueprints.feed.services.parsing_service import parse_and_update_feed_object
    
    feed = MockFeed(id=1, is_parsing=False)
    
    mock_requests.post.side_effect = requests.Timeout("Request timed out")
    mock_normalize_feed_url.return_value = "https://example.com/feed.xml"
    mock_get_current_auth0_id.return_value = "auth0|123456"
    
    result = parse_and_update_feed_object(feed)
    
    assert result["status"] == "error"
    assert "timed out" in result["message"]
    assert feed.is_parsing is False
    
    # Verify error log was created
    mock_session.add.assert_called_once()
    log_call = mock_session.add.call_args[0][0]
    assert log_call.is_success is False
    assert "timed out" in log_call.parse_error_message

def test_parse_and_update_feed_object_connection_error(mock_session, mock_get_current_auth0_id, mock_normalize_feed_url, mock_requests):
    """Test parse_and_update_feed_object with connection error."""
    from app.blueprints.feed.services.parsing_service import parse_and_update_feed_object
    
    feed = MockFeed(id=1, is_parsing=False)
    
    mock_requests.post.side_effect = requests.ConnectionError("Connection refused")
    mock_normalize_feed_url.return_value = "https://example.com/feed.xml"
    mock_get_current_auth0_id.return_value = "auth0|123456"
    
    result = parse_and_update_feed_object(feed)
    
    assert result["status"] == "error"
    assert "Parsing failed: Connection refused" in result["message"]
    assert feed.is_parsing is False

def test_parse_and_update_feed_object_http_404_error(mock_session, mock_get_current_auth0_id, mock_normalize_feed_url, mock_requests):
    """Test parse_and_update_feed_object with HTTP 404 error."""
    from app.blueprints.feed.services.parsing_service import parse_and_update_feed_object
    
    feed = MockFeed(id=1, is_parsing=False)
    
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_requests.post.side_effect = requests.HTTPError("HTTP Error", response=mock_response)
    
    mock_normalize_feed_url.return_value = "https://example.com/feed.xml"
    mock_get_current_auth0_id.return_value = "auth0|123456"
    
    result = parse_and_update_feed_object(feed)
    
    assert result["status"] == "error"
    assert "Parsing failed: HTTP Error" in result["message"]
    assert feed.is_parsing is False

def test_parse_and_update_feed_object_http_403_error(mock_session, mock_get_current_auth0_id, mock_normalize_feed_url, mock_requests):
    """Test parse_and_update_feed_object with HTTP 403 error."""
    from app.blueprints.feed.services.parsing_service import parse_and_update_feed_object
    
    feed = MockFeed(id=1, is_parsing=False)
    
    mock_response = MagicMock()
    mock_response.status_code = 403
    mock_requests.post.side_effect = requests.HTTPError("HTTP Error", response=mock_response)
    
    mock_normalize_feed_url.return_value = "https://example.com/feed.xml"
    mock_get_current_auth0_id.return_value = "auth0|123456"
    
    result = parse_and_update_feed_object(feed)
    
    assert result["status"] == "error"
    assert "Parsing failed: HTTP Error" in result["message"]
    assert feed.is_parsing is False

def test_parse_and_update_feed_object_http_500_error(mock_session, mock_get_current_auth0_id, mock_normalize_feed_url, mock_requests):
    """Test parse_and_update_feed_object with HTTP 500 error."""
    from app.blueprints.feed.services.parsing_service import parse_and_update_feed_object
    
    feed = MockFeed(id=1, is_parsing=False)
    
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_requests.post.side_effect = requests.HTTPError("HTTP Error", response=mock_response)
    
    mock_normalize_feed_url.return_value = "https://example.com/feed.xml"
    mock_get_current_auth0_id.return_value = "auth0|123456"
    
    result = parse_and_update_feed_object(feed)
    
    assert result["status"] == "error"
    assert "Parsing failed: HTTP Error" in result["message"]
    assert feed.is_parsing is False

def test_parse_and_update_feed_object_retry_success(mock_session, mock_get_current_auth0_id, mock_normalize_feed_url, mock_requests, mock_time, mock_random):
    """Test parse_and_update_feed_object with retry success."""
    from app.blueprints.feed.services.parsing_service import parse_and_update_feed_object
    
    feed = MockFeed(id=1, is_parsing=False)
    
    # Mock first request fails, second succeeds
    mock_response = MagicMock()
    mock_response.json.return_value = {"success": True, "message": "Parsing started"}
    mock_response.status_code = 200
    
    mock_requests.post.side_effect = [
        requests.ConnectionError("Connection failed"),
        mock_response
    ]
    
    mock_normalize_feed_url.return_value = "https://example.com/feed.xml"
    mock_get_current_auth0_id.return_value = "auth0|123456"
    mock_random.uniform.return_value = 0.5
    
    result = parse_and_update_feed_object(feed)
    
    assert result["status"] == "success"
    assert mock_requests.post.call_count == 2
    mock_time.sleep.assert_called_once_with(1.5)  # 2^0 + 0.5

def test_parse_and_update_feed_object_retry_failure(mock_session, mock_get_current_auth0_id, mock_normalize_feed_url, mock_requests, mock_time, mock_random):
    """Test parse_and_update_feed_object with retry failure."""
    from app.blueprints.feed.services.parsing_service import parse_and_update_feed_object
    
    feed = MockFeed(id=1, is_parsing=False)
    
    # Mock both requests fail
    mock_requests.post.side_effect = [
        requests.ConnectionError("Connection failed"),
        requests.ConnectionError("Connection failed again")
    ]
    
    mock_normalize_feed_url.return_value = "https://example.com/feed.xml"
    mock_get_current_auth0_id.return_value = "auth0|123456"
    mock_random.uniform.return_value = 0.5
    
    result = parse_and_update_feed_object(feed)
    
    assert result["status"] == "error"
    assert "Parsing failed: Connection failed again" in result["message"]
    assert mock_requests.post.call_count == 2
    mock_time.sleep.assert_called_once()

def test_parse_and_update_feed_object_no_auth0_id(mock_session, mock_get_current_auth0_id, mock_normalize_feed_url, mock_requests):
    """Test parse_and_update_feed_object without auth0 ID."""
    from app.blueprints.feed.services.parsing_service import parse_and_update_feed_object
    
    feed = MockFeed(id=1, is_parsing=False)
    
    mock_response = MagicMock()
    mock_response.json.return_value = {"success": True, "message": "Parsing started"}
    mock_response.status_code = 200
    mock_requests.post.return_value = mock_response
    
    mock_normalize_feed_url.return_value = "https://example.com/feed.xml"
    mock_get_current_auth0_id.return_value = None
    
    result = parse_and_update_feed_object(feed)
    
    assert result["status"] == "success"
    
    # Verify log was created with default parsed_by
    mock_session.add.assert_called_once()
    log_call = mock_session.add.call_args[0][0]
    assert log_call.parsed_by == "system@podverse.com"

# ---- parse_and_update_feed Tests ----

def test_parse_and_update_feed_success(mock_session):
    """Test parse_and_update_feed with existing feed."""
    from app.blueprints.feed.services.parsing_service import parse_and_update_feed
    
    feed = MockFeed(id=123)
    mock_session.get.return_value = feed
    
    with patch("app.blueprints.feed.services.parsing_service.parse_and_update_feed_object") as mock_parse:
        mock_parse.return_value = {"status": "success", "feed_id": 123}
        
        result = parse_and_update_feed(123)
        
        assert result["status"] == "success"
        assert result["feed_id"] == 123
        mock_session.get.assert_called_once()
        mock_parse.assert_called_once_with(feed)

def test_parse_and_update_feed_not_found(mock_session):
    """Test parse_and_update_feed with non-existent feed."""
    from app.blueprints.feed.services.parsing_service import parse_and_update_feed
    
    mock_session.get.return_value = None
    
    with pytest.raises(NotFoundError, match="Feed not found"):
        parse_and_update_feed(999)

# ---- bulk_reparse_feeds Tests ----

def test_bulk_reparse_feeds_success(mock_session):
    """Test successful bulk_reparse_feeds."""
    from app.blueprints.feed.services.parsing_service import bulk_reparse_feeds
    
    # Mock feeds with active status
    feed1 = MockFeed(id=1, is_parsing=False)
    feed1.flag_status = Mock()
    feed1.flag_status.status = "active"
    
    feed2 = MockFeed(id=2, is_parsing=False)
    feed2.flag_status = Mock()
    feed2.flag_status.status = "active"
    
    mock_session.get.side_effect = [feed1, feed2]
    
    with patch("app.blueprints.feed.services.parsing_service.parse_and_update_feed") as mock_parse:
        mock_parse.side_effect = [
            {"status": "success", "feed_id": 1},
            {"status": "success", "feed_id": 2}
        ]
        
        result = bulk_reparse_feeds([1, 2])
        
        assert result["success"] == 2
        assert result["failed"] == 0
        assert result["not_found"] == 0
        assert result["already_parsing"] == 0
        assert result["total_requested"] == 2
        assert len(result["results"]) == 2
        assert result["results"][0]["status"] == "success"
        assert result["results"][1]["status"] == "success"

def test_bulk_reparse_feeds_with_not_found(mock_session):
    """Test bulk_reparse_feeds with some feeds not found."""
    from app.blueprints.feed.services.parsing_service import bulk_reparse_feeds
    
    with patch("app.blueprints.feed.services.parsing_service.parse_and_update_feed") as mock_parse:
        # First call succeeds, second call raises NotFoundError
        mock_parse.side_effect = [
            {"status": "success", "feed_id": 1},
            NotFoundError("Feed not found")
        ]
        
        result = bulk_reparse_feeds([1, 999])
        
        assert result["success"] == 1
        assert result["failed"] == 0
        assert result["not_found"] == 1
        assert result["already_parsing"] == 0
        assert result["total_requested"] == 2
        assert result["results"][0]["status"] == "success"
        assert result["results"][1]["status"] == "not_found"

def test_bulk_reparse_feeds_with_already_parsing(mock_session):
    """Test bulk_reparse_feeds with feeds already parsing."""
    from app.blueprints.feed.services.parsing_service import bulk_reparse_feeds
    from app.utils.error_exceptions import ValidationError
    
    with patch("app.blueprints.feed.services.parsing_service.parse_and_update_feed") as mock_parse:
        # First call raises ValidationError for already parsing, second call succeeds
        mock_parse.side_effect = [
            ValidationError("Feed is already being parsed", status_code=409),
            {"status": "success", "feed_id": 2}
        ]
        
        result = bulk_reparse_feeds([1, 2])
        
        assert result["success"] == 1
        assert result["failed"] == 0
        assert result["not_found"] == 0
        assert result["already_parsing"] == 1
        assert result["total_requested"] == 2
        assert result["results"][0]["status"] == "already_parsing"
        assert result["results"][1]["status"] == "success"

def test_bulk_reparse_feeds_with_skipped_flag(mock_session):
    """Test bulk_reparse_feeds with feeds having non-active flag status."""
    from app.blueprints.feed.services.parsing_service import bulk_reparse_feeds
    from app.utils.error_exceptions import ValidationError
    
    with patch("app.blueprints.feed.services.parsing_service.parse_and_update_feed") as mock_parse:
        # First call raises ValidationError for non-eligible flag status, second call succeeds
        mock_parse.side_effect = [
            ValidationError("Feed is not eligible (status: inactive)", status_code=400),
            {"status": "success", "feed_id": 2}
        ]
        
        result = bulk_reparse_feeds([1, 2])
        
        assert result["success"] == 1
        assert result["failed"] == 0
        assert result["not_found"] == 0
        assert result["already_parsing"] == 0
        assert result["total_requested"] == 2
        assert result["results"][0]["status"] == "skipped_flag"
        assert result["results"][1]["status"] == "success"

def test_bulk_reparse_feeds_with_parse_errors(mock_session):
    """Test bulk_reparse_feeds with parse errors."""
    from app.blueprints.feed.services.parsing_service import bulk_reparse_feeds
    
    feed1 = MockFeed(id=1, is_parsing=False)
    feed1.flag_status = Mock()
    feed1.flag_status.status = "active"
    
    feed2 = MockFeed(id=2, is_parsing=False)
    feed2.flag_status = Mock()
    feed2.flag_status.status = "active"
    
    mock_session.get.side_effect = [feed1, feed2]
    
    with patch("app.blueprints.feed.services.parsing_service.parse_and_update_feed") as mock_parse:
        mock_parse.side_effect = [
            {"status": "error", "feed_id": 1, "message": "Parse failed"},
            {"status": "success", "feed_id": 2}
        ]
        
        result = bulk_reparse_feeds([1, 2])
        
        assert result["success"] == 1
        assert result["failed"] == 1
        assert result["not_found"] == 0
        assert result["already_parsing"] == 0
        assert result["total_requested"] == 2
        assert result["results"][0]["status"] == "error"
        assert result["results"][1]["status"] == "success"

def test_bulk_reparse_feeds_with_exception(mock_session):
    """Test bulk_reparse_feeds with exception during parsing."""
    from app.blueprints.feed.services.parsing_service import bulk_reparse_feeds
    
    feed1 = MockFeed(id=1, is_parsing=False)
    feed1.flag_status = Mock()
    feed1.flag_status.status = "active"
    
    mock_session.get.return_value = feed1
    
    with patch("app.blueprints.feed.services.parsing_service.parse_and_update_feed") as mock_parse:
        mock_parse.side_effect = Exception("Unexpected error")
        
        result = bulk_reparse_feeds([1])
        
        assert result["success"] == 0
        assert result["failed"] == 1
        assert result["not_found"] == 0
        assert result["already_parsing"] == 0
        assert result["total_requested"] == 1
        assert result["results"][0]["status"] == "error"
        assert "Unexpected error" in result["results"][0]["error"]

def test_bulk_reparse_feeds_empty_list(mock_session):
    """Test bulk_reparse_feeds with empty feed list."""
    from app.blueprints.feed.services.parsing_service import bulk_reparse_feeds
    
    result = bulk_reparse_feeds([])
    
    assert result["success"] == 0
    assert result["failed"] == 0
    assert result["not_found"] == 0
    assert result["already_parsing"] == 0
    assert result["total_requested"] == 0
    assert len(result["results"]) == 0 