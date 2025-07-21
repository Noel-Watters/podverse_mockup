from app.extensions import db
from app.models.export_logs import ExportLog
from app.utils.error_exceptions import NotFoundError, ValidationError
from app.utils.request_logger import get_logger
from app.utils.query_helpers import paginate_query, apply_sorting
from app.blueprints.export_logs.schemas import export_log_schema
from sqlalchemy import and_, or_, func
import os
from flask import redirect

logger = get_logger(__name__)

def get_export_logs_controller(page, limit, sort_by, sort_order, filters):
    """Get paginated list of export logs. Supports filtering, pagination, status checks."""
    try:     
        query = db.session.query(ExportLog)
        
        #apply filters to the query
        if filters.get('status'):
            query = query.filter(ExportLog.status == filters["status"])
        if filters.get('source'):
            query = query.filter(ExportLog.source == filters["source"])
        if filters.get('export_by'):
            query = query.filter(ExportLog.export_by == filters["export_by"])
        if filters.get('id'):
            query = query.filter(ExportLog.id == filters["id"])
        if filters.get('format'):
            query = query.filter(ExportLog.format == filters["format"])
        if filters.get('has_error'):
            if filters["has_error"].lower() == 'true':
                query = query.filter(ExportLog.status == 'failed')
            elif filters["has_error"].lower() == 'false':
                query = query.filter(ExportLog.status != 'failed')
        # Use duration_expr for min_duration and max_duration
        if filters.get('min_duration') or filters.get('max_duration'):
            duration_expr = func.extract('epoch', ExportLog.completed_at - ExportLog.created_at)
            if filters.get('min_duration'):
                query = query.filter(duration_expr >= filters["min_duration"])
            if filters.get('max_duration'):
                query = query.filter(duration_expr <= filters["max_duration"])
        # Date range
        if filters.get('start_date') and filters.get('end_date'):
            query = query.filter(
                and_(
                    ExportLog.created_at >= filters["start_date"],
                    ExportLog.created_at <= filters["end_date"]
                )
            )
        # search_term is the search term for the error message
        if filters.get('search_term'):
            search_filter = or_(
                ExportLog.error_message.ilike(f'%{filters["search_term"]}%')
            )
            query = query.filter(search_filter)
        #sort by duration if specified
        if sort_by == 'duration':
            duration_expr = func.extract('epoch', ExportLog.completed_at - ExportLog.created_at)
            query = query.order_by(duration_expr.asc() if sort_order == "asc" else duration_expr.desc())
        else:
            query = apply_sorting(query, ExportLog, sort_by, sort_order)
        #paginate the query
        logs, pagination_metadata = paginate_query(query, page, limit)
        #return the logs and pagination metadata
        return [export_log_schema.dump(log) for log in logs], pagination_metadata
    except Exception as e:
        logger.error(f"Error retrieving export logs: {str(e)}")
        raise ValidationError(f"Failed to retrieve export logs: {str(e)}")

def get_export_log_controller(log_id):
    """Get a single export log by ID."""
    try:
        log = db.session.get(ExportLog, log_id)
        if not log:
            raise NotFoundError("Export log not found")
        return export_log_schema.dump(log)
    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error retrieving export log {log_id}: {str(e)}")
        raise ValidationError(f"Failed to retrieve export log: {str(e)}")

def download_export_file_controller(log_id: int) -> dict:
    """
        Download an export file by log ID. Handles both local files and S3 URLs.
        
        Returns a dict with keys:
        - type: "redirect" or "file"
        - url (if redirect)
        - file_path, filename, format (if file)
    """
    try:
        log = db.session.get(ExportLog, log_id)
        if not log:
            raise NotFoundError("Export log not found")
        
        if not log.file_path:
            raise NotFoundError("Export file not found or has expired")
        
        # Check if it's an S3 URL
        if log.file_path.startswith('http'):
            # For S3 URLs, redirect to the URL
            logger.info(f"Redirecting to S3 URL for export log {log_id}: {log.file_path}")
            return {"type": "redirect", "url": log.file_path}
        
        # For local files, check if they exist
        if not os.path.exists(log.file_path):
            raise NotFoundError("Export file not found or has expired")
        
        filename = os.path.basename(log.file_path)
        return {"type": "file", "file_path": log.file_path, "filename": filename, "format": log.format}
        
    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error downloading export file: {str(e)}")
        raise ValidationError(f"Failed to download export file: {str(e)}") 