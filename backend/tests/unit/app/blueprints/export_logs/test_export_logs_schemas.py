# backend/tests/unit/app/blueprints/export_logs/test_export_logs_schemas.py

import pytest
from datetime import datetime, timedelta
from app.blueprints.export_logs.schemas import ExportLogSchema, export_log_schema
from app.models.export_logs import ExportLog
from marshmallow import ValidationError
from unittest.mock import patch


def test_valid_export_log_serialization():
    """Test serializing a valid export log"""
    log = ExportLog(
        id=1,
        export_by="test@example.com",
        export_type="feeds",
        format="csv",
        status="success",
        file_path="/tmp/test.csv",
        channels_count=10,
        feeds_count=50,
        items_count=200,
        created_at=datetime.utcnow() - timedelta(minutes=30),
        completed_at=datetime.utcnow() - timedelta(minutes=25),
        error_message=None,
        filters={"date_from": "2023-01-01", "status": "active"}
    )
    result = export_log_schema.dump(log)
    
    assert result['id'] == 1
    assert result['export_by'] == "test@example.com"
    assert result['export_type'] == "feeds"
    assert result['format'] == "csv"
    assert result['status'] == "success"
    assert result['file_path'] == "/tmp/test.csv"
    assert result['channels_count'] == 10
    assert result['feeds_count'] == 50
    assert result['items_count'] == 200
    assert result['error_message'] is None
    assert result['filters'] == {"date_from": "2023-01-01", "status": "active"}
    assert 'duration' in result
    assert 'is_expired' in result
    assert 'has_file' in result


def test_export_log_with_null_values():
    """Test serializing an export log with null values"""
    log = ExportLog(
        id=1,
        export_by="test@example.com",
        export_type="channels",
        format="json",
        status="pending",
        file_path=None,
        channels_count=None,
        feeds_count=None,
        items_count=None,
        created_at=datetime.utcnow(),
        completed_at=None,
        error_message=None,
        filters=None
    )
    result = export_log_schema.dump(log)
    
    assert result['file_path'] is None
    assert result['channels_count'] is None
    assert result['feeds_count'] is None
    assert result['items_count'] is None
    assert result['completed_at'] is None
    assert result['error_message'] is None
    assert result['filters'] is None
    assert result['duration'] is None
    assert result['is_expired'] is False
    assert result['has_file'] is False
    
    
def test_export_log_with_error_message():
    """Test serializing an export log with error message"""
    log = ExportLog(
        id=1,
        export_by="test@example.com",
        export_type="items",
        format="csv",
        status="failed",
        file_path=None,
        channels_count=None,
        feeds_count=None,
        items_count=None,
        created_at=datetime.utcnow(),
        completed_at=datetime.utcnow(),
        error_message="Database connection failed",
        filters=None
    )
    result = export_log_schema.dump(log)
    
    assert result['status'] == "failed"
    assert result['error_message'] == "Database connection failed"
    assert result['duration'] is not None


def test_duration_calculation():
    """Test duration calculation"""
    created_at = datetime.utcnow() - timedelta(minutes=30)
    completed_at = datetime.utcnow() - timedelta(minutes=25)
    
    log = ExportLog(
        id=1,
        export_by="test@example.com",
        export_type="feeds",
        format="csv",
        status="success",
        file_path="/tmp/test.csv",
        created_at=created_at,
        completed_at=completed_at
    )
    result = export_log_schema.dump(log)
    
    # Duration should be approximately 5 minutes (300 seconds)
    assert result['duration'] is not None
    assert 290 <= result['duration'] <= 310  # Allow small time difference


def test_is_expired_calculation():
    """Test is_expired calculation"""
    # Create a log that's older than 30 days
    old_created_at = datetime.utcnow() - timedelta(days=31)
    
    log = ExportLog(
        id=1,
        export_by="test@example.com",
        export_type="feeds",
        format="csv",
        status="success",
        file_path="/tmp/test.csv",
        created_at=old_created_at,
        completed_at=old_created_at + timedelta(minutes=5)
    )
    result = export_log_schema.dump(log)
    
    assert result['is_expired'] is True
    

@patch('os.path.exists')
def test_has_file_calculation_file_not_exists(mock_exists):
    """Test has_file calculation when file doesn't exist"""
    mock_exists.return_value = False
    
    log = ExportLog(
        id=1,
        export_by="test@example.com",
        export_type="feeds",
        format="csv",
        status="success",
        file_path="/tmp/test.csv",
        created_at=datetime.utcnow(),
        completed_at=datetime.utcnow()
    )
    
    result = export_log_schema.dump(log)
    
    assert result['has_file'] is False
    mock_exists.assert_called_once_with("/tmp/test.csv")


    
    result = export_log_schema.dump(log)
    
    assert result['has_file'] is False


def test_validation_export_type_invalid():
    """Test validation of invalid export_type"""
    schema = ExportLogSchema()
    
    with pytest.raises(ValidationError, match="Must be one of"):
        schema.load({
            'export_by': 'test@example.com',
            'export_type': 'invalid_type',
            'format': 'csv',
            'status': 'pending'
        })


def test_validation_format_invalid():
    """Test validation of invalid format"""
    schema = ExportLogSchema()
    
    with pytest.raises(ValidationError, match="Must be one of"):
        schema.load({
            'export_by': 'test@example.com',
            'export_type': 'feeds',
            'format': 'invalid_format',
            'status': 'pending'
        })


def test_validation_status_invalid():
    """Test validation of invalid status"""
    schema = ExportLogSchema()
    
    with pytest.raises(ValidationError, match="Must be one of"):
        schema.load({
            'export_by': 'test@example.com',
            'export_type': 'feeds',
            'format': 'csv',
            'status': 'invalid_status'
        })


def test_validation_missing_required_fields():
    """Test validation with missing required fields"""
    schema = ExportLogSchema()
    
    with pytest.raises(ValidationError):
        schema.load({
            'export_by': 'test@example.com'
            # Missing export_type, format, status
        })


def test_validation_valid_data():
    """Test validation with valid data"""
    schema = ExportLogSchema()
    
    data = {
        'export_by': 'test@example.com',
        'export_type': 'feeds',
        'format': 'csv',
        'status': 'pending',
        'filters': {'date_from': '2023-01-01'},
        'channels_count': 10,
        'feeds_count': 50,
        'items_count': 200
    }
    
    result = schema.load(data)
    
    assert result.export_by == 'test@example.com'
    assert result.export_type == 'feeds'
    assert result.format == 'csv'
    assert result.status == 'pending'
    assert result.filters == {'date_from': '2023-01-01'}
    assert result.channels_count == 10
    assert result.feeds_count == 50
    assert result.items_count == 200