from flask import Blueprint

report_builder_bp = Blueprint("report_builder", __name__)

from . import routes