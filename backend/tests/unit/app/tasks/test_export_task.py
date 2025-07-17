# backend/tests/unit/app/tasks/test_export_task.py

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from app.tasks.export_task import scheduled_export_task, cleanup_old_export_files

# --- scheduled_export_task tests ---

@patch("app.tasks.export_task.redis_lock")
@patch("app.tasks.export_task.export_data_to_csv")
@patch("app.tasks.export_task.create_export_log_simple")
@patch("app.tasks.export_task.finalize_export_log")
@patch("app.tasks.export_task.get_export_directory")
def test_scheduled_export_success(mock_get_export_dir, mock_finalize_log, mock_create_log, mock_export_csv, mock_redis_lock):
    mock_redis_lock.return_value.__enter__.return_value = (True, None)
    mock_export_csv.return_value = {"file_path": "/tmp/f.csv", "channels_count": 1}
    mock_get_export_dir.return_value = ("/tmp", False)
    mock_create_log.return_value = MagicMock(id=1)

    result = scheduled_export_task.apply().result

    assert result["status"] == "success"
    assert "file_path" in result["result"]

@patch("app.tasks.export_task.redis_lock")
def test_scheduled_export_lock_not_acquired(mock_redis_lock):
    mock_redis_lock.return_value.__enter__.return_value = (False, "lock busy")

    result = scheduled_export_task.apply().result

    assert result["status"] == "skipped"
    assert result["reason"] == "lock busy"

# --- cleanup_old_export_files tests ---

@patch("app.tasks.export_task.db.session")
def test_cleanup_old_export_files_local(mock_db_session):
    mock_log = MagicMock()
    mock_log.file_path = "/tmp/old_file.csv"
    mock_log.created_at = datetime.utcnow() - timedelta(days=31)
    mock_log.completed_at = None

    mock_db_session.query.return_value.filter.return_value.all.return_value = [mock_log]

    with patch("os.path.exists", return_value=True), patch("os.remove") as mock_remove:
        result = cleanup_old_export_files()
        mock_remove.assert_called_with("/tmp/old_file.csv")
        assert "Processed 1 old export files" in result
