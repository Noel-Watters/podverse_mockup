import pytest
from unittest.mock import MagicMock
from app.blueprints.item.services import get_item_detail
from app.utils.error_exceptions import NotFoundError, DatabaseError
from app.models.item import Item

class MockItem:
    id = 1
    title = "Mock Title"
    flag_status = None
    stats = []
    channel = None

def test_get_item_detail_success(monkeypatch):
    mock_item = MockItem()

    mock_query = MagicMock()
    mock_query.options.return_value = mock_query
    mock_query.filter_by.return_value.first.return_value = mock_item

    monkeypatch.setattr("app.blueprints.item.services.db.session.query", lambda *args: mock_query)

    result = get_item_detail(1)
    assert result.id == 1
    assert result.title == "Mock Title"

def test_get_item_detail_not_found(monkeypatch):
    mock_query = MagicMock()
    mock_query.options.return_value = mock_query
    mock_query.filter_by.return_value.first.return_value = None

    monkeypatch.setattr("app.blueprints.item.services.db.session.query", lambda *args: mock_query)

    with pytest.raises(NotFoundError):
        get_item_detail(999)

def test_get_item_detail_db_error(monkeypatch):
    def failing_query(*args, **kwargs):
        raise Exception("Unexpected failure")

    monkeypatch.setattr("app.blueprints.item.services.db.session.query", failing_query)

    with pytest.raises(DatabaseError):
        get_item_detail(1)