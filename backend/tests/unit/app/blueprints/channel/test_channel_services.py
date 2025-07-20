import pytest
from unittest.mock import MagicMock, patch
from tests.conftest import MockChannel

# ---- Fixtures ----
@pytest.fixture
def mock_channel_service_session():
    with patch("app.blueprints.channel.services.db.session") as mock:
        yield mock

@pytest.fixture
def mock_eagerload():
    with patch("app.blueprints.channel.services.channel_eagerload_options", return_value=[]):
        yield

# ---- Tests ----
def test_get_channels_list_returns_data(mock_channel_service_session, mock_eagerload):
    from app.blueprints.channel.services import get_channels_list
    with patch("app.blueprints.channel.services.paginate_query", return_value=([MockChannel()], {"total_items": 1})):
        result, meta = get_channels_list(search=None, sort_by="id", sort_order="asc", page=1, limit=10)
        assert isinstance(result, list)
        assert meta["total_items"] == 1

def test_get_channels_for_export_limited_result(mock_channel_service_session, mock_eagerload):
    from app.blueprints.channel.services import get_channels_for_export
    # Mock the complete query chain properly
    mock_query = MagicMock()
    mock_channel_service_session.query.return_value = mock_query
    mock_query.options.return_value = mock_query
    mock_query.filter.return_value = mock_query  # For any filter calls
    mock_query.order_by.return_value = mock_query  # For apply_sorting
    mock_query.limit.return_value = mock_query
    mock_query.all.return_value = [MockChannel()]
    result = get_channels_for_export(max_rows=5)
    assert isinstance(result, list)

def test_get_channel_detail_found(mock_channel_service_session, mock_eagerload):
    from app.blueprints.channel.services import get_channel_detail
    mock_channel_service_session.query.return_value.options.return_value.filter_by.return_value.first.return_value = MockChannel(id=42)
    result = get_channel_detail(42)
    assert result.id == 42

def test_get_channel_detail_not_found(mock_channel_service_session, mock_eagerload):
    from app.blueprints.channel.services import get_channel_detail
    from app.utils.error_exceptions import NotFoundError
    mock_channel_service_session.query.return_value.options.return_value.filter_by.return_value.first.return_value = None
    with pytest.raises(NotFoundError):
        get_channel_detail(999)

def test_get_channels_by_feed_ids_truncated(mock_channel_service_session, mock_eagerload):
    from app.blueprints.channel.services import get_channels_by_feed_ids
    mock_channel_service_session.query.return_value.options.return_value.filter.return_value.all.return_value = [MockChannel(feed_id=1)]
    result = get_channels_by_feed_ids(feed_ids=list(range(150)), max_ids=100)
    assert len(result) == 1

def test_get_channels_by_feed_ids_none():
    from app.blueprints.channel.services import get_channels_by_feed_ids
    result = get_channels_by_feed_ids(feed_ids=[])
    assert result == []

# ---- Error Handling Tests ----

def test_get_channels_list_database_error(mock_channel_service_session, mock_eagerload):
    """Test database error handling in get_channels_list."""
    from app.blueprints.channel.services import get_channels_list
    from app.utils.error_exceptions import DatabaseError
    
    mock_channel_service_session.query.side_effect = Exception("Database connection failed")
    
    with pytest.raises(DatabaseError):
        get_channels_list(search=None, sort_by="id", sort_order="asc", page=1, limit=10)

def test_get_channel_detail_database_error(mock_channel_service_session, mock_eagerload):
    """Test database error handling in get_channel_detail."""
    from app.blueprints.channel.services import get_channel_detail
    from app.utils.error_exceptions import DatabaseError
    
    mock_channel_service_session.query.side_effect = Exception("Database connection failed")
    
    with pytest.raises(DatabaseError):
        get_channel_detail(42)

def test_get_channels_by_feed_ids_database_error(mock_channel_service_session, mock_eagerload):
    """Test database error handling in get_channels_by_feed_ids."""
    from app.blueprints.channel.services import get_channels_by_feed_ids
    from app.utils.error_exceptions import DatabaseError
    
    mock_channel_service_session.query.side_effect = Exception("Database connection failed")
    
    with pytest.raises(DatabaseError):
        get_channels_by_feed_ids(feed_ids=[1, 2, 3])

def test_get_channels_for_export_database_error(mock_channel_service_session, mock_eagerload):
    """Test database error handling in get_channels_for_export."""
    from app.blueprints.channel.services import get_channels_for_export
    from app.utils.error_exceptions import DatabaseError
    
    mock_channel_service_session.query.side_effect = Exception("Database connection failed")
    
    with pytest.raises(DatabaseError):
        get_channels_for_export(max_rows=100)
