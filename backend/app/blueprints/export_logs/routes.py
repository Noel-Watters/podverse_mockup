# backend/app/blueprints/export_logs/routes.py

from flask import jsonify, request, send_file
from sqlalchemy import and_, or_, func
from . import export_logs_bp
from app.extensions import limiter, db
from app.models.export_logs import ExportLog
from app.utils.error_exceptions import NotFoundError, ValidationError
from app.utils.auth import requires_auth
from app.utils.request_logger import get_logger
from app.utils.query_params import get_pagination_params, get_sorting_params
from app.utils.query_helpers import paginate_query, apply_sorting
from app.blueprints.export_logs.schemas import export_log_schema
import os
from datetime import datetime, timedelta

logger = get_logger(__name__)

@export_logs_bp.route('/', methods=['GET'])
#@requires_auth
@limiter.limit("100 per day")
def get_export_logs():
    """Get paginated list of export logs. Supports filtering, pagination, status checks"""
    try:
        # Get pagination and sorting parameters
        page, per_page = get_pagination_params(request)
        sort_by, sort_order = get_sorting_params(
            request,
            ['created_at', 'completed_at', 'status', 'export_type', 'format', 'duration'],
            'created_at',
            'desc'
        )

        query = db.session.query(ExportLog)

        # Apply filters
        status = request.args.get('status')
        if status:
            query = query.filter(ExportLog.status == status)

        export_type = request.args.get('export_type')
        if export_type:
            query = query.filter(ExportLog.export_type == export_type) # export_type: channels, feeds

        export_by = request.args.get('export_by')
        if export_by:
            query = query.filter(ExportLog.export_by == export_by)

        log_id = request.args.get('id', type=int)
        if log_id:
            query = query.filter(ExportLog.id == log_id)
            
        format_type = request.args.get('format')
        if format_type:
            query = query.filter(ExportLog.format == format_type)

        # Error status filtering
        has_error = request.args.get('has_error', type=str)
        if has_error:
            if has_error.lower() == 'true':
                query = query.filter(ExportLog.status == 'failed')
            elif has_error.lower() == 'false':
                query = query.filter(ExportLog.status != 'failed')

        # Duration filtering (in seconds)
        min_duration = request.args.get('min_duration', type=float)
        max_duration = request.args.get('max_duration', type=float)
        
        if min_duration is not None or max_duration is not None:
            # Calculate duration using SQL expression
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

        # Text search across error_message field
        search_term = request.args.get('search')
        if search_term:
            search_filter = or_(
                ExportLog.error_message.ilike(f'%{search_term}%')
            )
            query = query.filter(search_filter)
            
        # Apply sorting
        if sort_by == 'duration':
            # Custom sorting for duration
            duration_expr = func.extract('epoch', ExportLog.completed_at - ExportLog.created_at)
            if sort_order == 'asc':
                query = query.order_by(duration_expr.asc())
            else:
                query = query.order_by(duration_expr.desc())
        else:
            query = apply_sorting(query, ExportLog, sort_by, sort_order)

        # Paginate
        logs, pagination_metadata = paginate_query(query, page, per_page)

        return jsonify({
            'logs': [export_log_schema.dump(log) for log in logs],
            **pagination_metadata
        })

    except Exception as e:
        logger.error(f"Error retrieving export logs: {str(e)}")
        raise ValidationError(f"Failed to retrieve export logs: {str(e)}")


@export_logs_bp.route('/<int:log_id>', methods=['GET'])
#@requires_auth
@limiter.limit("100 per day")
def get_export_log(log_id):
    """Get detailed information about a specific export log"""
    try:
        log = db.session.get(ExportLog, log_id)
        if not log:
            raise NotFoundError("Export log not found")

        return jsonify(export_log_schema.dump(log))

    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error retrieving export log {log_id}: {str(e)}")
        raise ValidationError(f"Failed to retrieve export log: {str(e)}")


@export_logs_bp.route('/<int:log_id>/download', methods=['GET'])
#@requires_auth
@limiter.limit("50 per day")
def download_export_file(log_id):
    """Download the exported file for a specific log"""
    try:
        log = db.session.get(ExportLog, log_id)
        if not log:
            raise NotFoundError("Export log not found")

        if not log.file_path or not os.path.exists(log.file_path):
            raise NotFoundError("Export file not found or has expired")

        filename = os.path.basename(log.file_path)

        return send_file(
            log.file_path,
            as_attachment=True,
            download_name=filename,
            mimetype='text/csv' if log.format == 'csv' else 'application/json'
        )

    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error downloading export file: {str(e)}")
        raise ValidationError(f"Failed to download export file: {str(e)}")
