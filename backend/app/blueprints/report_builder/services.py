import csv, os, json
from datetime import datetime
from app.models.export_logs import ExportLog
from app.utils.file_system_helpers import safe_write_file
from app.blueprints.report_builder.query_builder import build_dynamic_query
from app.extensions import db

def export_custom_report(user_email, source, fields, filters, export_format):
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    filename = f"{source}_custom_export_{timestamp}.{export_format}"
    export_dir = os.path.join(os.getcwd(), "exports")
    os.makedirs(export_dir, exist_ok=True)
    full_path = os.path.join(export_dir, filename)

    query = build_dynamic_query(source, fields, filters, db.session)
    rows = query.all()
    export_count = len(rows)

    def write_file(f):
        if export_format == "csv":
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            for row in rows:
                writer.writerow({f: getattr(row, f, "") for f in fields})
        elif export_format == "json":
            #json.dump([{f: getattr(row, f, "") for f in fields} for row in rows], f, indent=2)
            json.dump([{f: getattr(row, f, "") for f in fields} for row in rows], f, indent=2, default=str)
    
    success, error = safe_write_file(full_path, write_file)
    if not success:
        raise Exception(f"Failed to write export file: {error}")
    
    export_log = ExportLog(
        export_by=user_email,
        source=source,
        format=export_format,
        filters=filters,
        file_path=full_path,
        status="success",
        created_at=datetime.utcnow(),
        completed_at=datetime.utcnow()
    )

    count_field = f"{source}_count"
    if hasattr(export_log, count_field):
        setattr(export_log, count_field, export_count)

    db.session.add(export_log)
    db.session.commit()

    return {
        "log_id": export_log.id,
        "file_path": full_path,
        "filename": filename,
        "count": export_count
    }