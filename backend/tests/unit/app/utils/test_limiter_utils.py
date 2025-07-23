# backend/tests/unit/app/utils/test_limiter_utils.py

import pytest
import os
from unittest.mock import patch, MagicMock
from app.utils.limiter_utils import get_limiter_storage


@patch('app.utils.limiter_utils.os')
def test_get_limiter_storage_with_redis_url(mock_os):
    """Test limiter storage configuration with Redis URL."""
    # Mock environment variable
    mock_os.getenv.return_value = "redis://localhost:6379/0"
    
    result = get_limiter_storage()
    
    assert result == "redis://localhost:6379/0"
    mock_os.getenv.assert_called_once_with('REDIS_URL')


@patch('app.utils.limiter_utils.os')
def test_get_limiter_storage_without_redis_url(mock_os):
    """Test limiter storage configuration without Redis URL."""
    # Mock environment variable not set
    mock_os.getenv.return_value = None
    
    result = get_limiter_storage()
    
    assert result == "memory://"
    mock_os.getenv.assert_called_once_with('REDIS_URL')


@patch('app.utils.limiter_utils.os')
def test_get_limiter_storage_with_empty_redis_url(mock_os):
    """Test limiter storage configuration with empty Redis URL."""
    # Mock environment variable set to empty string
    mock_os.getenv.return_value = ""
    
    result = get_limiter_storage()
    
    assert result == "memory://"
    mock_os.getenv.assert_called_once_with('REDIS_URL')


@patch('app.utils.limiter_utils.os')
def test_get_limiter_storage_with_whitespace_redis_url(mock_os):
    """Test limiter storage configuration with whitespace-only Redis URL."""
    # Mock environment variable set to whitespace
    mock_os.getenv.return_value = "   "
    
    result = get_limiter_storage()
    
    # The function returns the whitespace string as-is since it's truthy
    assert result == "   "
    mock_os.getenv.assert_called_once_with('REDIS_URL') 