from unittest.mock import Mock

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.main import app
from app.service import auth_service

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
