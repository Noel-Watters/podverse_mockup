# tests/unit/app/blueprints/feed/test_export_service.py

import pytest
from unittest.mock import MagicMock, patch, Mock
from app.utils.error_exceptions import DatabaseError
from tests.conftest import MockFeed, MockFeedFlagStatus, MockChannel

# ---- Fixtures ----
@pytest.fixture
def mock_export_service_session():
    with patch("app.blueprints.feed.services.export_service.db.session") as mock:
        yield mock

@pytest.fixture
def mock_export_service_log_database_operation():
    with patch("app.blueprints.feed.services.export_service.log_database_operation") as mock:
        yield mock

@pytest.fixture
def mock_export_service_log_error():
    with patch("app.blueprints.feed.services.export_service.log_error") as mock:
        yield mock

@pytest.fixture
def mock_apply_sorting():
    with patch("app.blueprints.feed.services.export_service.apply_sorting") as mock:
        yield mock

@pytest.fixture
def mock_normalize_feed_url():
    with patch("app.blueprints.feed.services.export_service.normalize_feed_url") as mock:
        yield mock

@pytest.fixture
def mock_feeds_export_schema():
    with patch("app.blueprints.feed.services.export_service.feeds_export_schema") as mock:
        yield mock

# ---- get_feeds_for_export Tests ----

def test_get_feeds_for_export_basic(mock_export_service_session, mock_export_service_log_database_operation, mock_apply_sorting, mock_feeds_export_schema):
    """Test basic get_feeds_for_export functionality."""
    from app.blueprints.feed.services.export_service import get_feeds_for_export
    
    # Mock query chain
    mock_query = MagicMock()
    mock_export_service_session.query.return_value.join.return_value.outerjoin.return_value.options.return_value.order_by.return_value = mock_query
    mock_apply_sorting.return_value = mock_query
    mock_query.limit.return_value = mock_query
    mock_query.all.return_value = [MockFeed()]
    mock_feeds_export_schema.dump.return_value = [{"id": 1, "url": "https://example.com/feed.xml"}]
    
    result = get_feeds_for_export()
    
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["id"] == 1
    mock_feeds_export_schema.dump.assert_called_once()

def test_get_feeds_for_export_with_max_rows(mock_export_service_session, mock_export_service_log_database_operation, mock_apply_sorting, mock_feeds_export_schema):
    """Test get_feeds_for_export with max_rows parameter."""
    from app.blueprints.feed.services.export_service import get_feeds_for_export
    
    mock_query = MagicMock()
    mock_export_service_session.query.return_value.join.return_value.outerjoin.return_value.options.return_value.order_by.return_value = mock_query
    mock_apply_sorting.return_value = mock_query
    mock_query.limit.return_value = mock_query
    mock_query.all.return_value = [MockFeed()]
    mock_feeds_export_schema.dump.return_value = [{"id": 1}]
    
    result = get_feeds_for_export(max_rows=100)
    
    # Verify limit was called with the specified max_rows
    mock_query.limit.assert_called_with(100)
    assert isinstance(result, list)

def test_get_feeds_for_export_with_default_max_rows(mock_export_service_session, mock_export_service_log_database_operation, mock_apply_sorting, mock_feeds_export_schema):
    """Test get_feeds_for_export with default max_rows (10000)."""
    from app.blueprints.feed.services.export_service import get_feeds_for_export
    
    mock_query = MagicMock()
    mock_export_service_session.query.return_value.join.return_value.outerjoin.return_value.options.return_value.order_by.return_value = mock_query
    mock_apply_sorting.return_value = mock_query
    mock_query.limit.return_value = mock_query
    mock_query.all.return_value = [MockFeed()]
    mock_feeds_export_schema.dump.return_value = [{"id": 1}]
    
    result = get_feeds_for_export(max_rows=None)
    
    mock_query.limit.assert_called_with(10000) # verify limit was called with default 10000
    assert isinstance(result, list)

def test_get_feeds_for_export_with_feed_id_filter(mock_export_service_session, mock_export_service_log_database_operation, mock_apply_sorting, mock_feeds_export_schema):
    """Test get_feeds_for_export with feed_id filter."""
    from app.blueprints.feed.services.export_service import get_feeds_for_export
    
    mock_query = MagicMock()
    mock_export_service_session.query.return_value.join.return_value.outerjoin.return_value.options.return_value.order_by.return_value = mock_query
    mock_apply_sorting.return_value = mock_query
    mock_query.limit.return_value = mock_query
    mock_query.all.return_value = [MockFeed()]
    mock_feeds_export_schema.dump.return_value = [{"id": 123}]
    
    result = get_feeds_for_export(feed_id=123)
    
    # Verify filter was applied
    mock_query.filter.assert_called()
    assert isinstance(result, list)

def test_get_feeds_for_export_with_podcast_index_id_filter(mock_export_service_session, mock_export_service_log_database_operation, mock_apply_sorting, mock_feeds_export_schema):
    """Test get_feeds_for_export with podcast_index_id filter."""
    from app.blueprints.feed.services.export_service import get_feeds_for_export
    
    mock_query = MagicMock()
    mock_export_service_session.query.return_value.join.return_value.outerjoin.return_value.options.return_value.order_by.return_value = mock_query
    mock_apply_sorting.return_value = mock_query
    mock_query.limit.return_value = mock_query
    mock_query.all.return_value = [MockFeed()]
    mock_feeds_export_schema.dump.return_value = [{"id": 1}]
    
    result = get_feeds_for_export(podcast_index_id=12345)
    
    # Verify filter was applied
    mock_query.filter.assert_called()
    assert isinstance(result, list)

def test_get_feeds_for_export_with_invalid_podcast_index_id(mock_export_service_session, mock_export_service_log_database_operation):
    """Test get_feeds_for_export with invalid podcast_index_id."""
    from app.blueprints.feed.services.export_service import get_feeds_for_export
    from app.utils.error_exceptions import DatabaseError
    
    with pytest.raises(DatabaseError, match="podcast_index_id must be a valid integer"):
        get_feeds_for_export(podcast_index_id="invalid")

def test_get_feeds_for_export_with_negative_podcast_index_id(mock_export_service_session, mock_export_service_log_database_operation):
    """Test get_feeds_for_export with negative podcast_index_id."""
    from app.blueprints.feed.services.export_service import get_feeds_for_export
    from app.utils.error_exceptions import DatabaseError
    
    with pytest.raises(DatabaseError, match="podcast_index_id must be non-negative"):
        get_feeds_for_export(podcast_index_id=-1)

def test_get_feeds_for_export_with_search_integer(mock_export_service_session, mock_export_service_log_database_operation, mock_apply_sorting, mock_feeds_export_schema, mock_normalize_feed_url):
    """Test get_feeds_for_export with integer search term."""
    from app.blueprints.feed.services.export_service import get_feeds_for_export
    
    mock_query = MagicMock()
    mock_export_service_session.query.return_value.join.return_value.outerjoin.return_value.options.return_value.order_by.return_value = mock_query
    mock_apply_sorting.return_value = mock_query
    mock_query.limit.return_value = mock_query
    mock_query.all.return_value = [MockFeed()]
    mock_feeds_export_schema.dump.return_value = [{"id": 123}]
    
    result = get_feeds_for_export(search="123")
    
    # Verify search filter was applied
    mock_query.filter.assert_called()
    assert isinstance(result, list)

def test_get_feeds_for_export_with_search_url(mock_export_service_session, mock_export_service_log_database_operation, mock_apply_sorting, mock_feeds_export_schema, mock_normalize_feed_url):
    """Test get_feeds_for_export with URL search term."""
    from app.blueprints.feed.services.export_service import get_feeds_for_export
    
    mock_query = MagicMock()
    mock_export_service_session.query.return_value.join.return_value.outerjoin.return_value.options.return_value.order_by.return_value = mock_query
    mock_apply_sorting.return_value = mock_query
    mock_query.limit.return_value = mock_query
    mock_query.all.return_value = [MockFeed()]
    mock_feeds_export_schema.dump.return_value = [{"id": 1}]
    mock_normalize_feed_url.return_value = "https://example.com/feed.xml"
    
    result = get_feeds_for_export(search="https://example.com/feed.xml")
    
    # Verify search filter was applied and URL was normalized
    mock_query.filter.assert_called()
    mock_normalize_feed_url.assert_called()
    assert isinstance(result, list)

def test_get_feeds_for_export_with_search_text(mock_export_service_session, mock_export_service_log_database_operation, mock_apply_sorting, mock_feeds_export_schema):
    """Test get_feeds_for_export with text search term."""
    from app.blueprints.feed.services.export_service import get_feeds_for_export
    
    mock_query = MagicMock()
    mock_export_service_session.query.return_value.join.return_value.outerjoin.return_value.options.return_value.order_by.return_value = mock_query
    mock_apply_sorting.return_value = mock_query
    mock_query.limit.return_value = mock_query
    mock_query.all.return_value = [MockFeed()]
    mock_feeds_export_schema.dump.return_value = [{"id": 1}]
    
    result = get_feeds_for_export(search="test")
    
    mock_query.filter.assert_called() # verify search filter was applied
    assert isinstance(result, list)

def test_get_feeds_for_export_with_sorting(mock_export_service_session, mock_export_service_log_database_operation, mock_apply_sorting, mock_feeds_export_schema):
    """Test get_feeds_for_export with custom sorting."""
    from app.blueprints.feed.services.export_service import get_feeds_for_export
    
    mock_query = MagicMock()
    mock_export_service_session.query.return_value.join.return_value.outerjoin.return_value.options.return_value.order_by.return_value = mock_query
    mock_apply_sorting.return_value = mock_query
    mock_query.limit.return_value = mock_query
    mock_query.all.return_value = [MockFeed()]
    mock_feeds_export_schema.dump.return_value = [{"id": 1}]
    
    result = get_feeds_for_export(sort_by="url", sort_order="desc")
    
    mock_apply_sorting.assert_called()
    assert isinstance(result, list)

def test_get_feeds_for_export_database_error(mock_export_service_session, mock_export_service_log_database_operation, mock_export_service_log_error):
    """Test get_feeds_for_export with database error."""
    from app.blueprints.feed.services.export_service import get_feeds_for_export
    
    mock_export_service_session.query.side_effect = Exception("Database connection failed")
    
    with pytest.raises(DatabaseError, match="Failed to retrieve feeds for export"):
        get_feeds_for_export()

def test_get_feeds_for_export_empty_result(mock_export_service_session, mock_export_service_log_database_operation, mock_apply_sorting, mock_feeds_export_schema):
    """Test get_feeds_for_export with empty result."""
    from app.blueprints.feed.services.export_service import get_feeds_for_export
    
    mock_query = MagicMock()
    mock_export_service_session.query.return_value.join.return_value.outerjoin.return_value.options.return_value.order_by.return_value = mock_query
    mock_apply_sorting.return_value = mock_query
    mock_query.limit.return_value = mock_query
    mock_query.all.return_value = []
    mock_feeds_export_schema.dump.return_value = []
    
    result = get_feeds_for_export()
    
    assert isinstance(result, list)
    assert len(result) == 0
    mock_feeds_export_schema.dump.assert_called_once_with([])

def test_get_feeds_for_export_with_multiple_filters(mock_export_service_session, mock_export_service_log_database_operation, mock_apply_sorting, mock_feeds_export_schema):
    """Test get_feeds_for_export with multiple filters."""
    from app.blueprints.feed.services.export_service import get_feeds_for_export
    
    mock_query = MagicMock()
    mock_export_service_session.query.return_value.join.return_value.outerjoin.return_value.options.return_value.order_by.return_value = mock_query
    mock_apply_sorting.return_value = mock_query
    mock_query.limit.return_value = mock_query
    mock_query.all.return_value = [MockFeed()]
    mock_feeds_export_schema.dump.return_value = [{"id": 1}]
    
    result = get_feeds_for_export(
        search="test",
        sort_by="id",
        sort_order="asc",
        max_rows=500,
        feed_id=123,
        podcast_index_id=12345
    )
    
    # Verify filters were applied
    assert mock_query.filter.call_count >= 1  # At least one filter should be applied
    mock_apply_sorting.assert_called()
    mock_query.limit.assert_called_with(500)
    assert isinstance(result, list) 