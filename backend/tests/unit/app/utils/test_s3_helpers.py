# backend/tests/unit/app/utils/test_s3_helpers.py

import pytest
from unittest.mock import patch, MagicMock
from app.utils.s3_helpers import upload_to_s3, delete_from_s3
from botocore.exceptions import BotoCoreError

class TestS3Helpers:
    
    @patch("app.utils.s3_helpers.boto3.client")
    def test_upload_to_s3_success_aws(self, mock_boto_client):
        """Test successful S3 upload with AWS configuration."""
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3

        url = upload_to_s3("local.txt", "my-bucket", "path/in/s3.txt")

        mock_s3.upload_file.assert_called_once_with("local.txt", "my-bucket", "path/in/s3.txt")
        # The actual URL includes the region, so we check for the pattern
        assert "my-bucket.s3" in url
        assert "amazonaws.com/path/in/s3.txt" in url

    @patch("app.utils.s3_helpers.boto3.client")
    @patch("app.utils.s3_helpers.BaseConfig")
    def test_upload_to_s3_success_custom_endpoint(self, mock_config, mock_boto_client):
        """Test successful S3 upload with custom endpoint configuration."""
        mock_config.S3_ENDPOINT_URL = "https://custom-s3.example.com"
        mock_config.S3_REGION = "us-east-1"
        mock_config.S3_ACCESS_KEY_ID = "test-key"
        mock_config.S3_SECRET_ACCESS_KEY = "test-secret"
        
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3

        url = upload_to_s3("local.txt", "my-bucket", "path/in/s3.txt")

        mock_s3.upload_file.assert_called_once_with("local.txt", "my-bucket", "path/in/s3.txt")
        assert url == "https://custom-s3.example.com/my-bucket/path/in/s3.txt"

    @patch("app.utils.s3_helpers.boto3.client")
    def test_upload_to_s3_failure(self, mock_boto_client):
        """Test S3 upload failure handling."""
        mock_s3 = MagicMock()
        mock_s3.upload_file.side_effect = BotoCoreError()
        mock_boto_client.return_value = mock_s3

        with pytest.raises(RuntimeError) as exc:
            upload_to_s3("file.txt", "bucket", "key")

        assert "S3 upload failed" in str(exc.value)

    @patch("app.utils.s3_helpers.boto3.client")
    def test_delete_from_s3_success(self, mock_boto_client):
        """Test successful S3 deletion."""
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3

        result = delete_from_s3("my-bucket", "path/in/s3.txt")

        mock_s3.delete_object.assert_called_once_with(Bucket="my-bucket", Key="path/in/s3.txt")
        assert result is True

    @patch("app.utils.s3_helpers.boto3.client")
    def test_delete_from_s3_failure(self, mock_boto_client):
        """Test S3 deletion failure handling."""
        mock_s3 = MagicMock()
        mock_s3.delete_object.side_effect = BotoCoreError()
        mock_boto_client.return_value = mock_s3

        with pytest.raises(RuntimeError) as exc:
            delete_from_s3("bucket", "key")

        assert "S3 deletion failed" in str(exc.value)

    @patch("app.utils.s3_helpers.boto3.client")
    @patch("app.utils.s3_helpers.BaseConfig")
    def test_s3_client_configuration(self, mock_config, mock_boto_client):
        """Test S3 client configuration with different settings."""
        mock_config.S3_ACCESS_KEY_ID = "test-key"
        mock_config.S3_SECRET_ACCESS_KEY = "test-secret"
        mock_config.S3_REGION = "us-west-2"
        mock_config.S3_ENDPOINT_URL = None

        upload_to_s3("test.txt", "bucket", "key")

        # Verify boto3.client was called with correct config
        mock_boto_client.assert_called_once_with('s3', **{
            'aws_access_key_id': 'test-key',
            'aws_secret_access_key': 'test-secret',
            'region_name': 'us-west-2'
        })
