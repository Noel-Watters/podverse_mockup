# app/utils/export_response.py

import csv
import io
from flask import Response, request, make_response, jsonify
from typing import List, Dict, Any
from app.utils.error_exceptions import ValidationError

def generate_export_response(data: List[Dict[str, Any]], filename: str, headers: Dict[str, str] = None) -> Response:
    """
    Generate a CSV or JSON response from a list of dictionaries. 
    Default is CSV

    Args:
        data: List of dictionaries representing rows
        filename: Base filename (extension added automatically)
        headers: Dictionary mapping field names to display names (optional for CSV, will infer from data)

    Returns:
        Flask Response with content
    """
    format = request.args.get("format", "csv").lower()
    if format not in ("csv", "json"):
        raise ValidationError("Unsupported format. Use 'csv', 'json' ")

    # Ensure filename has correct extension
    if not filename.endswith(f'.{format}'):
        filename += f'.{format}'

    # Handle empty data
    if not data:
        return jsonify([]) if format == "json" else generate_empty_csv_response(filename)

    if format == "json":
        return jsonify(data)
    elif format == "csv":
        # If no headers provided, infer them from the first data row
        if not headers and data:
            headers = {key: key for key in data[0].keys()}
        elif not headers:
            raise ValidationError("CSV export requires headers or non-empty data.")
        return generate_csv_response(data, headers, filename)

def generate_csv_response(data: List[Dict[str, Any]], headers: Dict[str, str], filename: str) -> Response:
    """
    Generate CSV file response from data and headers.

    Args:
        data: List of dictionaries (rows).
        headers: Dict of column headers.
        filename: Name of the resulting file.

    Returns:
        Flask Response object containing the CSV file.
    """
    output = io.StringIO()  # In-memory text stream for CSV content
    output.write('\ufeff')  # Write BOM (Byte Order Mark) so Excel can recognize UTF-8
    
    writer = csv.DictWriter(output, fieldnames=headers.keys(), quoting=csv.QUOTE_ALL)
    writer.writeheader() # column headers
    writer.writerows({k: row.get(k, "") for k in headers} for row in data) # write rows with required fields if misisng then emtpy string
    
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    response.headers["Content-type"] = "text/csv"
    return response

def generate_empty_csv_response(filename: str) -> Response:
    """
    Generate an empty CSV file response.

    Args:
        filename: Name of the file to return.

    Returns:
        Flask Response with an empty CSV file.
    """
    output = io.StringIO()
    output.write("")
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    response.headers["Content-Type"] = "text/csv"
    return response