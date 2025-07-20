# tests/unit/services/test_data_export.py

import pytest
import os
import tempfile
from unittest.mock import patch, MagicMock
from datetime import datetime
from app.services.data_export import (
    ensure_export_directory,
    export_data_to_csv
)
from app.utils.error_exceptions import FSError


@pytest.fixture
def mock_export_data():
    return [{'id': 1, 'title': 'Sample'}]


@pytest.fixture
def temp_export_dir():
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@patch("app.services.data_export.get_channels_for_export")
@patch("app.services.data_export.get_feeds_for_export")
@patch("app.services.data_export.channel_exports_schema.dump")
@patch("app.services.data_export.feeds_export_schema.dump")
@patch("app.services.data_export.safe_write_file", return_value=(True, None))
@patch("app.services.data_export.zip_files")
@patch("app.services.data_export.upload_to_s3", return_value="https://s3.fake/url.zip")
def test_export_local_success(
    mock_s3, mock_zip, mock_write, mock_feeds_dump, 
    mock_channels_dump, mock_get_feeds, mock_get_channels, 
    mock_export_data, temp_export_dir
):
    mock_channels_dump.return_value = mock_export_data
    mock_feeds_dump.return_value = mock_export_data
    
    with patch("config.BaseConfig.STORAGE_BACKEND", new="local"):
        result = export_data_to_csv(
            export_dir=temp_export_dir,
            export_types=["channels", "feeds"]
        )
    
    assert result["channels_count"] == 1
    assert result["feeds_count"] == 1
    assert result["zip_file"].endswith(".zip")
    assert result["file_path"] is not None
    assert result["storage_type"] == "local"


def test_export_no_types():
    with pytest.raises(Exception):
        export_data_to_csv(export_types=[])


@patch("app.services.data_export.get_feeds_for_export")
@patch("app.services.data_export.feeds_export_schema.dump")
@patch("app.services.data_export.safe_write_file", return_value=(True, None))
@patch("app.services.data_export.zip_files")
def test_export_feeds_only(
    mock_zip, mock_write, mock_feeds_dump, 
    mock_get_feeds, mock_export_data, temp_export_dir
):
    mock_feeds_dump.return_value = mock_export_data
    
    with patch("config.BaseConfig.STORAGE_BACKEND", "local"):
        result = export_data_to_csv(
            export_dir=temp_export_dir,
            export_types=["feeds"]        )
    
    assert result["feeds_count"] == 1
    assert "channels_count" not in result
    assert result["zip_file"].endswith(".zip")
    assert result["storage_type"] == "local"


@patch("app.services.data_export.get_channels_for_export")
@patch("app.services.data_export.channel_exports_schema.dump")
@patch("app.services.data_export.safe_write_file", return_value=(True, None))
@patch("app.services.data_export.zip_files")
@patch("app.services.data_export.upload_to_s3")
def test_export_s3_upload_failure(
    mock_s3, mock_zip, mock_write, mock_channels_dump, 
    mock_get_channels, mock_export_data, temp_export_dir
):
    mock_channels_dump.return_value = mock_export_data
    mock_s3.side_effect = Exception("S3oad failed")
    
    with patch("config.BaseConfig.STORAGE_BACKEND", "s3"), \
         patch("config.BaseConfig.S3_BUCKET_NAME", "test-bucket"):
        with pytest.raises(FSError, match="S3 upload failed"):
            export_data_to_csv(
                export_dir=temp_export_dir,
                export_types=["channels"]
            )

@patch("app.services.data_export.get_channels_for_export")
@patch("app.services.data_export.channel_exports_schema.dump")
@patch("app.services.data_export.safe_write_file", return_value=(True, None))
@patch("app.services.data_export.zip_files")
def test_export_empty_data(
    mock_zip, mock_write, mock_channels_dump, 
    mock_get_channels, temp_export_dir
):
    mock_channels_dump.return_value = []
    
    with patch("config.BaseConfig.STORAGE_BACKEND", "local"):
        result = export_data_to_csv(
            export_dir=temp_export_dir,
            export_types=["channels"]        )
    
    assert result["channels_count"] == 0
    assert result["zip_file"].endswith(".zip")
    mock_zip.assert_called_once()


@patch("app.services.data_export.get_channels_for_export")
def test_export_general_exception(
    mock_get_channels, temp_export_dir
):
    mock_get_channels.side_effect = Exception("Database error")
    
    with patch("config.BaseConfig.STORAGE_BACKEND", "local"):
        with pytest.raises(FSError, match="Export failed"):
            export_data_to_csv(
                export_dir=temp_export_dir,
                export_types=["channels"]
            )


def test_ensure_export_directory_creates_directory():
    with patch('os.path.exists', return_value=False) as mock_exists, \
         patch('os.makedirs') as mock_makedirs, \
         patch('os.chmod') as mock_chmod, \
         patch('os.path.dirname', return_value='/test/path') as mock_dirname:
        
        result = ensure_export_directory()
        
        mock_exists.assert_called_once()
        mock_makedirs.assert_called_once()
        mock_chmod.assert_called_once_with('/test/path/exports', 0o755)
        assert result == '/test/path/exports'


def test_ensure_export_directory_exists():
    with patch('os.path.exists', return_value=True) as mock_exists, \
         patch('os.makedirs') as mock_makedirs, \
         patch('os.path.dirname', return_value='/test/path') as mock_dirname:
        
        result = ensure_export_directory()
        
        mock_exists.assert_called_once()
        mock_makedirs.assert_not_called()
        assert result == '/test/path/exports'