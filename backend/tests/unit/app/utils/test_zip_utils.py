# backend/tests/unit/app/utils/test_zip_utils.py

import os
import zipfile
from pathlib import Path
from app.utils.zip_utils import zip_files

def test_zip_files(tmp_path):
    # Create sample files
    file1 = tmp_path / "file1.txt"
    file2 = tmp_path / "file2.txt"
    file1.write_text("Hello")
    file2.write_text("World")

    zip_path = tmp_path / "archive.zip"

    # Run function
    zip_files([str(file1), str(file2)], str(zip_path))

    # Check ZIP file created
    assert zip_path.exists()
    with zipfile.ZipFile(zip_path, 'r') as zipf:
        names = zipf.namelist()
        assert "file1.txt" in names
        assert "file2.txt" in names
        assert zipf.read("file1.txt").decode() == "Hello"
        assert zipf.read("file2.txt").decode() == "World"
