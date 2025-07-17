from app import create_app
from app.extensions import db
from dotenv import load_dotenv
import os
from flask import redirect
from app.utils.logger import get_logger
from app.utils.migration_runner import run_sql_migrations

load_dotenv() # loads .env from root

# Use our centralized logger
logger = get_logger(__name__)

config_name = os.getenv("FLASK_ENV", "development")
app = create_app(config_name)

# Redirect root path to the admin sitemap
@app.route("/")
def redirect_to_sitemap():
    return redirect("/admin/site")


if __name__ == '__main__':
    try:
        logger.info("Starting Podverse backend application...")
        with app.app_context():
            # Run Migrations before running create_all
            run_sql_migrations()
            db.create_all()
            logger.info("Database tables created/verified successfully")
        logger.info("Starting Flask server on port 8000...")
        app.run(debug=True, host="0.0.0.0", port=8000, use_reloader=False)
    except Exception as e:
        logger.error("Fatal error during startup: %s", e)
