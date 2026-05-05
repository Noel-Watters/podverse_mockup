import os
import tempfile
import pytest
from pathlib import Path
from app.utils.file_system_helpers import (
    check_directory_permissions,
    get_export_directory,
    safe_write_file,
    ensure_export_directory
)
from app.utils.error_exceptions import FSError

def test_check_directory_permissions_valid(tmp_path):
    is_writable, error = check_directory_permissions(str(tmp_path))
    assert is_writable is True
    assert error is None

def test_check_directory_permissions_nonexistent(tmp_path):
    new_dir = tmp_path / "new"
    is_writable, error = check_directory_permissions(str(new_dir))
    assert is_writable is True
    assert error is None
    assert new_dir.exists()

def test_check_directory_permissions_file(tmp_path):
    test_file = tmp_path / "test.txt"
    test_file.write_text("content")
    is_writable, error = check_directory_permissions(str(test_file))
    assert is_writable is False
    assert "not a directory" in error

def test_get_export_directory_primary_valid(tmp_path):
    result_dir, is_fallback = get_export_directory(str(tmp_path))
    assert result_dir == str(tmp_path)
    assert is_fallback is False

def test_get_export_directory_fallback(monkeypatch):
    monkeypatch.setattr("app.utils.file_system_helpers.check_directory_permissions", lambda d: (False, "fail"))
    with pytest.raises(FSError):
        get_export_directory("invalid_dir")

def test_safe_write_file(tmp_path):
    target_file = tmp_path / "output.txt"

    def write_func(f):
        f.write("Hello World")

    success, error = safe_write_file(str(target_file), write_func)
    assert success is True
    assert error is None
    assert target_file.read_text() == "Hello World"

def test_safe_write_file_failure(tmp_path):
    target_file = tmp_path / "fail.txt"

    def bad_write_func(f):
        raise RuntimeError("Write failed")

    success, error = safe_write_file(str(target_file), bad_write_func)
    assert success is False
    assert "Write failed" in error
    # No output file created
    assert not target_file.exists()

def test_ensure_export_directory_creates(monkeypatch, tmp_path):
    monkeypatch.setattr("app.utils.file_system_helpers.os.path.dirname", lambda _: str(tmp_path))
    exports_dir = os.path.join(tmp_path, "exports")
    if os.path.exists(exports_dir):
        os.rmdir(exports_dir)
    result = ensure_export_directory()
    assert os.path.exists(result)
    assert os.path.basename(result) == "exports"
