from app.blueprints.stats.schemas import StatsChannelSchema, StatsItemSchema, ChannelDetailWithStatsSchema
from datetime import datetime
# Test Schema Dumps and Loads to ensure valid Schemas

#### CHANNEL STATS SCHEMAS ####
def test_stats_aggregated_channel_schema_dump():
    input_data = {
        "channel_id": 1,
        "month_current_count": 100,
        "week_current_count": 50,
        "day_current_count": 10,
        "all_time_count": 1000,
    }

    schema = StatsChannelSchema()
    result = schema.dump(input_data)

    assert result["channel_id"] == 1
    assert result["month_current_count"] == 100
    assert result["all_time_count"] == 1000

def test_stats_aggregated_channel_schema_load():
    input_data = {
        "channel_id": 1,
        "month_current_count": 100,
        "week_current_count": 50,
        "day_current_count": 10,
        "all_time_count": 1000,
    }

    schema = StatsChannelSchema()
    loaded = schema.load(input_data)

    assert loaded.channel_id == 1
    assert loaded.week_current_count == 50
    assert loaded.day_current_count == 10

def test_channel_detail_with_stats_shema_dump():
    class MockCategory:
        def __init__(self):
            self.id = 2
            self.parent_id = 1
            self.display_name = "Test Category"
            self.slug = "example-category"
            self.mapping_key = "test_key"

    class MockChannelCategory:
        def __init__(self):
            self.category = MockCategory()

    class MockFlagStatus:
        def __init__(self):
            self.status = "active"

    class MockFeed:
        def __init__(self, channel=None):
            self.id = 2
            self.url = "https://example.com/rss"
            self.flag_status = MockFlagStatus()
            self.channels = [channel] if channel else []
            self.logs = []

    class MockItem:
        def __init__(self):
            self.id = 10
            self.title = "Test Item"
            self.guid = "abc123"
            self.pub_date = datetime(2025, 1, 1)

    class MockStats:
        def __init__(self):
            self.channel_id = 1
            self.month_current_count = 200
            self.week_current_count = 100
            self.day_current_count = 10
            self.all_time_count = 500

    class MockMedium:
        def __init__(self):
            self.value = "audio"

    class MockChannel:
        def __init__(self):
            self.id = 1
            self.id_text = "test"
            self.title = "Example Channel"
            self.slug = "example-channel"
            self.description = "A test channel"
            self.feed_id = 2
            self.podcast_index_id = 1
            self.categories = [MockChannelCategory()]
            self.stats = [MockStats()]
            self.items = [MockItem()]
            self.feed = MockFeed(channel=self)
            self.medium = MockMedium()

    schema = ChannelDetailWithStatsSchema()
    mock_channel = MockChannel()
    result = schema.dump(mock_channel)

    assert result["id"] == 1
    assert result["stats"][0]["channel_id"] == 1
    assert result["items"][0]["title"] == "Test Item"
    assert result["feed"]["url"] == "https://example.com/rss"
    assert result["categories"][0]["slug"] == "example-category"

#### ITEM STATS SCHEMAS

def test_stats_aggregated_item_schema_dump():
    input_data = {
        "item_id": 1,
        "month_current_count": 100,
        "week_current_count": 50,
        "day_current_count": 10,
        "all_time_count": 1000,
    }

    schema = StatsItemSchema()
    result = schema.dump(input_data)

    assert result["item_id"] == 1
    assert result["month_current_count"] == 100
    assert result["all_time_count"] == 1000

def test_stats_aggregated_item_schema_load():
    input_data = {
        "item_id": 1,
        "month_current_count": 100,
        "week_current_count": 50,
        "day_current_count": 10,
        "all_time_count": 1000,
    }

    schema = StatsItemSchema()
    loaded = schema.load(input_data)

    assert loaded.item_id == 1
    assert loaded.week_current_count == 50
    assert loaded.day_current_count == 10