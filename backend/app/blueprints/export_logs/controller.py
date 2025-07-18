from app.extensions import db
from app.models.export_logs import ExportLog
from app.utils.error_exceptions import NotFoundError, ValidationError
from app.utils.request_logger import get_logger
from app.utils.query_params import get_pagination_params, get_sorting_params
from app.utils.query_helpers import paginate_query, apply_sorting
from app.blueprints.export_logs.schemas import export_log_schema
from sqlalchemy import and_, or_, func
import os

logger = get_logger(__name__)

def get_export_logs_controller(request):
    """Get paginated list of export logs. Supports filtering, pagination, status checks. See API.md for query params and status codes."""
    try:
        page, per_page = get_pagination_params(request)
        sort_by, sort_order = get_sorting_params(
            request,
            ['created_at', 'completed_at', 'status', 'export_type', 'format', 'duration'],
            'created_at',
            'desc'
        )
        query = db.session.query(ExportLog)
        status = request.args.get('status')
        if status:
            query = query.filter(ExportLog.status == status)
        export_type = request.args.get('export_type')
        if export_type:
            query = query.filter(ExportLog.export_type == export_type)
        export_by = request.args.get('export_by')
        if export_by:
            query = query.filter(ExportLog.export_by == export_by)
        log_id = request.args.get('id', type=int)
        if log_id:
            query = query.filter(ExportLog.id == log_id)
        format_type = request.args.get('format')
        if format_type:
            query = query.filter(ExportLog.format == format_type)
        has_error = request.args.get('has_error', type=str)
        if has_error:
            if has_error.lower() == 'true':
                query = query.filter(ExportLog.status == 'failed')
            elif has_error.lower() == 'false':
                query = query.filter(ExportLog.status != 'failed')
        min_duration = request.args.get('min_duration', type=float)
        max_duration = request.args.get('max_duration', type=float)
        if min_duration is not None or max_duration is not None:
            duration_expr = func.extract('epoch', ExportLog.completed_at - ExportLog.created_at)
            if min_duration is not None:
                query = query.filter(duration_expr >= min_duration)
            if max_duration is not None:
                query = query.filter(duration_expr <= max_duration)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        if start_date and end_date:
            query = query.filter(
                and_(
                    ExportLog.created_at >= start_date,
                    ExportLog.created_at <= end_date
                )
            )
        search_term = request.args.get('search')
        if search_term:
            search_filter = or_(
                ExportLog.error_message.ilike(f'%{search_term}%')
            )
            query = query.filter(search_filter)
        if sort_by == 'duration':
            duration_expr = func.extract('epoch', ExportLog.completed_at - ExportLog.created_at)
            if sort_order == 'asc':
                query = query.order_by(duration_expr.asc())
            else:
                query = query.order_by(duration_expr.desc())
        else:
            query = apply_sorting(query, ExportLog, sort_by, sort_order)
        logs, pagination_metadata = paginate_query(query, page, per_page)
        return [export_log_schema.dump(log) for log in logs], pagination_metadata
    except Exception as e:
        logger.error(f"Error retrieving export logs: {str(e)}")
        raise ValidationError(f"Failed to retrieve export logs: {str(e)}")

def get_export_log_controller(log_id):
    """Get a single export log by ID. See API.md for status codes."""
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

def download_export_file_controller(log_id):
    """Download an export file by log ID. See API.md for status codes."""
    try:
        log = db.session.get(ExportLog, log_id)
        if not log:
            raise NotFoundError("Export log not found")
        if not log.file_path or not os.path.exists(log.file_path):
            raise NotFoundError("Export file not found or has expired")
        filename = os.path.basename(log.file_path)
        return log.file_path, filename, log.format
    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error downloading export file: {str(e)}")
        raise ValidationError(f"Failed to download export file: {str(e)}") 