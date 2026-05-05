from flask import request, jsonify
from . import report_builder_bp
from app.blueprints.report_builder.controller import handle_custom_report

@report_builder_bp.route("/custom", methods=['POST'])
def custom_report():
    data = request.get_json()
    result = handle_custom_report(data)
    return jsonify(result)