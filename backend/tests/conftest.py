# Import test configuration to override environment variables FIRST
import test_config 

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
from app import create_app
from app.extensions import db as _db
import os

# Load environment variables from .env.test.local
def load_env_file(filepath):
    """Load environment variables from a .env file"""
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value

# Load test environment variables
load_env_file(os.path.join(os.path.dirname(__file__), '.env.test.local'))

# Debug: Print the DATABASE_URL to see what's being loaded
print(f"DEBUG: DATABASE_URL = {os.environ.get('DATABASE_URL', 'NOT SET')}")
print(f"DEBUG: TEST_DATABASE_URL = {os.environ.get('TEST_DATABASE_URL', 'NOT SET')}")
print(f"DEBUG: FLASK_ENV = {os.environ.get('FLASK_ENV', 'NOT SET')}")

# ---- Standardized Mock Classes ----
class MockFeed:
    """Standardized mock for Feed model."""
    def __init__(self, **kwargs):
        self.id = kwargs.get('id', 1)
        self.url = kwargs.get('url', 'https://example.com/feed.xml')
        self.parsing_priority = kwargs.get('parsing_priority', 1)
        self.is_parsing = kwargs.get('is_parsing', False)
        self.container_id = kwargs.get('container_id', None)
        self.feed_flag_status_id = kwargs.get('feed_flag_status_id', 1)
        self.last_parsed_file_hash = kwargs.get('last_parsed_file_hash', None)
        self.created_at = kwargs.get('created_at', datetime.utcnow())
        self.updated_at = kwargs.get('updated_at', datetime.utcnow())
        self.channels = kwargs.get('channels', [])
        self.logs = kwargs.get('logs', [])
        self.flag_status = kwargs.get('flag_status', None)

class MockFeedFlagStatus:
    """Standardized mock for FeedFlagStatus model."""
    def __init__(self, **kwargs):
        self.id = kwargs.get('id', 1)
        self.status = kwargs.get('status', 'active')
        self.description = kwargs.get('description', 'Active feed')

class MockFeedLog:
    """Standardized mock for FeedLog model."""
    def __init__(self, **kwargs):
        self.id = kwargs.get('id', 1)
        self.feed_id = kwargs.get('feed_id', 1)
        self.http_status = kwargs.get('http_status', 200)
        self.is_success = kwargs.get('is_success', True)
        self.parse_error_message = kwargs.get('parse_error_message', None)
        self.started_at = kwargs.get('started_at', datetime.utcnow())
        self.finished_at = kwargs.get('finished_at', datetime.utcnow())
        self.parsed_by = kwargs.get('parsed_by', 'test@example.com')

class MockChannel:
    """Standardized mock for Channel model."""
    def __init__(self, **kwargs):
        self.id = kwargs.get('id', 1)
        self.title = kwargs.get('title', 'Test Channel')
        self.podcast_index_id = kwargs.get('podcast_index_id', 12345)
        self.feed_id = kwargs.get('feed_id', 1)

class MockItem:
    """Standardized mock for Item model."""
    def __init__(self, **kwargs):
        self.id = kwargs.get('id', 1)
        self.title = kwargs.get('title', 'Test Item')
        self.channel_id = kwargs.get('channel_id', 1)
        self.created_at = kwargs.get('created_at', datetime.utcnow())
        self.updated_at = kwargs.get('updated_at', datetime.utcnow())

class MockExportLog:
    """Standardized mock for ExportLog model."""
    def __init__(self, **kwargs):
        self.id = kwargs.get('id', 1)
        self.source = kwargs.get('source', 'feed')
        self.status = kwargs.get('status', 'completed')
        self.started_at = kwargs.get('started_at', datetime.utcnow())
        self.finished_at = kwargs.get('finished_at', datetime.utcnow())
        self.error_message = kwargs.get('error_message', None)

# ---- Standardized Fixtures ----
@pytest.fixture(scope='session')
def app():
    """Create a Flask app context for the tests."""
    # Debug: Print the configuration being used
    print(f"DEBUG: Creating app with config 'testing'")
    print(f"DEBUG: TEST_DATABASE_URL = {os.environ.get('TEST_DATABASE_URL', 'NOT SET')}")
    
    app = create_app('testing')
    
    # Debug: Print the app config
    print(f"DEBUG: App SQLALCHEMY_DATABASE_URI = {app.config.get('SQLALCHEMY_DATABASE_URI', 'NOT SET')}")
    
    # Create an application context
    with app.app_context():
        yield app

@pytest.fixture(scope='session')
def db(app):
    """Create a database for the tests."""
    _db.create_all()
    yield _db
    _db.drop_all()

@pytest.fixture(scope='function')
def session(db):
    """Create a new database session for a test."""
    connection = db.engine.connect()
    transaction = connection.begin()
    
    # Create a new session bound to the connection
    session = db.session
    
    yield session
    
    transaction.rollback()
    connection.close()
    session.remove()

@pytest.fixture(scope='function')
def test_client(app):
    """Create a test client for the Flask app."""
    with app.test_client() as client:
        yield client

@pytest.fixture
def mock_session():
    """Standardized mock for database session."""
    with patch("app.extensions.db.session") as mock:
        yield mock

@pytest.fixture
def mock_logger():
    """Standardized mock for logger."""
    with patch("app.utils.log_config.logger") as mock:
        yield mock

@pytest.fixture
def mock_log_database_operation():
    """Standardized mock for log_database_operation."""
    with patch("app.utils.audit_decorators.log_database_operation") as mock:
        yield mock

@pytest.fixture
def mock_log_error():
    """Standardized mock for log_error."""
    with patch("app.utils.error_handlers.log_error") as mock:
        yield mock 