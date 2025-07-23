# backend/tests/unit/app/blueprints/feed/test_query_service.py

import pytest
from unittest.mock import Mock, patch
from app.blueprints.feed.services.query_service import get_feed_logs
from app.utils.error_exceptions import ValidationError, NotFoundError
from app.models.feed import Feed, FeedLog
from datetime import datetime

# ---- Fixtures ----

@pytest.fixture
def mock_feed():
    """Mock feed object for testing."""
    feed = Mock(spec=Feed)
    feed.id = 1
    return feed

@pytest.fixture
def mock_feed_logs():
    """Mock feed logs for testing."""
    logs = []
    for i in range(5):
        log = Mock(spec=FeedLog)
        log.id = i
        log.feed_id = 1
        log.is_success = i % 2 == 0  # Alternate between success and failure
        log.finished_at = datetime.utcnow()
        logs.append(log)
    return logs

# ---- Tests ----

@patch('app.blueprints.feed.services.query_service.paginate_query')
@patch('app.blueprints.feed.services.query_service.db')
def test_get_feed_logs_success_only_true(mock_db, mock_paginate_query, mock_feed, mock_feed_logs):
    """Test filtering logs with success_only=true."""
    # Setup
    mock_db.session.get.return_value = mock_feed
    mock_query = Mock()
    mock_db.session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.order_by.return_value = mock_query
    
    # Mock pagination result
    success_logs = [log for log in mock_feed_logs if log.is_success]
    mock_paginate_query.return_value = (success_logs, {"total_items": len(success_logs), "page": 1, "limit": 50})
    
    # Execute
    result = get_feed_logs(feed_id=1, success_only="true")
    
    # Assert
    assert result["logs"] == success_logs
    mock_query.filter.assert_called()

@patch('app.blueprints.feed.services.query_service.paginate_query')
@patch('app.blueprints.feed.services.query_service.db')
def test_get_feed_logs_error_only_true(mock_db, mock_paginate_query, mock_feed, mock_feed_logs):
    """Test filtering logs with error_only=true."""
    # Setup
    mock_db.session.get.return_value = mock_feed
    mock_query = Mock()
    mock_db.session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.order_by.return_value = mock_query
    
    # Mock pagination result
    error_logs = [log for log in mock_feed_logs if not log.is_success]
    mock_paginate_query.return_value = (error_logs, {"total_items": len(error_logs), "page": 1, "limit": 50})
    
    # Execute
    result = get_feed_logs(feed_id=1, error_only="true")
    
    # Assert
    assert result["logs"] == error_logs
    mock_query.filter.assert_called()

@patch('app.blueprints.feed.services.query_service.db')
def test_get_feed_logs_both_parameters_raises_error(mock_db, mock_feed):
    """Test that using both success_only and error_only raises ValidationError."""
    # Setup
    mock_db.session.get.return_value = mock_feed
    
    # Execute and assert
    with pytest.raises(ValidationError, match="Cannot use both 'success_only' and 'error_only' parameters together"):
        get_feed_logs(feed_id=1, success_only="true", error_only="true")

@patch('app.blueprints.feed.services.query_service.db')
def test_get_feed_logs_feed_not_found(mock_db):
    """Test that NotFoundError is raised when feed doesn't exist."""
    # Setup
    mock_db.session.get.return_value = None
    
    # Execute and assert
    with pytest.raises(NotFoundError, match="Feed not found"):
        get_feed_logs(feed_id=999)

@patch('app.blueprints.feed.services.query_service.paginate_query')
@patch('app.blueprints.feed.services.query_service.db')
def test_get_feed_logs_no_filtering(mock_db, mock_paginate_query, mock_feed, mock_feed_logs):
    """Test getting logs without any filtering."""
    # Setup
    mock_db.session.get.return_value = mock_feed
    mock_query = Mock()
    mock_db.session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.order_by.return_value = mock_query
    
    # Mock pagination result
    mock_paginate_query.return_value = (mock_feed_logs, {"total_items": len(mock_feed_logs), "page": 1, "limit": 50})
    
    # Execute
    result = get_feed_logs(feed_id=1)
    
    # Assert
    assert result["logs"] == mock_feed_logs
    # Should not apply any success/error filtering
    assert mock_query.filter.call_count == 1  # Only the feed_id filter 