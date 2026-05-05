import pytest
from datetime import datetime
from app.blueprints.item.schemas import ItemSchema, ItemFlagStatusSchema
from app.models.item import Item, ItemFlagStatus

def test_item_schema_serialization():
    mock_item = Item(
        id=1,
        id_text="item-1",
        channel_id=2,
        item_flag_status_id=3,
        title="Test Episode",
        slug="test-episode",
        guid="abc123",
        guid_enclosure_url="https://example.com/audio.mp3",
        pub_date=datetime(2023, 7, 1, 10, 0, 0),
        flag_status=ItemFlagStatus(id=3, status="active")
    )

    schema = ItemSchema()
    result = schema.dump(mock_item)

    assert result["id"] == 1
    assert result["title"] == "Test Episode"
    assert result["flag_status"]["status"] == "active"
    assert "guid_enclosure_url" in result

def test_item_schema_deserialization():
    payload = {
        "id": 2,
        "id_text": "item-2",
        "channel_id": 1,
        "item_flag_status_id": 3,
        "title": "Another Episode",
        "slug": "another-episode",
        "guid": "def456",
        "guid_enclosure_url": "https://example.com/audio2.mp3",
        "pub_date": "2023-08-01T12:30:00"
    }

    schema = ItemSchema()
    schema.transient = True
    result = schema.load(payload)

    assert result.title == "Another Episode"
    assert result.slug == "another-episode"
    assert result.channel_id == 1
    assert result.guid == "def456"

def test_item_flag_status_schema_serialization():
    flag_status = ItemFlagStatus(id=99, status="archived")
    schema = ItemFlagStatusSchema()
    result = schema.dump(flag_status)

    assert result["id"] == 99
    assert result["status"] == "archived"