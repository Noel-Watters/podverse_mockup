# backend/tests/unit/app/utils/test_s3_helpers.py

import pytest
from unittest.mock import patch, MagicMock
from app.utils.s3_helpers import upload_to_s3
from botocore.exceptions import BotoCoreError

@patch("app.utils.s3_helpers.boto3.client")
def test_upload_to_s3_success(mock_boto_client):
    mock_s3 = MagicMock()
    mock_boto_client.return_value = mock_s3

    url = upload_to_s3("local.txt", "my-bucket", "path/in/s3.txt")

    mock_s3.upload_file.assert_called_once_with("local.txt", "my-bucket", "path/in/s3.txt")
    assert url == "https://my-bucket.s3.amazonaws.com/path/in/s3.txt"

@patch("app.utils.s3_helpers.boto3.client")
def test_upload_to_s3_failure(mock_boto_client):
    mock_s3 = MagicMock()
    mock_s3.upload_file.side_effect = BotoCoreError()
    mock_boto_client.return_value = mock_s3

    with pytest.raises(RuntimeError) as exc:
        upload_to_s3("file.txt", "bucket", "key")

    assert "S3 upload failed" in str(exc.value)
