from app.blueprints.report_builder.schema import CustomReportSchema
from app.blueprints.report_builder.services import export_custom_report

def handle_custom_report(data):
    schema = CustomReportSchema()
    validated = schema.load(data)

    export_result = export_custom_report(
        user_email=validated["exported_by"],
        source=validated["source"],
        fields=validated["selected_fields"],
        filters=validated["filters"],
        export_format=validated["format"]
    )

    return {
        "message": "Report exported successfully",
        "log_id": export_result["log_id"],
        "filename": export_result["filename"],
        "count": export_result["count"]
    }