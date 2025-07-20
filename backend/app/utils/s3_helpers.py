# backend/app/utils/s3_helpers.py

import boto3
import os
from botocore.exceptions import BotoCoreError
from config import BaseConfig

def upload_to_s3(local_path: str, bucket: str, s3_key: str) -> str:
    """
    Upload a file to S3 and return the public URL.
    
    Args:
        local_path: Path to the local file to upload
        bucket: S3 bucket name
        s3_key: S3 object key (file path in bucket)
        
    Returns:
        str: Public URL of the uploaded file
        
    Raises:
        RuntimeError: If S3 upload fails
    """
    # Configure S3 client with credentials and region
    s3_config = {}
    
    if BaseConfig.S3_ACCESS_KEY_ID and BaseConfig.S3_SECRET_ACCESS_KEY:
        s3_config['aws_access_key_id'] = BaseConfig.S3_ACCESS_KEY_ID
        s3_config['aws_secret_access_key'] = BaseConfig.S3_SECRET_ACCESS_KEY
    
    if BaseConfig.S3_REGION:
        s3_config['region_name'] = BaseConfig.S3_REGION
    
    if BaseConfig.S3_ENDPOINT_URL:
        s3_config['endpoint_url'] = BaseConfig.S3_ENDPOINT_URL
    
    s3 = boto3.client('s3', **s3_config)
    
    try:
        s3.upload_file(local_path, bucket, s3_key)
        
        # Generate the public URL
        if BaseConfig.S3_ENDPOINT_URL:
            # Custom S3-compatible service
            return f"{BaseConfig.S3_ENDPOINT_URL}/{bucket}/{s3_key}"
        else:
            # Standard AWS S3
            return f"https://{bucket}.s3.{BaseConfig.S3_REGION}.amazonaws.com/{s3_key}"
            
    except BotoCoreError as e:
        raise RuntimeError(f"S3 upload failed: {str(e)}")

def delete_from_s3(bucket: str, s3_key: str) -> bool:
    """
    Delete a file from S3.
    
    Args:
        bucket: S3 bucket name
        s3_key: S3 object key to delete
        
    Returns:
        bool: True if deletion was successful
        
    Raises:
        RuntimeError: If S3 deletion fails
    """
    # Configure S3 client with credentials and region
    s3_config = {}
    
    if BaseConfig.S3_ACCESS_KEY_ID and BaseConfig.S3_SECRET_ACCESS_KEY:
        s3_config['aws_access_key_id'] = BaseConfig.S3_ACCESS_KEY_ID
        s3_config['aws_secret_access_key'] = BaseConfig.S3_SECRET_ACCESS_KEY
    
    if BaseConfig.S3_REGION:
        s3_config['region_name'] = BaseConfig.S3_REGION
    
    if BaseConfig.S3_ENDPOINT_URL:
        s3_config['endpoint_url'] = BaseConfig.S3_ENDPOINT_URL
    
    s3 = boto3.client('s3', **s3_config)
    
    try:
        s3.delete_object(Bucket=bucket, Key=s3_key)
        return True
    except BotoCoreError as e:
        raise RuntimeError(f"S3 deletion failed: {str(e)}")
