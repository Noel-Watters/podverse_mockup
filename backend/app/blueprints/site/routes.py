# backend/app/blueprints/site/routes.py

from flask import Blueprint, current_app, render_template, request, flash
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from app.extensions import db

site_bp = Blueprint("site", __name__)

@site_bp.route("/", strict_slashes=False)
def site_home():
    route_list = []

    for rule in current_app.url_map.iter_rules():
        # Filter only relevant /admin routes
        if (
            rule.rule.startswith("/admin")
            and "GET" in rule.methods
            and not rule.rule.startswith("/admin/site")
            and not rule.rule.endswith("/<path:filename>")
        ):
            route_list.append({
                "endpoint": rule.endpoint,
                "url": rule.rule
            })

    return render_template('sitemap.html', routes=sorted(route_list, key=lambda r: r["url"]))

@site_bp.route('/sql-runner', methods=['GET', 'POST'])
def sql_runner():
    result = None
    error = None

    if request.method == 'POST':
        sql_script = request.form.get('sql_script', '').strip()
        if not sql_script:
            flash('Please enter some SQL to execute.', 'warning')
        else:
            try:
                with db.engine.begin() as conn:  
                    res = conn.execute(text(sql_script))
                    if res.returns_rows:
                        rows = res.fetchall()
                        columns = res.keys()
                        result = [{'columns': columns, 'rows': rows, 'statement': sql_script}]
                    else:
                        result = [{'columns': [], 'rows': [], 'statement': sql_script, 'rowcount': res.rowcount}]
            except SQLAlchemyError as e:
                error = str(e)

    return render_template('sql_runner.html', result=result, error=error)