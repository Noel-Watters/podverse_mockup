# tests/unit/app/blueprints/channel/test_channel_schemas.py

import pytest
from marshmallow import ValidationError
from app.blueprints.channel.schemas import ChannelSchema, ChannelDetailSchema, ChannelExportSchema

# ---- Minimal Mock Classes ----
class MockCategory:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

class MockChannelCategory:
    def __init__(self, category):
        self.category = category

class MockMedium:
    def __init__(self, value):
        self.value = value

class MockFeed:
    def __init__(self, url=None, flag_status=None):
        self.url = url
        self.flag_status = flag_status

class MockFlagStatus:
    def __init__(self, status):
        self.status = status

class MockStats:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

class MockChannel:
    def __init__(self, **kwargs):
        # Set default attributes to prevent AttributeError
        self.categories = []
        self.medium = None
        self.feed = None
        self.stats = []
        self.id_text = None
        self.feed_id = None
        
        # Override with provided kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)

# ---- ChannelSchema Tests (Serialization Only) ----
def test_channel_schema_dump_with_relationships():
    """Test dumping channel with nested relationships"""
    category = MockCategory(id=1, display_name="Tech", mapping_key="tech")
    channel_cat = MockChannelCategory(category)
    medium = MockMedium("audio")
    channel = MockChannel(
        title="Test Channel",
        categories=[channel_cat],
        medium=medium
    )
    
    result = ChannelSchema().dump(channel)
    
    assert result["title"] == "Test Channel"
    assert result["categories"] == [{"id": 1, "display_name": "Tech", "mapping_key": "tech"}]
    assert result["medium"] == {"value": "audio"}


# ---- ChannelDetailSchema Tests ----
def test_channel_detail_schema_dump_complete():
    """Test dumping complete channel details"""
    category = MockCategory(
        id=1, 
        parent_id=0, 
        display_name="Business", 
        slug="business", 
        mapping_key="biz"
    )
    channel_cat = MockChannelCategory(category)
    medium = MockMedium("video")
    feed = MockFeed("http://example.com/feed")
    channel = MockChannel(
        title="Detail Channel",
        categories=[channel_cat],
        medium=medium,
        feed=feed
    )
    
    result = ChannelDetailSchema().dump(channel)
    
    assert result["title"] == "Detail Channel"
    assert result["categories"][0]["slug"] == "business"
    assert result["medium"]["value"] == "video"
    assert result["feed_url"] == "http://example.com/feed"


# ---- ChannelExportSchema Tests ----
def test_channel_export_schema_dump_complete():
    """Test dumping complete export data"""
    stats = MockStats(
        all_time_count=100,
        month_current_count=50,
        week_current_count=20,
        day_current_count=5
    )
    flag_status = MockFlagStatus("active")
    feed = MockFeed("http://example.com/feed", flag_status)
    medium = MockMedium("audio")
    channel = MockChannel(
        title="Export Channel",
        medium=medium,
        feed=feed,
        stats=[stats]
    )
    
    result = ChannelExportSchema().dump(channel)
    
    assert result["medium_name"] == "audio"
    assert result["feed_url"] == "http://example.com/feed"
    assert result["feed_status"] == "active"
    assert result["stats_all_time_count"] == 100
    assert result["stats_month_current_count"] == 50
    assert result["stats_week_current_count"] == 20
    assert result["stats_day_current_count"] == 5


# ---- Validation Tests ----
def test_channel_schema_title_validation():
    """Test title field validation."""
    schema = ChannelSchema()
    
    # Test valid title with all required fields
    data = {
        "title": "Valid Title",
        "id_text": "TEST123",
        "feed_id": 1,
        "podcast_index_id": 12345
    }
    result = schema.load(data)
    assert result.title == "Valid Title"  # Access as object attribute
    
    # Test empty title (should fail)
    with pytest.raises(ValidationError):
        schema.load({
            "title": "",
            "id_text": "TEST123",
            "feed_id": 1,
            "podcast_index_id": 12345
        })
    
    # Test title too long (should fail)
    with pytest.raises(ValidationError):
        schema.load({
            "title": "A" * 256,
            "id_text": "TEST123",
            "feed_id": 1,
            "podcast_index_id": 12345
        })

def test_channel_schema_missing_title():
    """Test that title is required."""
    schema = ChannelSchema()
    
    with pytest.raises(ValidationError):
        schema.load({
            "id_text": "TEST123",
            "feed_id": 1,
            "podcast_index_id": 12345
        })

def test_channel_schema_invalid_data_type():
    """Test invalid data type handling."""
    schema = ChannelSchema()
    
    with pytest.raises(ValidationError):
        schema.load({
            "title": 123,  # Title should be string
            "id_text": "TEST123",
            "feed_id": 1,
            "podcast_index_id": 12345
        })