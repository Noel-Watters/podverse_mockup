# tests/unit/app/blueprints/feed/test_bulk_service.py

import pytest
from unittest.mock import MagicMock, patch, Mock
from app.utils.error_exceptions import ValidationError, DatabaseError
from tests.conftest import MockFeed, MockFeedFlagStatus


# ---- Fixtures ----
@pytest.fixture
def mock_bulk_service_session():
    with patch("app.blueprints.feed.services.bulk_service.db.session") as mock:
        yield mock

@pytest.fixture
def mock_bulk_service_log_database_operation():
    with patch("app.blueprints.feed.services.bulk_service.log_database_operation") as mock:
        yield mock

@pytest.fixture
def mock_bulk_service_log_error():
    with patch("app.blueprints.feed.services.bulk_service.log_error") as mock:
        yield mock

# ---- bulk_update_feeds Tests ----
def test_bulk_update_feeds_success(mock_bulk_service_session, mock_bulk_service_log_database_operation):
    """Test successful bulk update of feeds."""
    from app.blueprints.feed.services.bulk_service import bulk_update_feeds
    
    # Mock feeds
    feed1 = MockFeed(id=1, parsing_priority=1)
    feed2 = MockFeed(id=2, parsing_priority=1)
    
    mock_bulk_service_session.get.side_effect = [feed1, feed2]
    
    feed_ids = [1, 2]
    updates = {"parsing_priority": 2}
    
    result = bulk_update_feeds(feed_ids, updates)
    
    assert result["updated"] == 2
    assert result["not_found"] == 0
    assert result["total_requested"] == 2
    assert len(result["results"]) == 2
    assert result["results"][0]["status"] == "updated"
    assert result["results"][1]["status"] == "updated"
    
    # Verify feeds were updated
    assert feed1.parsing_priority == 2
    assert feed2.parsing_priority == 2
    assert feed1.updated_at != feed1.created_at
    assert feed2.updated_at != feed2.created_at
    
    mock_bulk_service_session.commit.assert_called_once() # verify commit was called

def test_bulk_update_feeds_with_not_found_feeds(mock_bulk_service_session, mock_bulk_service_log_database_operation):
    """Test bulk update with some feeds not found."""
    from app.blueprints.feed.services.bulk_service import bulk_update_feeds
    
    # Mock one feed found, one not found
    feed1 = MockFeed(id=1, parsing_priority=1)
    mock_bulk_service_session.get.side_effect = [feed1, None]
    
    feed_ids = [1, 999]
    updates = {"parsing_priority": 2}
    
    result = bulk_update_feeds(feed_ids, updates)
    
    assert result["updated"] == 1
    assert result["not_found"] == 1
    assert result["total_requested"] == 2
    assert len(result["results"]) == 2
    assert result["results"][0]["status"] == "updated"
    assert result["results"][1]["status"] == "not_found"
    
    # Verify only found feed was updated
    assert feed1.parsing_priority == 2
    mock_bulk_service_session.commit.assert_called_once()

def test_bulk_update_feeds_with_feed_flag_status_id(mock_bulk_service_session, mock_bulk_service_log_database_operation):
    """Test bulk update with feed_flag_status_id."""
    from app.blueprints.feed.services.bulk_service import bulk_update_feeds
    
    # Mock flag status exists
    flag_status = MockFeedFlagStatus(id=2, status='inactive')
    mock_bulk_service_session.get.side_effect = [flag_status, MockFeed(id=1)]
    
    feed_ids = [1]
    updates = {"feed_flag_status_id": 2}
    
    result = bulk_update_feeds(feed_ids, updates)
    
    assert result["updated"] == 1
    assert result["not_found"] == 0
    mock_bulk_service_session.commit.assert_called_once()

def test_bulk_update_feeds_with_invalid_feed_flag_status_id(mock_bulk_service_session, mock_bulk_service_log_database_operation):
    """Test bulk update with invalid feed_flag_status_id."""
    from app.blueprints.feed.services.bulk_service import bulk_update_feeds
    
    mock_bulk_service_session.get.return_value = None # mock flag status doesn't exist
    
    feed_ids = [1]
    updates = {"feed_flag_status_id": 999}
    
    with pytest.raises(ValidationError, match="Invalid feed_flag_status_id"):
        bulk_update_feeds(feed_ids, updates)

def test_bulk_update_feeds_with_invalid_field(mock_bulk_service_session, mock_bulk_service_log_database_operation):
    """Test bulk update with invalid field."""
    from app.blueprints.feed.services.bulk_service import bulk_update_feeds
    
    feed_ids = [1]
    updates = {"invalid_field": "value"}
    
    with pytest.raises(ValidationError, match="Invalid update fields"):
        bulk_update_feeds(feed_ids, updates)

def test_bulk_update_feeds_with_multiple_valid_fields(mock_bulk_service_session, mock_bulk_service_log_database_operation):
    """Test bulk update with multiple valid fields."""
    from app.blueprints.feed.services.bulk_service import bulk_update_feeds
    
    # Mock flag status exists
    flag_status = MockFeedFlagStatus(id=2, status='inactive')
    feed = MockFeed(id=1, parsing_priority=1, container_id=None)
    mock_bulk_service_session.get.side_effect = [flag_status, feed]
    
    feed_ids = [1]
    updates = {
        "parsing_priority": 3,
        "container_id": "test-container",
        "feed_flag_status_id": 2
    }
    
    result = bulk_update_feeds(feed_ids, updates)
    
    assert result["updated"] == 1
    assert feed.parsing_priority == 3
    assert feed.container_id == "test-container"
    assert feed.feed_flag_status_id == 2
    mock_bulk_service_session.commit.assert_called_once()

def test_bulk_update_feeds_database_error(mock_bulk_service_session, mock_bulk_service_log_database_operation, mock_bulk_service_log_error):
    """Test bulk update with database error."""
    from app.blueprints.feed.services.bulk_service import bulk_update_feeds
    
    feed = MockFeed(id=1)
    mock_bulk_service_session.get.return_value = feed
    mock_bulk_service_session.commit.side_effect = Exception("Database error")
    
    feed_ids = [1]
    updates = {"parsing_priority": 2}
    
    with pytest.raises(DatabaseError, match="Failed to bulk update feeds"):
        bulk_update_feeds(feed_ids, updates)
    
    mock_bulk_service_session.rollback.assert_called_once() # verify rollback was called

def test_bulk_update_feeds_empty_feed_ids(mock_bulk_service_session, mock_bulk_service_log_database_operation):
    """Test bulk update with empty feed IDs list."""
    from app.blueprints.feed.services.bulk_service import bulk_update_feeds
    
    feed_ids = []
    updates = {"parsing_priority": 2}
    
    result = bulk_update_feeds(feed_ids, updates)
    
    assert result["updated"] == 0
    assert result["not_found"] == 0
    assert result["total_requested"] == 0
    assert len(result["results"]) == 0
    mock_bulk_service_session.commit.assert_called_once()

def test_bulk_update_feeds_empty_updates(mock_bulk_service_session, mock_bulk_service_log_database_operation):
    """Test bulk update with empty updates dict."""
    from app.blueprints.feed.services.bulk_service import bulk_update_feeds
    
    feed = MockFeed(id=1)
    mock_bulk_service_session.get.return_value = feed
    
    feed_ids = [1]
    updates = {}
    
    result = bulk_update_feeds(feed_ids, updates)
    
    assert result["updated"] == 1
    assert result["not_found"] == 0
    assert result["total_requested"] == 1
    # Feed should still be updated (updated_at timestamp)
    assert feed.updated_at != feed.created_at
    mock_bulk_service_session.commit.assert_called_once()

def test_bulk_update_feeds_all_not_found(mock_bulk_service_session, mock_bulk_service_log_database_operation):
    """Test bulk update with all feeds not found."""
    from app.blueprints.feed.services.bulk_service import bulk_update_feeds
    
    mock_bulk_service_session.get.return_value = None
    
    feed_ids = [999, 998, 997]
    updates = {"parsing_priority": 2}
    
    result = bulk_update_feeds(feed_ids, updates)
    
    assert result["updated"] == 0
    assert result["not_found"] == 3
    assert result["total_requested"] == 3
    assert all(r["status"] == "not_found" for r in result["results"])
    mock_bulk_service_session.commit.assert_called_once()

def test_bulk_update_feeds_validation_error_handling(mock_bulk_service_session, mock_bulk_service_log_database_operation):
    """Test that ValidationError is re-raised without rollback."""
    from app.blueprints.feed.services.bulk_service import bulk_update_feeds
    
    feed_ids = [1]
    updates = {"invalid_field": "value"}
    
    with pytest.raises(ValidationError):
        bulk_update_feeds(feed_ids, updates)
    
    mock_bulk_service_session.rollback.assert_not_called()  # shouldn't call rollback for validation erros