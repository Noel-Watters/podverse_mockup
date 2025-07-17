import os
from sqlalchemy import text
from app.extensions import db

def run_sql_migrations():
    # Get pathing of migration sql files
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
    migration_dir = os.path.join(root_dir, "podverse_db/migrations")
    
    filenames = sorted(f for f in os.listdir(migration_dir) if f.endswith(".sql"))
    
    with db.engine.begin() as connection:
        for filename in filenames:
            path = os.path.join(migration_dir, filename)
            with open(path, "r") as file:
                print(f"Running migration: {filename}")
                connection.execute(text(file.read()))

