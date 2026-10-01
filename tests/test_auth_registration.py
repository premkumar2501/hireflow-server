from unittest.mock import Mock

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.main import app
from app.service import auth_service, user_service
from app.middleware import user_auth as user_auth_module
from app.schema.user import UserUpdate

client = TestClient(app)


def test_register_returns_validation_error_for_missing_fields():
    response = client.post(
        "/auth/register",
        json={
            "username": "john",
            "password": "short",
        },
    )

    assert response.status_code == 422
    payload = response.json()
    assert payload["success"] is False
    assert "email" in payload["error"]["message"] or "phoneNo" in payload["error"]["message"]


def test_register_returns_user_and_token():
    db = Mock()
    db.query.return_value.filter.return_value.first.return_value = None
    db.add.return_value = None
    db.commit.return_value = None
    db.refresh.side_effect = lambda user: setattr(user, "id", 1)

    user = Mock(email="john@example.com", username="john", password="password123", phoneNo="1234567890")
    response = auth_service.register(db, user)

    assert response.user.email == "john@example.com"
    assert response.user.username == "john"
    assert response.verification_token


def test_register_raises_http_exception_when_user_already_exists():
    db = Mock()
    user = Mock()
    user.email = "john@example.com"
    user.username = "john"
    db.query.return_value.filter.return_value.first.return_value = user

    with pytest.raises(HTTPException) as exc_info:
        auth_service.register(db, Mock(email="john@example.com", username="john", password="password123", phoneNo="1234567890"))

    assert exc_info.value.status_code == 400
    assert "already exists" in exc_info.value.detail.lower()


def test_verify_user_activates_account(monkeypatch):
    db = Mock()
    user = Mock(is_varify=False, is_active=False)
    db.query.return_value.filter.return_value.first.return_value = user
    monkeypatch.setattr(auth_service, "verify_verification_token", lambda token: "john@example.com")

    result = auth_service.verify_user(Mock(token="valid-token"), db)

    assert result is user
    assert user.is_varify is True
    assert user.is_active is True
    db.commit.assert_called_once()


def test_user_auth_rejects_refresh_token(monkeypatch):
    db = Mock()
    monkeypatch.setattr(user_auth_module.jwt, "decode", lambda *args, **kwargs: {"sub": "1", "type": "refresh"})

    with pytest.raises(HTTPException) as exc_info:
        user_auth_module.user_auth(Mock(credentials="refresh-token"), db)

    assert exc_info.value.status_code == 401
    db.get.assert_not_called()


def test_user_update_accepts_partial_payload():
    assert UserUpdate(username="new-name").model_dump(exclude_unset=True) == {"username": "new-name"}


def test_user_update_changes_only_supplied_fields():
    db = Mock()
    user = Mock(email="john@example.com", username="john", phoneNo="1234567890")
    db.query.return_value.filter.return_value.first.side_effect = [user, None]

    result = user_service.update_user(db, 1, UserUpdate(username="new-name"))

    assert result is user
    assert user.email == "john@example.com"
    assert user.username == "new-name"
    assert user.phoneNo == "1234567890"
    db.commit.assert_called_once()


def test_login_rejects_unverified_user(monkeypatch):
    db = Mock()
    db.query.return_value.filter.return_value.first.return_value = Mock(
        password="hashed-password",
        is_varify=False,
        is_active=False,
    )
    monkeypatch.setattr(auth_service, "verify_password", lambda plain, hashed: True)

    with pytest.raises(HTTPException) as exc_info:
        auth_service.login(Mock(email="john@example.com", password="password123"), db)

    assert exc_info.value.status_code == 403
