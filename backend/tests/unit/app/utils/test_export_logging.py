# backend/tests/unit/app/utils/test_export_logging.py

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
from app.utils.export_logging import (
    create_export_log,
    finalize_export_log,
    create_export_log_simple
)

@patch("app.utils.export_logging.db.session")
def test_create_export_log(mock_session):
    mock_log = MagicMock()
    mock_session.add = MagicMock()
    mock_session.commit = MagicMock()

    with patch("app.utils.export_logging.ExportLog", return_value=mock_log):
        data = {"export_type": "feeds", "filters": {}, "status": "pending", "format": "csv"}
        result = create_export_log(data)

    mock_session.add.assert_called_once_with(mock_log)
    mock_session.commit.assert_called_once()
    assert result == mock_log

@patch("app.utils.export_logging.db.session")
def test_finalize_export_log_full_update(mock_session):
    mock_log = MagicMock()
    mock_session.get.return_value = mock_log

    result = finalize_export_log(
        log_id=1,
        status="success",
        file_path="/tmp/test.csv",
        format="csv",
        feeds_count=10,
        channels_count=5,
        items_count=50,
        error_message="none"
    )

    assert mock_log.status == "success"
    assert mock_log.file_path == "/tmp/test.csv"
    assert mock_log.format == "csv"
    assert mock_log.feeds_count == 10
    assert mock_log.channels_count == 5
    assert mock_log.items_count == 50
    assert mock_log.error_message == "none"
    assert isinstance(mock_log.completed_at, datetime)
    mock_session.commit.assert_called_once()
    assert result == mock_log

@patch("app.utils.export_logging.db.session")
def test_finalize_export_log_not_found(mock_session):
    mock_session.get.return_value = None
    result = finalize_export_log(log_id=99)
    assert result is None

@patch("app.utils.export_logging.create_export_log")
def test_create_export_log_simple_with_list(mock_create):
    mock_log = MagicMock()
    mock_create.return_value = mock_log

    result = create_export_log_simple(export_type=["feeds", "channels"], filters={"active": True})

    mock_create.assert_called_once()
    data_arg = mock_create.call_args[0][0]
    assert data_arg["export_type"] == "feeds,channels"
    assert data_arg["filters"] == {"active": True}
    assert data_arg["status"] == "pending"
    assert data_arg["format"] == "csv"
    assert result == mock_log
