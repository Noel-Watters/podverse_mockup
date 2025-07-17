# backend/app/utils/s3_helpers.py

import boto3
import os
from botocore.exceptions import BotoCoreError

def upload_to_s3(local_path: str, bucket: str, s3_key: str) -> str:
    s3 = boto3.client('s3')
    try:
        s3.upload_file(local_path, bucket, s3_key)
        return f"https://{bucket}.s3.amazonaws.com/{s3_key}"
    except BotoCoreError as e:
        raise RuntimeError(f"S3 upload failed: {str(e)}")
