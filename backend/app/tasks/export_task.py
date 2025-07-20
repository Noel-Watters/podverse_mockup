# backend/app/tasks/export_task.py

import os
from celery import shared_task
from celery.app.task import Task
from typing import Dict, Any
from app.services.data_export import export_data_to_csv
from app.utils.file_system_helpers import get_export_directory, FSError
from app.utils.redis_lock import redis_lock, RedisLockError
from app.utils.request_logger import get_logger
from app.utils.security_logger import log_error
from datetime import datetime, timedelta
from app.extensions import db
from app.models.export_logs import ExportLog
from app.utils.export_logging import create_export_log_simple, finalize_export_log
from app.utils.s3_helpers import delete_from_s3
from config import BaseConfig


logger = get_logger(__name__)

@shared_task(bind=True, max_retries=3)
def scheduled_export_task(self: Task, export_types=["channels", "feeds"]) -> Dict[str, Any]:
    """
    Scheduled task to export data to CSV files.
    Uses Redis lock to prevent multiple exports running simultaneously.
    Includes fallback to temp directory if primary export location is unavailable.
    """
    log = None  # Initialize log variable
    try:
        # Try to acquire Redis lock
        with redis_lock("scheduled_export", timeout=1800) as (acquired, error): # 30 minutes timeout
            if not acquired: # check teh state of lock
                logger.warning(f"Export task skipped: {error or 'lock not acquired'}")
                return {
                    "status": "skipped",
                    "reason": error or "already_running"
                }
            
            try:
                logger.info("Starting scheduled data export")
                
                # Get export directory with fallback
                primary_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'exports') 
                try:
                    export_dir, is_fallback = get_export_directory(primary_dir)
                    if is_fallback:
                        logger.warning("Using fallback export directory")
                except FSError as e:
                    logger.error(f"Failed to get export directory: {str(e)}")
                    raise
                
                # Determine export_type for log
                if len(export_types) > 1:
                    export_type = "bulk"
                else:
                    export_type = ",".join(export_types)
                
                # Create export log
                log = create_export_log_simple(
                    export_type=export_type,
                    format="csv",
                    filters={}, # no filters for scheduled export
                    export_by="system@podverse.com"
                )
                
                # Perform export with directory override
                result = export_data_to_csv(export_dir=export_dir, export_types=export_types)
                
                # finalize export log
                finalize_export_log(
                    log.id, 
                    status="success", 
                    file_path=result.get("file_path"), 
                    channels_count=result.get("channels_count", 0),
                    feeds_count=result.get("feeds_count", 0),
                    items_count=result.get("items_count", 0)
                )
                
                logger.info(f"Export completed successfully: {result}")
                return {
                    "status": "success",
                    "result": result,
                    "using_fallback_directory": is_fallback
                }
                
            except FSError as e:
                logger.error(f"Filesystem error during export: {str(e)}")
                if self.request.retries < self.max_retries:
                    logger.info(f"Retrying export task (attempt {self.request.retries + 1})")
                    if log:
                        finalize_export_log(log.id, status="failed", error_message=str(e))
                    # retry the task
                    self.retry(exc=e, countdown=60 * (self.request.retries + 1))  # exponential backoff
                return {
                    "status": "error",
                    "error": str(e)
                }
                
            except Exception as e:
                logger.error(f"Export failed: {str(e)}")
                if self.request.retries < self.max_retries: # if the task has not been retried 3 times
                    logger.info(f"Retrying export task (attempt {self.request.retries + 1})")
                    if log:
                        finalize_export_log(log.id, status="failed", error_message=str(e))
                    
                    self.retry(exc=e, countdown=60 * (self.request.retries + 1))  # Exponential backoff
                return {
                    "status": "error",
                    "error": str(e)
                }
                
    except RedisLockError as e:
        logger.error(f"Redis lock error: {str(e)}")
        return {
            "status": "error",
            "error": f"Redis lock error: {str(e)}"
        }
    except Exception as e:
        logger.error(f"Unexpected error in export task: {str(e)}")
        return {
            "status": "error",
            "error": f"Unexpected error: {str(e)}"
        }

@shared_task
def cleanup_old_export_files() -> str:
    """
    Cleanup export files older than 30 days and update their records.
    Supports both local and S3 backends.
    """
     #! this can be increased 
    cutoff_date = datetime.utcnow() - timedelta(days=30) 
    old_logs = db.session.query(ExportLog).filter(ExportLog.created_at < cutoff_date, ExportLog.file_path.isnot(None)).all() # get logs with files older than 30 days

    for log in old_logs:
        try:
            if BaseConfig.STORAGE_BACKEND == "s3":
                if log.file_path and log.file_path.startswith("https://"):
                    # Extract key from S3 URL
                    if BaseConfig.S3_ENDPOINT_URL and BaseConfig.S3_ENDPOINT_URL in log.file_path:
                        # Custom S3-compatible service
                        s3_key = log.file_path.split(f"{BaseConfig.S3_ENDPOINT_URL}/{BaseConfig.S3_BUCKET_NAME}/")[-1]
                    else:
                        # Standard AWS S3
                        s3_key = log.file_path.split(f"{BaseConfig.S3_BUCKET_NAME}.s3.{BaseConfig.S3_REGION}.amazonaws.com/")[-1]
                    
                    delete_from_s3(BaseConfig.S3_BUCKET_NAME, s3_key)
            else:
                if log.file_path and os.path.exists(log.file_path):
                    os.remove(log.file_path)
        except Exception as e:
            log_error(f"Failed to delete export file: {log.file_path} | Error: {str(e)}", "system@podverse.com", e)
            continue

        # Update log metadata
        log.file_path = None
        log.status = "expired"
        if not log.completed_at:
            log.completed_at = datetime.utcnow()

    try:
        db.session.commit()
    except Exception as e:
        log_error(f"DB commit failed during export cleanup: {str(e)}")
        raise

    logger.info(f"Cleanup complete. Processed {len(old_logs)} old export files.")
    return f"Processed {len(old_logs)} old export files"