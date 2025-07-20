# backend/app/utils/export_utils.py

import os
import csv
import tempfile
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from flask import Response, request
from app.utils.export_logging import create_export_log_simple, finalize_export_log
from app.utils.export_response import generate_export_response
from app.utils.file_system_helpers import ensure_export_directory, safe_write_file
from app.utils.s3_helpers import upload_to_s3
from app.utils.auth import get_current_auth0_id
from app.utils.error_exceptions import ValidationError, DatabaseError
from app.utils.request_logger import get_logger
from config import BaseConfig

logger = get_logger(__name__)

def sanitize_user_id(user_id: str) -> str:
    """Sanitize user ID for use in filenames."""
    return user_id.replace('@', '_').replace('.', '_')

def generate_export_filename(prefix: str, user_id: str, resource_id: Optional[int] = None) -> str:
    """Generate a unique filename with timestamp and user ID."""
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')
    sanitized_user_id = sanitize_user_id(user_id)
    
    if resource_id:
        return f"{prefix}_{resource_id}_export_{timestamp}_{sanitized_user_id}"
    return f"{prefix}_export_{timestamp}_{sanitized_user_id}"

def create_export_log_with_filters(export_type: str, filters: Dict[str, Any], export_by: str) -> Any:
    """Create export log with common parameters."""
    return create_export_log_simple(export_type=export_type, filters=filters, export_by=export_by)

def finalize_export_success(export_log_id: int, file_path: str, format: str, **kwargs) -> None:
    """Finalize export log with success status."""
    finalize_export_log(export_log_id, status="success", file_path=file_path, format=format, **kwargs)

def finalize_export_failure(export_log_id: int, error_message: str) -> None:
    """Finalize export log with failure status."""
    finalize_export_log(export_log_id, status="failed", error_message=error_message)

def write_export_data_to_file(export_data: List[Dict], file_path: str, format: str) -> None:
    """Write export data to file in the specified format."""
    if format == "csv":
        def write_csv_file(f):
            if export_data:
                # Write BOM for Excel compatibility
                f.write('\ufeff')
                writer = csv.DictWriter(f, fieldnames=export_data[0].keys(), quoting=csv.QUOTE_ALL)
                writer.writeheader()
                writer.writerows({k: row.get(k, "") for k in export_data[0].keys()} for row in export_data)
            else:
                # Write empty CSV
                f.write("")
        success, error = safe_write_file(file_path, write_csv_file)
    
    elif format == "json":
        import json
        def write_json_file(f):
            json.dump(export_data, f, indent=2, default=str)
        success, error = safe_write_file(file_path, write_json_file)
    
    else:
        raise ValidationError(f"Unsupported format: {format}")
    
    if not success:
        logger.error(f"Failed to write export file {file_path}: {error}")
        raise DatabaseError(f"Failed to write export file: {error}")

def generate_export_response_with_path(export_data: List[Dict], filename: str, format: str, headers: Optional[Dict] = None) -> Tuple[Response, str]:
    """Generate export response and store file (S3 or local), return both response and file path/URL."""
    # Generate the Flask response for immediate download
    response = generate_export_response(export_data, filename, headers)
    
    # Determine storage backend
    storage_backend = getattr(BaseConfig, 'STORAGE_BACKEND', 'local')
    
    if storage_backend == "s3":
        # Use S3 storage - write to temp file first, then upload
        with tempfile.NamedTemporaryFile(mode='w', suffix=f'.{format}', delete=False) as temp_file:
            temp_file_path = temp_file.name
        
        try:
            # Write data to temp file
            write_export_data_to_file(export_data, temp_file_path, format)
            
            # Upload to S3
            s3_key = f"exports/{filename}.{format}"
            s3_url = upload_to_s3(temp_file_path, BaseConfig.S3_BUCKET_NAME, s3_key)
            
            # Clean up temp file
            os.unlink(temp_file_path)
            
            logger.info(f"Successfully uploaded export file to S3: {s3_url}")
            return response, s3_url
            
        except Exception as e:
            # Clean up temp file on error
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
            logger.error(f"Failed to upload to S3: {str(e)}")
            raise DatabaseError(f"Failed to upload export file to S3: {str(e)}")
    
    else:
        # Use local storage (or temp directory if no volume mounted)
        try:
            # Try to use configured export directory
            export_dir = ensure_export_directory()
        except Exception:
            # Fallback to temp directory if export directory not accessible
            export_dir = tempfile.gettempdir()
            logger.warning(f"Using temp directory for exports: {export_dir}")
        
        file_extension = f".{format}" if format else ""
        absolute_file_path = os.path.abspath(os.path.join(export_dir, f"{filename}{file_extension}"))
        
        # Write file to disk
        write_export_data_to_file(export_data, absolute_file_path, format)
        
        logger.info(f"Successfully wrote export file to disk: {absolute_file_path}")
        return response, absolute_file_path

def get_export_format_and_user() -> Tuple[str, str]:
    """Get export format and user ID from request."""
    format = request.args.get("format", "csv")
    export_by = request.args.get("export_by") or get_current_auth0_id()
    return format, export_by

def validate_export_format(format: str) -> None:
    """Validate export format."""
    if format not in ["csv", "json"]:
        raise ValidationError("Invalid format. Use 'csv' or 'json'")

def create_export_headers_from_schema(schema_fields: List[str]) -> Dict[str, str]:
    """Create headers dictionary from schema fields."""
    return {field: field for field in schema_fields} 