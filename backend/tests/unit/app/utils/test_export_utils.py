# backend/tests/unit/app/utils/test_export_utils.py

import pytest
import tempfile
import os
import json
from unittest.mock import patch, MagicMock
from flask import Response

from app.utils.export_utils import sanitize_user_id, generate_export_filename, write_export_data_to_file, generate_export_response_with_path
from app.utils.error_exceptions import ValidationError


def test_sanitize_user_id():
    """Test user ID sanitization for filename safety."""
    assert sanitize_user_id("user@example.com") == "user_example_com"
    assert sanitize_user_id("user.name@domain.co.uk") == "user_name_domain_co_uk"
    assert sanitize_user_id("simple_user") == "simple_user"
    assert sanitize_user_id("user.with.dots") == "user_with_dots"


def test_generate_export_filename():
    """Test export filename generation with various parameters."""
    with patch('app.utils.export_utils.datetime') as mock_datetime:
        mock_datetime.utcnow.return_value.strftime.return_value = "20231201_143022_123456"
        
        # Test with resource ID
        filename = generate_export_filename("feed", "user@test.com", 123)
        assert filename == "feed_123_export_20231201_143022_123456_user_test_com"
        
        # Test without resource ID
        filename = generate_export_filename("channel", "user@test.com")
        assert filename == "channel_export_20231201_143022_123456_user_test_com"


def test_write_export_data_to_file_csv():
    """Test writing CSV export data to file."""
    export_data = [
        {"id": 1, "title": "Test Item", "status": "active"},
        {"id": 2, "title": "Another Item", "status": "inactive"}
    ]
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
        temp_path = temp_file.name
    
    try:
        write_export_data_to_file(export_data, temp_path, "csv")
        
        with open(temp_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        # CSV uses QUOTE_ALL, so all fields are quoted
        assert '"id","title","status"' in content
        assert '"1","Test Item","active"' in content
        assert '"2","Another Item","inactive"' in content
        
    finally:
        os.unlink(temp_path)


def test_write_export_data_to_file_json():
    """Test writing JSON export data to file."""
    export_data = [
        {"id": 1, "title": "Test Item", "status": "active"},
        {"id": 2, "title": "Another Item", "status": "inactive"}
    ]
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
        temp_path = temp_file.name
    
    try:
        write_export_data_to_file(export_data, temp_path, "json")
        
        with open(temp_path, 'r') as f:
            content = json.load(f)
        
        assert content == export_data
        
    finally:
        os.unlink(temp_path)


def test_write_export_data_to_file_invalid_format():
    """Test writing export data with invalid format."""
    export_data = [{"id": 1}]
    
    with pytest.raises(ValidationError) as exc:
        write_export_data_to_file(export_data, "/tmp/test.txt", "xml")
    
    assert "Unsupported format: xml" in str(exc.value)


@patch('app.utils.export_utils.generate_export_response')
@patch('app.utils.export_utils.BaseConfig')
@patch('app.utils.export_utils.ensure_export_directory')
@patch('app.utils.export_utils.write_export_data_to_file')
def test_generate_export_response_with_path_local(
    mock_write, mock_ensure_dir, mock_config, mock_generate_response
):
    """Test export response generation with local storage."""
    mock_config.STORAGE_BACKEND = 'local'
    mock_ensure_dir.return_value = '/tmp/exports'
    mock_response = MagicMock(spec=Response)
    mock_generate_response.return_value = mock_response
    
    export_data = [{"id": 1, "title": "Test"}]
    filename = "test_export"
    
    response, file_path = generate_export_response_with_path(
        export_data, filename, "csv"
    )
    
    assert response == mock_response
    assert file_path == "/tmp/exports/test_export.csv"
    mock_write.assert_called_once_with(export_data, file_path, "csv")


@patch('app.utils.export_utils.generate_export_response')
@patch('app.utils.export_utils.BaseConfig')
@patch('app.utils.export_utils.upload_to_s3')
@patch('app.utils.export_utils.write_export_data_to_file')
@patch('app.utils.export_utils.os')
@patch('tempfile.NamedTemporaryFile')
def test_generate_export_response_with_path_s3(
    mock_temp_file, mock_os, mock_write, mock_upload, mock_config, mock_generate_response
):
    """Test export response generation with S3 storage."""
    mock_config.STORAGE_BACKEND = 's3'
    mock_config.S3_BUCKET_NAME = 'test-bucket'
    mock_response = MagicMock(spec=Response)
    mock_generate_response.return_value = mock_response
    
    # Mock temp file
    mock_temp = MagicMock()
    mock_temp.name = '/tmp/temp_file.csv'
    mock_temp_file.return_value.__enter__.return_value = mock_temp
    
    # Mock os operations
    mock_os.unlink.return_value = None
    mock_os.path.exists.return_value = True
    
    export_data = [{"id": 1, "title": "Test"}]
    filename = "test_export"
    mock_upload.return_value = "https://s3.amazonaws.com/test-bucket/exports/test_export.csv"
    
    response, file_path = generate_export_response_with_path(
        export_data, filename, "csv"
    )
    
    assert response == mock_response
    assert file_path == "https://s3.amazonaws.com/test-bucket/exports/test_export.csv"
    mock_write.assert_called_once_with(export_data, '/tmp/temp_file.csv', "csv")
    mock_upload.assert_called_once_with(
        '/tmp/temp_file.csv', 'test-bucket', 'exports/test_export.csv'
    )