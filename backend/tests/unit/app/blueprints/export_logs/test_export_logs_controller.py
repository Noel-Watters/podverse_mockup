# tests/unit/app/blueprints/export_logs/test_export_logs_controller.py

import pytest
from unittest.mock import patch, MagicMock
from app.blueprints.export_logs.controller import get_export_log_controller
from app.models.export_logs import ExportLog
from app.utils.error_exceptions import NotFoundError

def test_get_export_log_success():
    dummy_log = ExportLog(id=1, export_type="rss", format="csv", status="completed")
    
    with patch("app.blueprints.export_logs.controller.db.session.get") as mock_get:
        mock_get.return_value = dummy_log
        result = get_export_log_controller(1)
        assert result["id"] == 1
        assert result["export_type"] == "rss"

def test_get_export_log_not_found():
    with patch("app.blueprints.export_logs.controller.db.session.get") as mock_get:
        mock_get.return_value = None
        with pytest.raises(NotFoundError):
            get_export_log_controller(999)