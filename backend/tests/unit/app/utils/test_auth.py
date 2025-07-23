# tests/unit/test_auth.py

import pytest
from flask import Flask, request
from app.utils.auth import get_token_auth_header, requires_auth
from app.utils.error_exceptions import AuthError
from jose import jwt
import json

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config.update({
        "AUTH0_DOMAIN": "test.auth0.com",
        "API_AUDIENCE": "test-api",
        "ALGORITHMS": "RS256"
    })
    return app

def test_get_token_auth_header_valid_token(app):
    with app.test_request_context(headers={"Authorization": "Bearer testtoken"}):
        token = get_token_auth_header()
        assert token == "testtoken"

@pytest.mark.parametrize("header", [
    None,
    "Basic sometoken",
    "Bearer",
    "Bearer one two"
])
def test_get_token_auth_header_invalid(header, app):
    with app.test_request_context(headers={"Authorization": header} if header else {}):
        with pytest.raises(AuthError):
            get_token_auth_header()

def test_requires_auth_valid_token(monkeypatch, app):
    rsa_key = {
        "kty": "RSA", "kid": "1234", "use": "sig", "n": "abc", "e": "AQAB"
    }
    token = jwt.encode({"sub": "user123", "aud": "test-api", "iss": "https://test.auth0.com/"}, "secret", algorithm="HS256")
    
    @requires_auth
    def dummy_view():
        return "success"

    monkeypatch.setattr("app.utils.auth.get_token_auth_header", lambda: token)
    monkeypatch.setattr("app.utils.auth.jwt.get_unverified_header", lambda x: {"kid": "1234"})
    monkeypatch.setattr("app.utils.auth.requests.get", lambda url: type("Resp", (), {"json": staticmethod(lambda: {"keys": [rsa_key]})})())
    monkeypatch.setattr("app.utils.auth.jwt.decode", lambda *a, **kw: {"sub": "user123"})

    with app.test_request_context():
        assert dummy_view() == "success"