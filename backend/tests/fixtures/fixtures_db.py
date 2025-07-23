import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.extensions import db
from app.models.base import Base

@pytest.fixture(scope="session")
def database_engine(app):
    """Create database engine for testing."""
    return app.extensions['sqlalchemy'].db.engine

@pytest.fixture(scope="function")
def db_session(session):
    """Create a new database session for each test with automatic rollback."""
    return session

@pytest.fixture(scope="function")
def clean_db(session):
    """Ensure clean database state for each test."""
    # Clear all tables
    for table in reversed(db.metadata.sorted_tables):
        session.execute(table.delete())
    session.commit()
    return session

@pytest.fixture
def sample_data(session):
    """Create minimal sample data for testing."""
    # Add any base data needed across tests
    # This can be extended as needed
    session.commit()
    return session