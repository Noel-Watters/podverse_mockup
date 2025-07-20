# backend/app/services/data_export.py


# NOTE: This export currently uses local filesystem.
# If Podverse wants S3-compatible storage, update this section to upload file and log S3 URL.

import csv
import os
from datetime import datetime
from typing import List, Optional, Dict, Any
from app.utils.request_logger import get_logger
from app.blueprints.channel.services import get_channels_for_export
from app.blueprints.feed.services import get_feeds_for_export
from app.blueprints.channel.schemas import channel_exports_schema
from app.blueprints.feed.schemas import feeds_export_schema
from app.utils.file_system_helpers import safe_write_file, FSError, ensure_export_directory
from config import BaseConfig
from app.utils.zip_utils import zip_files
from app.utils.s3_helpers import upload_to_s3


logger = get_logger(__name__)

def export_data_to_csv(export_dir: Optional[str] = None, export_types: List[str] = ["channels", "feeds"]) -> Dict[str, Any]:
    """
    Export selected data types to CSV files and optionally bundle into a ZIP file.

    Args:
        export_dir: Optional directory for storing export files.
        export_types: List of strings indicating which datasets to export.

    Returns:
        Dict with metadata: file paths, record counts, timestamp, etc.

    Raises:
        FSError: For any file or upload-related failure.
    """
    try:
        if not export_types:
            raise FSError("No export types provided.")
            
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        export_dir = export_dir or ensure_export_directory()
        # Initialize result structure
        result = {
            "timestamp": timestamp,
            "file_path": None,
            "storage_type": BaseConfig.STORAGE_BACKEND,
            "export_directory": export_dir or ensure_export_directory()
        }
        
        file_paths = []  # Track all created files for ZIP
        
        # Export channels if requested
        if "channels" in export_types:
            channels = get_channels_for_export(sort_by='id', sort_order='asc')
            channels_data = channel_exports_schema.dump(channels)
            channels_file = f"channels_export_{timestamp}.csv"
            channels_path = os.path.join(result["export_directory"], channels_file)
            
            def write_channels(f):
                if channels_data:
                    writer = csv.DictWriter(f, fieldnames=channels_data[0].keys())
                    writer.writeheader()
                    writer.writerows(channels_data)
            
            success, error = safe_write_file(channels_path, write_channels)
            if not success:
                raise FSError(f"Failed to write channels file: {error}")
            
            result["channels_file"] = channels_file
            result["channels_count"] = len(channels_data)
            file_paths.append(channels_path)
            logger.info(f"Exported {len(channels_data)} channels")
        
        # Export feeds if requested
        if "feeds" in export_types:
            feeds = get_feeds_for_export(sort_by='id', sort_order='asc')
            feeds_data = feeds_export_schema.dump(feeds)
            feeds_file = f"feeds_export_{timestamp}.csv"
            feeds_path = os.path.join(result["export_directory"], feeds_file)
            
            def write_feeds(f):
                if feeds_data:
                    writer = csv.DictWriter(f, fieldnames=feeds_data[0].keys())
                    writer.writeheader()
                    writer.writerows(feeds_data)
            
            success, error = safe_write_file(feeds_path, write_feeds)
            if not success:
                raise FSError(f"Failed to write feeds file: {error}")
            
            result["feeds_file"] = feeds_file
            result["feeds_count"] = len(feeds_data)
            file_paths.append(feeds_path)
            logger.info(f"Exported {len(feeds_data)} feeds")
        
        # Create ZIP file if multiple files or single file
        if file_paths:
            zip_filename = f"export_{timestamp}.zip"
            zip_path = os.path.join(result["export_directory"], zip_filename)
            
            try:
                zip_files(file_paths, zip_path)
                logger.info(f"Created ZIP file: {zip_filename}")
            except Exception as e:
                raise FSError(f"Failed to create ZIP file: {str(e)}")
            
            # Save ZIP path into result for logging and download
            result["zip_file"] = zip_filename
            
            # Storage backend handling -upload or store ZIP
            if BaseConfig.STORAGE_BACKEND == "s3":
                try:
                    s3_key = f"exports/{zip_filename}"
                    zip_url = upload_to_s3(zip_path, BaseConfig.S3_BUCKET_NAME, s3_key)
                    result["file_path"] = zip_url
                    result["storage_type"] = "s3"
                except Exception as e:
                    raise FSError(f"S3 upload failed: {str(e)}")
            else:
                result["file_path"] = os.path.abspath(zip_path)
                result["storage_type"] = "local"
        
        # Log summary
        export_summary = []
        if "channels" in export_types:
            export_summary.append(f"{result.get('channels_count', 0)} channels")
        if "feeds" in export_types:
            export_summary.append(f"{result.get('feeds_count', 0)} feeds")
        
        logger.info(f"Export completed: {', '.join(export_summary)}")
        
        return result
        
    except Exception as e:
        logger.error(f"Export failed: {str(e)}")
        raise FSError(f"Export failed: {str(e)}")
