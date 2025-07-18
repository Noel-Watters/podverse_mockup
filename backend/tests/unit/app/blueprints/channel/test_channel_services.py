import pytest
from unittest.mock import MagicMock, patch

# Mocked Channel model stub
class FakeChannel:
    def __init__(self, id=1, feed_id=None):
        self.id = id
        self.feed_id = feed_id
        self.title = "Test"

# ---- Fixtures ----

@pytest.fixture
def mock_session():
    with patch("app.blueprints.channel.services.db.session") as mock:
        yield mock

@pytest.fixture
def mock_eagerload():
    with patch("app.blueprints.channel.services.channel_eagerload_options", return_value=[]):
        yield

# ---- Tests ----

def test_get_channels_list_returns_data(mock_session, mock_eagerload):
    from app.blueprints.channel.services import get_channels_list
    with patch("app.blueprints.channel.services.paginate_query", return_value=([FakeChannel()], {"total_items": 1})):
        result, meta = get_channels_list(search=None, sort_by="id", sort_order="asc", page=1, limit=10)
        assert isinstance(result, list)
        assert meta["total_items"] == 1

def test_get_channels_for_export_limited_result(mock_session, mock_eagerload):
    from app.blueprints.channel.services import get_channels_for_export
    # Mock the complete query chain properly
    mock_query = MagicMock()
    mock_session.query.return_value = mock_query
    mock_query.options.return_value = mock_query
    mock_query.filter.return_value = mock_query  # For any filter calls
    mock_query.order_by.return_value = mock_query  # For apply_sorting
    mock_query.limit.return_value = mock_query
    mock_query.all.return_value = [FakeChannel()]
    result = get_channels_for_export(max_rows=5)
    assert isinstance(result, list)

def test_get_channel_detail_found(mock_session, mock_eagerload):
    from app.blueprints.channel.services import get_channel_detail
    mock_session.query.return_value.options.return_value.filter_by.return_value.first.return_value = FakeChannel(id=42)
    result = get_channel_detail(42)
    assert result.id == 42

def test_get_channel_detail_not_found(mock_session, mock_eagerload):
    from app.blueprints.channel.services import get_channel_detail
    from app.utils.error_exceptions import NotFoundError
    mock_session.query.return_value.options.return_value.filter_by.return_value.first.return_value = None
    with pytest.raises(NotFoundError):
        get_channel_detail(999)

def test_get_channels_by_feed_ids_truncated(mock_session, mock_eagerload):
    from app.blueprints.channel.services import get_channels_by_feed_ids
    mock_session.query.return_value.options.return_value.filter.return_value.all.return_value = [FakeChannel(feed_id=1)]
    result = get_channels_by_feed_ids(feed_ids=list(range(150)), max_ids=100)
    assert len(result) == 1

def test_get_channels_by_feed_ids_none():
    from app.blueprints.channel.services import get_channels_by_feed_ids
    result = get_channels_by_feed_ids(feed_ids=[])
    assert result == []
