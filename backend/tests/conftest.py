# Import test configuration to override environment variables FIRST
import test_config 

import pytest
from app import create_app
from app.extensions import db as _db
import os

# Load environment variables from .env.test.local
def load_env_file(filepath):
    """Load environment variables from a .env file"""
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value

# Load test environment variables
load_env_file(os.path.join(os.path.dirname(__file__), '.env.test.local'))

# Debug: Print the DATABASE_URL to see what's being loaded
print(f"DEBUG: DATABASE_URL = {os.environ.get('DATABASE_URL', 'NOT SET')}")
print(f"DEBUG: TEST_DATABASE_URL = {os.environ.get('TEST_DATABASE_URL', 'NOT SET')}")
print(f"DEBUG: FLASK_ENV = {os.environ.get('FLASK_ENV', 'NOT SET')}")
   
@pytest.fixture(scope='session')
def app():
    """Create a Flask app context for the tests."""
    # Debug: Print the configuration being used
    print(f"DEBUG: Creating app with config 'testing'")
    print(f"DEBUG: TEST_DATABASE_URL = {os.environ.get('TEST_DATABASE_URL', 'NOT SET')}")
    
    app = create_app('testing')
    
    # Debug: Print the app config
    print(f"DEBUG: App SQLALCHEMY_DATABASE_URI = {app.config.get('SQLALCHEMY_DATABASE_URI', 'NOT SET')}")
    
    # Create an application context
    with app.app_context():
        yield app

@pytest.fixture(scope='session')
def db(app):
    """Create a database for the tests."""
    _db.create_all()
    yield _db
    _db.drop_all()

@pytest.fixture(scope='function')
def session(db):
    """Create a new database session for a test."""
    connection = db.engine.connect()
    transaction = connection.begin()
    
    # Create a new session bound to the connection
    session = db.session
    
    yield session
    
    transaction.rollback()
    connection.close()
    session.remove()

@pytest.fixture(scope='function')
def test_client(app):
    """Create a test client for the Flask app."""
    with app.test_client() as client:
        yield client 