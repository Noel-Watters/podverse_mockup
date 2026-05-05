# backend/tests/unit/app/utils/test_query_helpers.py

import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Query
from sqlalchemy import desc, asc

from app.utils.query_helpers import paginate_query, apply_sorting

# pagination
def test_paginate_query_basic():
    """Test basic pagination functionality."""
    # Mock query with proper chaining
    mock_query = MagicMock(spec=Query)
    mock_count_query = MagicMock()
    mock_count_query.count.return_value = 100
    mock_query.order_by.return_value = mock_count_query
    
    mock_offset_query = MagicMock()
    mock_limit_query = MagicMock()
    mock_limit_query.all.return_value = [
        {"id": 1, "title": "Item 1"},
        {"id": 2, "title": "Item 2"},
        {"id": 3, "title": "Item 3"}
    ]
    mock_query.offset.return_value = mock_offset_query
    mock_offset_query.limit.return_value = mock_limit_query
    
    items, metadata = paginate_query(mock_query, page=2, limit=10)
    
    # Verify results
    assert len(items) == 3
    assert items[0]["id"] == 1
    assert items[1]["id"] == 2
    assert items[2]["id"] == 3
    
    # Verify metadata
    assert metadata["page"] == 2
    assert metadata["limit"] == 10
    assert metadata["total_items"] == 100
    assert metadata["total_pages"] == 10
    assert metadata["has_next"] is True
    assert metadata["has_prev"] is True
    
    # Verify query calls
    mock_query.order_by.assert_called_once_with(None)
    mock_query.offset.assert_called_once_with(10)  # (page-1) * limit
    mock_offset_query.limit.assert_called_once_with(10)


def test_paginate_query_first_page():
    """Test pagination for first page."""
    mock_query = MagicMock(spec=Query)
    mock_query.order_by.return_value.count.return_value = 50
    mock_query.offset.return_value.limit.return_value.all.return_value = [
        {"id": 1, "title": "Item 1"}
    ]
    
    items, metadata = paginate_query(mock_query, page=1, limit=20)
    
    assert metadata["page"] == 1
    assert metadata["total_pages"] == 3  # ceil(50/20)
    assert metadata["has_next"] is True
    assert metadata["has_prev"] is False
    mock_query.offset.assert_called_once_with(0)


def test_paginate_query_last_page():
    """Test pagination for last page."""
    mock_query = MagicMock(spec=Query)
    mock_query.order_by.return_value.count.return_value = 50
    mock_query.offset.return_value.limit.return_value.all.return_value = [
        {"id": 50, "title": "Item 50"}
    ]
    
    items, metadata = paginate_query(mock_query, page=3, limit=20)
    
    assert metadata["page"] == 3
    assert metadata["total_pages"] == 3
    assert metadata["has_next"] is False
    assert metadata["has_prev"] is True
    mock_query.offset.assert_called_once_with(40)  # (3-1) * 20


def test_paginate_query_empty_results():
    """Test pagination with empty results."""
    mock_query = MagicMock(spec=Query)
    mock_query.order_by.return_value.count.return_value = 0
    mock_query.offset.return_value.limit.return_value.all.return_value = []
    
    items, metadata = paginate_query(mock_query, page=1, limit=20)
    
    assert items == []
    assert metadata["total_items"] == 0
    assert metadata["total_pages"] == 0
    assert metadata["has_next"] is False
    assert metadata["has_prev"] is False


def test_paginate_query_single_page():
    """Test pagination when all items fit in one page."""
    mock_query = MagicMock(spec=Query)
    mock_query.order_by.return_value.count.return_value = 5
    mock_query.offset.return_value.limit.return_value.all.return_value = [
        {"id": 1}, {"id": 2}, {"id": 3}, {"id": 4}, {"id": 5}
    ]
    
    items, metadata = paginate_query(mock_query, page=1, limit=10)
    
    assert metadata["total_pages"] == 1
    assert metadata["has_next"] is False
    assert metadata["has_prev"] is False

def test_paginate_query_edge_cases():
    """Test pagination with various edge cases."""
    test_cases = [
        # (total_items, page, limit, expected_total_pages, expected_has_next, expected_has_prev)
        (0, 1, 10, 0, False, False),      # No items
        (1, 1, 10, 1, False, False),      # One item, first page
        (10, 1, 10, 1, False, False),     # Exact fit
        (11, 1, 10, 2, True, False),      # One extra item
        (20, 2, 10, 2, False, True),      # Last page
        (25, 3, 10, 3, False, True),      # Last page with remainder
    ]
    
    for total_items, page, limit, expected_pages, expected_next, expected_prev in test_cases:
        mock_query = MagicMock(spec=Query)
        mock_query.order_by.return_value.count.return_value = total_items
        mock_query.offset.return_value.limit.return_value.all.return_value = []
        
        items, metadata = paginate_query(mock_query, page, limit)
        
        assert metadata["total_items"] == total_items
        assert metadata["total_pages"] == expected_pages
        assert metadata["has_next"] == expected_next
        assert metadata["has_prev"] == expected_prev


# sorting
def test_apply_sorting_ascending():
    """Test applying ascending sort to query."""
    mock_query = MagicMock(spec=Query)
    mock_model = MagicMock()
    mock_column = MagicMock()
    mock_model.title = mock_column
    mock_model.__name__ = "TestModel"
    
    # Mock the return value of order_by
    mock_ordered_query = MagicMock()
    mock_query.order_by.return_value = mock_ordered_query
    
    result = apply_sorting(mock_query, mock_model, "title", "asc")
    
    mock_query.order_by.assert_called_once_with(mock_column.asc())
    assert result == mock_ordered_query


def test_apply_sorting_descending():
    """Test applying descending sort to query."""
    mock_query = MagicMock(spec=Query)
    mock_model = MagicMock()
    mock_column = MagicMock()
    mock_model.created_at = mock_column
    mock_model.__name__ = "TestModel"
    
    # Mock the return value of order_by
    mock_ordered_query = MagicMock()
    mock_query.order_by.return_value = mock_ordered_query
    
    result = apply_sorting(mock_query, mock_model, "created_at", "desc")
    
    mock_query.order_by.assert_called_once_with(mock_column.desc())
    assert result == mock_ordered_query


def test_apply_sorting_invalid_field():
    """Test applying sort with invalid field name."""
    mock_query = MagicMock(spec=Query)
    mock_model = MagicMock()
    mock_model.invalid_field = None  # Field doesn't exist
    mock_model.__name__ = "TestModel"
    
    with pytest.raises(ValueError) as exc:
        apply_sorting(mock_query, mock_model, "invalid_field")
    
    assert "Invalid sort field: 'invalid_field' is not a column on model 'TestModel'" in str(exc.value)


def test_apply_sorting_with_getattr_none():
    """Test sorting when getattr returns None for the field."""
    mock_query = MagicMock(spec=Query)
    mock_model = MagicMock()
    mock_model.__name__ = "TestModel"
    
    # Mock getattr to return None for the field
    with patch('app.utils.query_helpers.getattr', return_value=None):
        with pytest.raises(ValueError) as exc:
            apply_sorting(mock_query, mock_model, "nonexistent_field")
        
        assert "Invalid sort field: 'nonexistent_field' is not a column on model 'TestModel'" in str(exc.value)