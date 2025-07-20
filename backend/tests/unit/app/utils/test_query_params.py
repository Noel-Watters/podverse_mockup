# backend/tests/unit/app/utils/test_query_params.py

import pytest
from unittest.mock import MagicMock
from app.utils.query_params import (
    get_pagination_params,
    get_sorting_params,
    get_filter_param,
    get_multi_filter_param,
    get_search_query
)
from app.utils.error_exceptions import ValidationError

# pagination params
def test_get_pagination_params_defaults():
    """Test pagination parameters with default values."""
    mock_request = MagicMock()
    mock_request.args.get.return_value = None
    
    page, limit = get_pagination_params(mock_request)
    
    assert page == 1
    assert limit == 20


def test_get_pagination_params_invalid_page_string():
    """Test pagination parameters with invalid page string."""
    mock_request = MagicMock()
    mock_request.args.get.side_effect = lambda key: {
        'page': 'invalid',
        'limit': '20'
    }.get(key)
    
    with pytest.raises(ValidationError) as exc:
        get_pagination_params(mock_request)
    
    assert "Page parameter must be a valid integer" in str(exc.value)
    
    
def test_get_pagination_params_limit_exceeds_max():
    """Test pagination parameters when limit exceeds maximum allowed."""
    mock_request = MagicMock()
    mock_request.args.get.side_effect = lambda key: {
        'page': '1',
        'limit': '150'
    }.get(key)
    
    page, limit = get_pagination_params(mock_request, max_limit=100)
    
    assert page == 1
    assert limit == 100 
    
    
# sorting params
def test_get_sorting_params_valid_values():
    """Test sorting parameters with valid user-provided values."""
    mock_request = MagicMock()
    mock_request.args.get.side_effect = lambda key, default=None, type=None: {
        'sort_by': 'title',
        'sort_order': 'desc'
    }.get(key, default)
    
    allowed_fields = ['id', 'title', 'created_at']
    sort_by, sort_order = get_sorting_params(mock_request, allowed_fields)
    
    assert sort_by == 'title'
    assert sort_order == 'desc'


def test_get_sorting_params_invalid_field():
    """Test sorting parameters with invalid field name."""
    mock_request = MagicMock()
    mock_request.args.get.side_effect = lambda key, default=None, type=None: {
        'sort_by': 'invalid_field',
        'sort_order': 'asc'
    }.get(key, default)
    
    allowed_fields = ['id', 'title', 'created_at']
    sort_by, sort_order = get_sorting_params(mock_request, allowed_fields)
    
    assert sort_by == 'id'  # Should fallback to default
    assert sort_order == 'asc'


# filter params
def test_get_filter_param_with_value():
    """Test getting a single filter parameter with a value."""
    mock_request = MagicMock()
    mock_request.args.get.return_value = 'active'
    
    result = get_filter_param(mock_request, 'status')
    
    assert result == 'active'
    mock_request.args.get.assert_called_once_with('status', None, type=str)


def test_get_multi_filter_param_with_values():
    """Test getting multi-value filter parameter with values."""
    mock_request = MagicMock()
    mock_request.args.get.return_value = '1,2,3'
    
    result = get_multi_filter_param(mock_request, 'tags')
    
    assert result == ['1', '2', '3']


def test_get_multi_filter_param_invalid_values():
    """Test getting multi-value filter parameter with invalid values."""
    mock_request = MagicMock()
    mock_request.args.get.return_value = '1,invalid,3'
    
    result = get_multi_filter_param(mock_request, 'category_ids', type_func=int)
    
    assert result == []  # Should return empty list on conversion error


# search query
def test_get_search_query_exceeds_max_length():
    """Test search query that exceeds maximum length."""
    mock_request = MagicMock()
    mock_request.args.get.return_value = 'a' * 101  # Exceeds default max of 100
    
    with pytest.raises(ValidationError) as exc:
        get_search_query(mock_request)
    
    assert "Search query exceeds maximum length of 100 characters" in str(exc.value)