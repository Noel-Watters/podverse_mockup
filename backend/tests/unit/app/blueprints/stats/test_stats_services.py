import pytest
from datetime import datetime

from sqlalchemy import Function, func
from app.blueprints.stats.services import get_channel_stats, get_item_stats, get_channel_stats_detail
from app.utils.error_exceptions import DatabaseError
from unittest.mock import MagicMock

# Mock a query for use with mocking joins adn the Get alls
class MockPaginatedQuery:
    def __init__(self, data):
        self.data = data

    def join(self, *args, **kwargs):
        return self

    def filter(self, *args, **kwargs):
        return self

    def order_by(self, *args, **kwargs):
        return self

    def paginate(self, page, per_page, error_out):
        return type("Pagination", (), {
            "items": self.data,
            "page": page,
            "per_page": per_page,
            "total": len(self.data)
        })

# For detail stats ( Getting by ID )
class MockDetailQuery:
    def __init__(self, result=None):
        self.result = result

    def filter(self, *args, **kwargs):
        return self

    def first(self):
        return self.result
    
    def options(self, *args, **kwargs):
        return self

    def scalar(self):
        return self._count
    
class MockEventQuery:
    def __init__(self, count=5):
        self._count = count

    def filter(self, *args, **kwargs):
        return self

    def scalar(self):
        return self._count

class MockChannelModel:
    id = MagicMock(name="Channel.id")
    stats = []
    items = []
    feed = None
    categories = []
    medium = None

class MockChannelInstance:
    def __init__(self):
        self.id = 1
        self.title = "Test Channel"
        self.stats = []
        self.items = []
        self.feed = None
        self.categories = []
        self.medium = None
        self.raw_event_count = None

@pytest.fixture
def mock_channel_stats_data():
    class MockStatsAggregatedChannel:
        def __init__(self):
            self.channel_id = 1
            self.month_current_count = 100
            self.week_current_count = 50
            self.day_current_count = 10
            self.all_time_count = 500
            self.channel = type('MockChannel', (), {
                'id': 1,
                'title': "Example Channel",
                'slug': "example-channel",
                'feed_id': 2
            })()
    return [MockStatsAggregatedChannel()]

@pytest.fixture
def mock_item_stats_data():
    class MockStatsAggregatedItem:
        def __init__(self):
            self.item_id = 1
            self.month_current_count = 200
            self.week_current_count = 80
            self.day_current_count = 20
            self.all_time_count = 1000
            self.item = type('MockItem', (), {
                'id': 1,
                'title': "Example Item",
                'guid': "abc123"
            })()
    return [MockStatsAggregatedItem()]

def test_get_channel_stats_with_mock_data(monkeypatch, mock_channel_stats_data):
    mock_query = MockPaginatedQuery(mock_channel_stats_data)

    monkeypatch.setattr("app.blueprints.stats.services.db.session.query", lambda *args, **kwargs: mock_query)

    filters = {
        "search": "Example",
        "sort_by": "month_current_count",
        "sort_order": "desc",
        "page": 1,
        "per_page": 1,
        "view": "monthly"
    }

    result = get_channel_stats(filters)
    assert "results" in result
    assert isinstance(result["results"], list)
    assert result["results"][0]["week_current_count"] == 50

def test_get_item_stats_with_mock_data(monkeypatch, mock_item_stats_data):
    mock_query = MockPaginatedQuery(mock_item_stats_data)
    
    monkeypatch.setattr("app.blueprints.stats.services.db.session.query", lambda *args, **kwargs: mock_query)

    filters = {
        "search": "Example",
        "sort_by": "month_current_count",
        "sort_order": "desc",
        "page": 1,
        "per_page": 1,
        "view": "monthly"
    }

    result = get_item_stats(filters)
    assert isinstance(result["results"], list)
    assert result["page"] == 1
    assert result["view"] == "monthly"


### CHANNEL DETAIL #####
def test_get_channel_stats_detail_success(monkeypatch):
    mock_channel = MockChannelInstance()

    # Patch the Channel queries * Had to use workaround to avoid trying to access Columns from the Channel Model
    def fake_query(*args, **kwargs):
        if args and hasattr(args[0], '__name__') and args[0].__name__ == "Channel":
            return MockDetailQuery(mock_channel)
        elif args and isinstance(args[0], Function):
            return MockEventQuery(5)  # Simulate raw event count
        raise ValueError(f"Unexpected query args: {args}")
            
    monkeypatch.setattr("app.blueprints.stats.services.db.session.query", fake_query)

    monkeypatch.setattr("app.models.channel.Channel.id", MagicMock(name="Channel.id"))

    result = get_channel_stats_detail(channel_id=1)
    
    assert isinstance(result, dict)
    assert result["id"] == 1
    assert "title" in result

def test_get_channel_stats_detail_not_found(monkeypatch):
    mock_query = MockDetailQuery(None)

    monkeypatch.setattr("app.blueprints.stats.services.db.session.query", lambda *args, **kwargs: mock_query)

    with pytest.raises(DatabaseError) as excinfo:
        get_channel_stats_detail(channel_id=999)

    assert "Failed to retrieve channel details" in str(excinfo.value)