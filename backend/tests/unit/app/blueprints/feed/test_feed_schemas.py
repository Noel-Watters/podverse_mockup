# tests/unit/app/blueprints/feed/test_feed_schemas.py

from datetime import datetime
from app.blueprints.feed.schemas import BaseFeedSchema, FeedSchema, FeedExportSchema, feed_schema, feeds_schema, feed_log_schema, feed_logs_schema, feed_flag_status_schema, feed_flag_statuses_schema, feed_export_schema, feeds_export_schema
from tests.conftest import MockFeed, MockFeedFlagStatus, MockChannel

# ---- Mock Classes ----
class MockFeedLog:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id', 1)
        self.feed_id = kwargs.get('feed_id', 1)
        self.http_status = kwargs.get('http_status', 200)
        self.is_success = kwargs.get('is_success', True)
        self.parse_error_message = kwargs.get('parse_error_message', None)
        self.started_at = kwargs.get('started_at', datetime.utcnow())
        self.finished_at = kwargs.get('finished_at', datetime.utcnow())
        self.parsed_by = kwargs.get('parsed_by', 'test@example.com')

# ---- FeedLogSchema Tests ----
def test_feed_log_schema_dump():
    """Test FeedLogSchema serialization."""
    log = MockFeedLog(
        id=1,
        feed_id=1,
        http_status=200,
        is_success=True,
        parse_error_message=None,
        started_at=datetime(2023, 1, 1, 12, 0, 0),
        finished_at=datetime(2023, 1, 1, 12, 1, 0),
        parsed_by='test@example.com'
    )
    
    result = feed_log_schema.dump(log)
    
    assert result['id'] == 1
    assert result['feed_id'] == 1
    assert result['http_status'] == 200
    assert result['is_success'] is True
    assert result['parse_error_message'] is None
    assert result['parsed_by'] == 'test@example.com'

def test_feed_logs_schema_dump_multiple():
    """Test FeedLogSchema with multiple logs."""
    logs = [
        MockFeedLog(id=1, is_success=True),
        MockFeedLog(id=2, is_success=False, parse_error_message='Error occurred')
    ]
    
    result = feed_logs_schema.dump(logs)
    
    assert len(result) == 2
    assert result[0]['id'] == 1
    assert result[0]['is_success'] is True
    assert result[1]['id'] == 2
    assert result[1]['is_success'] is False
    assert result[1]['parse_error_message'] == 'Error occurred'

# ---- FeedFlagStatusSchema Tests ----
def test_feed_flag_status_schema_dump():
    """Test FeedFlagStatusSchema serialization."""
    flag_status = MockFeedFlagStatus(
        id=1,
        status='active'
    )
    
    result = feed_flag_status_schema.dump(flag_status)
    
    assert result['id'] == 1
    assert result['status'] == 'active'

def test_feed_flag_statuses_schema_dump_multiple():
    """Test FeedFlagStatusSchema with multiple statuses."""
    statuses = [
        MockFeedFlagStatus(id=1, status='active'),
        MockFeedFlagStatus(id=2, status='inactive')
    ]
    
    result = feed_flag_statuses_schema.dump(statuses)
    
    assert len(result) == 2
    assert result[0]['status'] == 'active'
    assert result[1]['status'] == 'inactive'

# ---- BaseFeedSchema Tests ----
def test_base_feed_schema_get_flag_status():
    """Test get_flag_status method."""
    schema = BaseFeedSchema()
    
    # Test with flag status
    feed = MockFeed(flag_status=MockFeedFlagStatus(status='active'))
    result = schema.get_flag_status(feed)
    assert result == 'active'
    
    # Test without flag status
    feed_no_flag = MockFeed(flag_status=None)
    result = schema.get_flag_status(feed_no_flag)
    assert result is None

def test_base_feed_schema_get_channel_title():
    """Test get_channel_title method."""
    schema = BaseFeedSchema()
    
    # Test with single channel
    feed = MockFeed(channels=[MockChannel(title='Test Channel')])
    result = schema.get_channel_title(feed)
    assert result == 'Test Channel'
    
    # Test with multiple channels (should use first)
    feed_multiple = MockFeed(channels=[
        MockChannel(title='First Channel'),
        MockChannel(title='Second Channel')
    ])
    result = schema.get_channel_title(feed_multiple)
    assert result == 'First Channel'
    
    # Test with no channels
    feed_no_channels = MockFeed(channels=[])
    result = schema.get_channel_title(feed_no_channels)
    assert result is None

def test_base_feed_schema_get_channel_podcast_index_id():
    """Test get_channel_podcast_index_id method."""
    schema = BaseFeedSchema()
    
    # Test with channel
    feed = MockFeed(channels=[MockChannel(podcast_index_id=12345)])
    result = schema.get_channel_podcast_index_id(feed)
    assert result == 12345
    

# ---- FeedSchema Tests ----
def test_feed_schema_dump():
    """Test FeedSchema serialization."""
    feed = MockFeed(
        id=1,
        url='https://example.com/feed.xml',
        parsing_priority=2,
        is_parsing=False,
        flag_status=MockFeedFlagStatus(status='active'),
        channels=[MockChannel(title='Test Channel', podcast_index_id=12345)]
    )
    
    result = feed_schema.dump(feed)
    
    assert result['id'] == 1
    assert result['url'] == 'https://example.com/feed.xml'
    assert result['parsing_priority'] == 2
    assert result['is_parsing'] is False
    assert result['flag_status'] == 'active'
    assert result['channel_title'] == 'Test Channel'
    assert result['channel_podcast_index_id'] == 12345
    assert 'recent_logs' in result

def test_feed_schema_get_recent_logs():
    """Test get_recent_logs method."""
    schema = FeedSchema()
    
    # Create logs with different timestamps
    old_log = MockFeedLog(id=1, finished_at=datetime(2023, 1, 1, 12, 0, 0))
    new_log = MockFeedLog(id=2, finished_at=datetime(2023, 1, 1, 12, 2, 0))
    middle_log = MockFeedLog(id=3, finished_at=datetime(2023, 1, 1, 12, 1, 0))
    
    feed = MockFeed(logs=[old_log, new_log, middle_log])
    
    result = schema.get_recent_logs(feed)
    
    # Should return 2 most recent logs, sorted by finished_at desc
    assert len(result) == 2
    assert result[0]['id'] == 2  # newest
    assert result[1]['id'] == 3  # middle

def test_feed_schema_get_recent_logs_empty():
    """Test get_recent_logs with no logs."""
    schema = FeedSchema()
    feed = MockFeed(logs=[])
    
    result = schema.get_recent_logs(feed)
    assert result == []


# ---- FeedExportSchema Tests ----
def test_feed_export_schema_dump():
    """Test FeedExportSchema serialization."""
    feed = MockFeed(
        id=1,
        url='https://example.com/feed.xml',
        parsing_priority=1,
        flag_status=MockFeedFlagStatus(status='active'),
        channels=[MockChannel(title='Test Channel', podcast_index_id=12345)]
    )
    
    result = feed_export_schema.dump(feed)
    
    assert result['id'] == 1
    assert result['url'] == 'https://example.com/feed.xml'
    assert result['parsing_priority'] == 1
    assert result['flag_status'] == 'active'
    assert result['channel_title'] == 'Test Channel'
    assert result['channel_podcast_index_id'] == 12345
    assert 'last_parse_error' in result
    assert 'parse_error_count' in result
    assert 'last_successful_parse_at' in result
    assert 'channel_issue' in result

def test_feed_export_schema_get_last_parse_error():
    """Test get_last_parse_error method."""
    schema = FeedExportSchema()
    
    # Test with error logs
    error_log1 = MockFeedLog(
        id=1,
        is_success=False,
        parse_error_message='First error',
        finished_at=datetime(2023, 1, 1, 12, 0, 0)
    )
    error_log2 = MockFeedLog(
        id=2,
        is_success=False,
        parse_error_message='Second error',
        finished_at=datetime(2023, 1, 1, 12, 1, 0)
    )
    
    feed = MockFeed(logs=[error_log1, error_log2])
    
    result = schema.get_last_parse_error(feed)
    
    # Should return most recent error
    assert 'Second error' in result
    assert '2023-01-01 12:01:00' in result

def test_feed_export_schema_get_last_parse_error_no_errors():
    """Test get_last_parse_error with no error logs."""
    schema = FeedExportSchema()
    
    success_log = MockFeedLog(
        id=1,
        is_success=True,
        finished_at=datetime(2023, 1, 1, 12, 0, 0)
    )
    
    feed = MockFeed(logs=[success_log])
    
    result = schema.get_last_parse_error(feed)
    assert result is None

def test_feed_export_schema_get_parse_error_count():
    """Test get_parse_error_count method."""
    schema = FeedExportSchema()
    
    # Mix of success and error logs
    logs = [
        MockFeedLog(id=1, is_success=True),
        MockFeedLog(id=2, is_success=False),
        MockFeedLog(id=3, is_success=True),
        MockFeedLog(id=4, is_success=False)
    ]
    
    feed = MockFeed(logs=logs)
    
    result = schema.get_parse_error_count(feed)
    assert result == 2

def test_feed_export_schema_get_last_successful_parse_at():
    """Test get_last_successful_parse_at method."""
    schema = FeedExportSchema()
    
    # Mix of success and error logs with different timestamps
    logs = [
        MockFeedLog(id=1, is_success=True, finished_at=datetime(2023, 1, 1, 12, 0, 0)),
        MockFeedLog(id=2, is_success=False, finished_at=datetime(2023, 1, 1, 12, 1, 0)),
        MockFeedLog(id=3, is_success=True, finished_at=datetime(2023, 1, 1, 12, 2, 0))
    ]
    
    feed = MockFeed(logs=logs)
    
    result = schema.get_last_successful_parse_at(feed)
    
    # Should return the latest successful parse
    assert result == datetime(2023, 1, 1, 12, 2, 0)

def test_feed_export_schema_get_last_successful_parse_at_no_success():
    """Test get_last_successful_parse_at with no successful parses."""
    schema = FeedExportSchema()
    
    error_log = MockFeedLog(id=1, is_success=False)
    feed = MockFeed(logs=[error_log])
    
    result = schema.get_last_successful_parse_at(feed)
    assert result is None


# ---- Schema Instance Tests ----
def test_feeds_schema_dump_multiple():
    """Test feeds_schema with multiple feeds."""
    feeds = [
        MockFeed(id=1, url='https://example1.com/feed.xml'),
        MockFeed(id=2, url='https://example2.com/feed.xml')
    ]
    
    result = feeds_schema.dump(feeds)
    
    assert len(result) == 2
    assert result[0]['id'] == 1
    assert result[0]['url'] == 'https://example1.com/feed.xml'
    assert result[1]['id'] == 2
    assert result[1]['url'] == 'https://example2.com/feed.xml'

def test_feeds_export_schema_dump_multiple():
    """Test feeds_export_schema with multiple feeds."""
    feeds = [
        MockFeed(id=1, url='https://example1.com/feed.xml'),
        MockFeed(id=2, url='https://example2.com/feed.xml')
    ]
    
    result = feeds_export_schema.dump(feeds)
    
    assert len(result) == 2
    assert result[0]['id'] == 1
    assert result[1]['id'] == 2
    assert 'last_parse_error' in result[0]
    assert 'parse_error_count' in result[0] 