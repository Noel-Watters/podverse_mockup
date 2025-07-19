# tests/unit/app/blueprints/feed/test_export_controller.py

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from flask import Flask
from app.blueprints.feed.controllers.export import (
    export_single_feed_controller,
    bulk_export_feeds_controller
)
from app.models.feed import Feed, FeedFlagStatus
from app.models.channel import Channel
from app.utils.error_exceptions import NotFoundError, ValidationError, DatabaseError
from app.utils.redis_lock import RedisLockError
from app.extensions import db

# Import test configuration to override environment variables
import test_config

@pytest.fixture
def mock_request():
    """Mock Flask request object"""
    request = Mock()
    request.args = {}
    return request

@pytest.fixture
def sample_feed_data(app):
    """Create sample feed data for testing"""
    with app.app_context():
        from app.extensions import db
        
        # Create flag status
        flag_status = FeedFlagStatus(status="active")
        db.session.add(flag_status)
        db.session.commit()
        
        # Create channel
        channel = Channel(
            title="Test Podcast",
            podcast_index_id=12345,
            feed_id=1
        )
        db.session.add(channel)
        db.session.commit()
        
        # Create feed
        feed = Feed(
            id=1,
            url="https://example.com/feed.xml",
            parsing_priority=1,
            is_parsing=False,
            flag_status_id=flag_status.id
        )
        db.session.add(feed)
        db.session.commit()
        
        yield feed
        
        # Cleanup
        db.session.delete(feed)
        db.session.delete(channel)
        db.session.delete(flag_status)
        db.session.commit()

@pytest.fixture
def mock_auth():
    """Mock authentication"""
    with patch('app.blueprints.feed.controllers.export.get_current_auth0_id') as mock:
        mock.return_value = "test_user@example.com"
        yield mock

@pytest.fixture
def mock_redis_lock():
    """Mock Redis lock"""
    with patch('app.blueprints.feed.controllers.export.redis_lock') as mock:
        mock.return_value.__enter__.return_value = (True, None)
        yield mock

@pytest.fixture
def mock_export_logging():
    """Mock export logging functions"""
    with patch('app.blueprints.feed.controllers.export.create_export_log_simple') as mock_create, \
         patch('app.blueprints.feed.controllers.export.finalize_export_log') as mock_finalize:
        mock_create.return_value = Mock(id=1)
        yield mock_create, mock_finalize

@pytest.fixture
def mock_export_response():
    """Mock export response generation"""
    with patch('app.blueprints.feed.controllers.export._generate_export_response_with_path') as mock:
        mock.return_value = (Mock(status_code=200), "/tmp/test.csv")
        yield mock

@pytest.fixture
def mock_query_params():
    """Mock query parameter functions"""
    with patch('app.blueprints.feed.controllers.export.get_sorting_params') as mock_sort, \
         patch('app.blueprints.feed.controllers.export.get_search_query') as mock_search:
        mock_sort.return_value = ('id', 'asc')
        mock_search.return_value = None
        yield mock_sort, mock_search

@pytest.fixture
def mock_flask_request():
    """Mock Flask request object"""
    mock_request = Mock()
    mock_request.args = Mock()
    mock_request.args.get = Mock(return_value="csv")
    return mock_request

def test_export_single_feed_controller_success(
    app, mock_request, sample_feed_data, mock_auth, mock_redis_lock, 
    mock_export_logging, mock_export_response, mock_flask_request
):
    """Test successful single feed export"""
    mock_create, mock_finalize = mock_export_logging
    
    # Mock the request.args.get call
    with app.app_context(): # bu onemli 
        with patch('app.blueprints.feed.controllers.export.request', mock_flask_request):
            response = export_single_feed_controller(sample_feed_data.id)
            
            assert response.status_code == 200
            mock_create.assert_called_once()
            mock_finalize.assert_called_once_with(1, "success", "/tmp/test.csv", "csv")

def test_export_single_feed_controller_feed_not_found(
    app, mock_request, mock_auth, mock_redis_lock, mock_export_logging, mock_flask_request
):
    """Test single feed export with non-existent feed"""
    with app.app_context():
        with patch('app.blueprints.feed.controllers.export.request', mock_flask_request):
            with pytest.raises(NotFoundError, match="Feed not found"):
                export_single_feed_controller(99999)

def test_export_single_feed_controller_redis_lock_failed(
    app, mock_request, sample_feed_data, mock_auth, mock_export_logging, mock_flask_request
):
    """Test single feed export when Redis lock fails"""
    with app.app_context():
        with patch('app.blueprints.feed.controllers.export.redis_lock') as mock_lock, \
             patch('app.blueprints.feed.controllers.export.request', mock_flask_request):
            mock_lock.return_value.__enter__.return_value = (False, "Lock failed")
            
            with pytest.raises(ValidationError, match="Feed is already being exported"):
                export_single_feed_controller(sample_feed_data.id)

def test_export_single_feed_controller_redis_error(
    app, mock_request, sample_feed_data, mock_auth, mock_export_logging, mock_flask_request
):
    """Test single feed export when Redis lock raises error"""
    with app.app_context():
        with patch('app.blueprints.feed.controllers.export.redis_lock') as mock_lock, \
             patch('app.blueprints.feed.controllers.export.request', mock_flask_request):
            mock_lock.side_effect = RedisLockError("Redis error")
            
            with pytest.raises(RedisLockError):
                export_single_feed_controller(sample_feed_data.id)

def test_export_single_feed_controller_with_format(
    app, mock_request, sample_feed_data, mock_auth, mock_redis_lock, 
    mock_export_logging, mock_export_response, mock_flask_request
):
    """Test single feed export with specific format"""
    mock_create, mock_finalize = mock_export_logging
    mock_flask_request.args.get.return_value = "json"
    
    with app.app_context():
        with patch('app.blueprints.feed.controllers.export.request', mock_flask_request):
            response = export_single_feed_controller(sample_feed_data.id)
            
            assert response.status_code == 200
            mock_finalize.assert_called_once_with(1, "success", "/tmp/test.csv", "json")

def test_bulk_export_feeds_controller_success(
    app, mock_request, sample_feed_data, mock_auth, mock_redis_lock, 
    mock_export_logging, mock_export_response, mock_query_params, mock_flask_request
):
    """Test successful bulk feeds export"""
    mock_create, mock_finalize = mock_export_logging
    
    def mock_get(key, default=None, type=None):
        return {
            'format': 'csv',
            'export_by': None,
            'id': None,
            'podcast_index_id': None
        }.get(key, default)
    
    mock_flask_request.args.get.side_effect = mock_get
    
    with app.app_context():
        with patch('app.blueprints.feed.controllers.export.request', mock_flask_request):
            response = bulk_export_feeds_controller()
            
            assert response.status_code == 200
            mock_create.assert_called_once()
            mock_finalize.assert_called_once_with(1, "success", "/tmp/test.csv", "csv", feeds_count=1)

def test_bulk_export_feeds_controller_with_filters(
    app, mock_request, sample_feed_data, mock_auth, mock_redis_lock, 
    mock_export_logging, mock_export_response, mock_query_params, mock_flask_request
):
    """Test bulk feeds export with filters"""
    mock_create, mock_finalize = mock_export_logging
    
    def mock_get(key, default=None, type=None):
        return {
            'format': 'json',
            'export_by': 'custom_user@example.com',
            'id': '1',
            'podcast_index_id': '12345'
        }.get(key, default)
    
    mock_flask_request.args.get.side_effect = mock_get
    
    with app.app_context():
        with patch('app.blueprints.feed.controllers.export.request', mock_flask_request):
            response = bulk_export_feeds_controller()
            
            assert response.status_code == 200
            # Check that filters were passed to create_export_log_simple
            call_args = mock_create.call_args[1]
            assert call_args['filters']['format'] == 'json'
            assert call_args['filters']['export_by'] == 'custom_user@example.com'
            assert call_args['filters']['feed_id'] == 1
            assert call_args['filters']['podcast_index_id'] == 12345

def test_bulk_export_feeds_controller_invalid_format(
    app, mock_request, mock_auth, mock_redis_lock, mock_export_logging, mock_query_params, mock_flask_request
):
    """Test bulk feeds export with invalid format"""
    def mock_get(key, default=None, type=None):
        return {
            'format': 'pdf'
        }.get(key, default)
    
    mock_flask_request.args.get.side_effect = mock_get
    
    with app.app_context():
        with patch('app.blueprints.feed.controllers.export.request', mock_flask_request):
            with pytest.raises(ValidationError, match="Invalid format"):
                bulk_export_feeds_controller()

def test_bulk_export_feeds_controller_redis_lock_failed(
    app, mock_request, sample_feed_data, mock_auth, mock_export_logging, mock_query_params, mock_flask_request
):
    """Test bulk feeds export when Redis lock fails"""
    def mock_get(key, default=None, type=None):
        return {
            'format': 'csv',
            'export_by': None
        }.get(key, default)
    
    mock_flask_request.args.get.side_effect = mock_get
    
    with app.app_context():
        with patch('app.blueprints.feed.controllers.export.redis_lock') as mock_lock, \
             patch('app.blueprints.feed.controllers.export.request', mock_flask_request):
            mock_lock.return_value.__enter__.return_value = (False, "Lock failed")
            
            with pytest.raises(ValidationError, match="Bulk export is already in progress"):
                bulk_export_feeds_controller()

def test_bulk_export_feeds_controller_redis_error(
    app, mock_request, sample_feed_data, mock_auth, mock_export_logging, mock_query_params, mock_flask_request
):
    """Test bulk feeds export when Redis lock raises error"""
    def mock_get(key, default=None, type=None):
        return {
            'format': 'csv',
            'export_by': None
        }.get(key, default)
    
    mock_flask_request.args.get.side_effect = mock_get
    
    with app.app_context():
        with patch('app.blueprints.feed.controllers.export.redis_lock') as mock_lock, \
             patch('app.blueprints.feed.controllers.export.request', mock_flask_request):
            mock_lock.side_effect = RedisLockError("Redis error")
            
            with pytest.raises(RedisLockError):
                bulk_export_feeds_controller()

def test_bulk_export_feeds_controller_with_sorting(
    app, mock_request, sample_feed_data, mock_auth, mock_redis_lock, 
    mock_export_logging, mock_export_response, mock_query_params, mock_flask_request
):
    """Test bulk feeds export with sorting parameters"""
    mock_create, mock_finalize = mock_export_logging
    
    def mock_get(key, default=None, type=None):
        return {
            'format': 'csv',
            'export_by': None,
            'sort_by': 'url',
            'sort_order': 'desc'
        }.get(key, default)
    
    mock_flask_request.args.get.side_effect = mock_get
    
    with app.app_context():
        with patch('app.blueprints.feed.controllers.export.request', mock_flask_request):
            response = bulk_export_feeds_controller()
            
            assert response.status_code == 200
            mock_create.assert_called_once()

def test_bulk_export_feeds_controller_with_search(
    app, mock_request, sample_feed_data, mock_auth, mock_redis_lock, 
    mock_export_logging, mock_export_response, mock_query_params, mock_flask_request
):
    """Test bulk feeds export with search parameter"""
    mock_create, mock_finalize = mock_export_logging
    
    def mock_get(key, default=None, type=None):
        return {
            'format': 'csv',
            'export_by': None,
            'search': 'test'
        }.get(key, default)
    
    mock_flask_request.args.get.side_effect = mock_get
    
    with app.app_context():
        with patch('app.blueprints.feed.controllers.export.request', mock_flask_request):
            response = bulk_export_feeds_controller()
            
            assert response.status_code == 200
            mock_create.assert_called_once()

def test_bulk_export_feeds_controller_error_handling(
    app, mock_request, sample_feed_data, mock_auth, mock_redis_lock, 
    mock_export_logging, mock_query_params, mock_flask_request
):
    """Test bulk feeds export error handling"""
    mock_create, mock_finalize = mock_export_logging
    
    def mock_get(key, default=None, type=None):
        return {
            'format': 'csv',
            'export_by': None
        }.get(key, default)
    
    mock_flask_request.args.get.side_effect = mock_get
    
    with app.app_context():
        with patch('app.blueprints.feed.controllers.export.request', mock_flask_request), \
             patch('app.blueprints.feed.controllers.export.get_feeds_for_export') as mock_get_feeds:
            mock_get_feeds.side_effect = Exception("Database error")
            
            with pytest.raises(DatabaseError, match="Failed to export feeds"):
                bulk_export_feeds_controller()
            
            # Should finalize with failure
            mock_finalize.assert_called_once_with(1, "failed", error_message="Database error")

def test_export_single_feed_controller_error_handling(
    app, mock_request, sample_feed_data, mock_auth, mock_redis_lock, 
    mock_export_logging, mock_flask_request
):
    """Test single feed export error handling"""
    mock_create, mock_finalize = mock_export_logging
    
    with app.app_context():
        with patch('app.blueprints.feed.controllers.export.request', mock_flask_request), \
             patch('app.blueprints.feed.controllers.export.get_feed_by_id') as mock_get_feed:
            mock_get_feed.side_effect = Exception("Database error")
            
            with pytest.raises(DatabaseError, match="Failed to export single feed"):
                export_single_feed_controller(sample_feed_data.id)
            
            # Should finalize with failure
            mock_finalize.assert_called_once_with(1, "failed", error_message="Database error") 