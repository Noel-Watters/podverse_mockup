import pytest
from flask import url_for
import json

@pytest.fixture
def api_client(test_client):
    """Create a test client for API testing."""
    return test_client

@pytest.fixture
def api_headers():
    """Default headers for API requests."""
    return {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

@pytest.fixture
def authenticated_headers(api_headers, auth_headers):
    """Headers with authentication for API requests."""
    return {**api_headers, **auth_headers}

@pytest.fixture
def admin_headers(api_headers, admin_auth_headers):
    """Headers with admin authentication for API requests."""
    return {**api_headers, **admin_auth_headers}

def assert_response_status(response, expected_status):
    """Helper to assert response status code."""
    assert response.status_code == expected_status, \
        f"Expected status {expected_status}, got {response.status_code}. Response: {response.get_data(as_text=True)}"

def assert_json_response(response, expected_status=200):
    """Helper to assert JSON response with status code."""
    assert_response_status(response, expected_status)
    assert response.is_json
    return response.get_json()

def assert_error_response(response, expected_status, error_type=None):
    """Helper to assert error response."""
    assert_response_status(response, expected_status)
    if error_type:
        data = response.get_json()
        assert 'error' in data or 'message' in data 