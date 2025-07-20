import pytest
from datetime import datetime, timedelta
import jwt
from app.extensions import db
from app.models.account import Account
from app.models.user import User

@pytest.fixture
def test_user(session):
    """Create a test user."""
    user = User(
        email='test@example.com',
        username='testuser',
        role='user',
        is_active=True,
        referral_token='test-token-123'
    )
    session.add(user)
    session.commit()
    return user

@pytest.fixture
def admin_user(session):
    """Create an admin user."""
    admin = User(
        email='admin@example.com',
        username='adminuser',
        role='admin',
        is_active=True,
        referral_token='admin-token-456'
    )
    session.add(admin)
    session.commit()
    return admin

@pytest.fixture
def test_account(session):
    """Create a test account."""
    account = Account(
        id_text='TEST001',
        verified=True
    )
    session.add(account)
    session.commit()
    return account

@pytest.fixture
def auth_headers(app, test_user):
    """Generate authentication headers for regular user."""
    token = jwt.encode(
        {
            'user_id': test_user.id,
            'email': test_user.email,
            'role': test_user.role,
            'exp': datetime.utcnow() + timedelta(hours=1)
        },
        app.config['SECRET_KEY'],
        algorithm='HS256'
    )
    return {'Authorization': f'Bearer {token}'}

@pytest.fixture
def admin_auth_headers(app, admin_user):
    """Generate authentication headers for admin user."""
    token = jwt.encode(
        {
            'user_id': admin_user.id,
            'email': admin_user.email,
            'role': admin_user.role,
            'exp': datetime.utcnow() + timedelta(hours=1)
        },
        app.config['SECRET_KEY'],
        algorithm='HS256'
    )
    return {'Authorization': f'Bearer {token}'}

@pytest.fixture
def expired_token_headers(app, test_user):
    """Generate expired authentication headers for testing token expiration."""
    token = jwt.encode(
        {
            'user_id': test_user.id,
            'email': test_user.email,
            'role': test_user.role,
            'exp': datetime.utcnow() - timedelta(hours=1)  # Expired
        },
        app.config['SECRET_KEY'],
        algorithm='HS256'
    )
    return {'Authorization': f'Bearer {token}'} 