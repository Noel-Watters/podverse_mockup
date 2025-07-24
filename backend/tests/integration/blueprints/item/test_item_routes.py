import pytest
from app.models.item import Item

def test_get_item_detail_success(test_client, monkeypatch):
    class MockItem:
        id = 1
        title = "Test Item"
        flag_status = None
        stats = []
        channel = None

    def mock_get_item_detail(item_id):
        return MockItem()

    monkeypatch.setattr("app.blueprints.item.controller.get_item_detail", mock_get_item_detail)

    response = test_client.get("/admin/items/1")
    assert response.status_code == 200
    data = response.get_json()
    assert data["id"] == 1
    assert "title" in data

def test_get_item_detail_not_found(test_client, monkeypatch):
    from app.utils.error_exceptions import NotFoundError

    def mock_get_item_detail(item_id):
        raise NotFoundError("Item not found")

    monkeypatch.setattr("app.blueprints.item.controller.get_item_detail", mock_get_item_detail)
    
    response = test_client.get("/admin/items/999")
    assert response.status_code == 404
    assert response.get_json()["error"]["message"] == "Item not found"

def test_get_item_detail_server_error(test_client, monkeypatch):
    from app.utils.error_exceptions import DatabaseError

    def mock_get_item_detail(item_id):
        raise DatabaseError("DB failure")

    monkeypatch.setattr("app.blueprints.item.controller.get_item_detail", mock_get_item_detail)

    response = test_client.get("/admin/items/1")
    assert response.status_code == 500
    assert response.get_json()["error"]["message"] == "Failed to retrieve item"