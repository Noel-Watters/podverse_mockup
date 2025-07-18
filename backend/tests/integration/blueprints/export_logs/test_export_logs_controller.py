# tests/integration/blueprints/export_logs/test_export_logs_controller.py

import pytest
from app.models.export_logs import ExportLog
from app.extensions import db

@pytest.fixture
def sample_log(app):
    log = ExportLog(
        export_type="rss",
        format="csv",
        status="completed",
        export_by="user123"
    )
    db.session.add(log)
    db.session.commit()
    yield log
    db.session.delete(log)
    db.session.commit()

def test_get_export_log_by_id(client, sample_log):
    res = client.get(f"/export_logs/{sample_log.id}")
    assert res.status_code == 200
    data = res.get_json()
    assert data["id"] == sample_log.id
    assert data["status"] == "completed"
