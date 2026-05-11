"""Tests for authentication endpoints."""
import pytest
from fastapi.testclient import TestClient


def test_login_success(client, doctor_user):
    resp = client.post("/api/v1/auth/login", json={
        "email": "doctor@test.com",
        "password": "Test@1234",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, doctor_user):
    resp = client.post("/api/v1/auth/login", json={
        "email": "doctor@test.com",
        "password": "wrong",
    })
    assert resp.status_code == 401


def test_login_unknown_email(client):
    resp = client.post("/api/v1/auth/login", json={
        "email": "nobody@test.com",
        "password": "pass",
    })
    assert resp.status_code == 401


def test_refresh_token(client, doctor_user):
    login = client.post("/api/v1/auth/login", json={
        "email": "doctor@test.com",
        "password": "Test@1234",
    })
    refresh_token = login.json()["refresh_token"]
    resp = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_refresh_invalid_token(client):
    resp = client.post("/api/v1/auth/refresh", json={"refresh_token": "bad.token.here"})
    assert resp.status_code == 401


def test_get_me(client, doctor_headers):
    resp = client.get("/api/v1/users/me", headers=doctor_headers)
    assert resp.status_code == 200
    assert resp.json()["email"] == "doctor@test.com"


def test_protected_route_without_token(client):
    resp = client.get("/api/v1/users/me")
    assert resp.status_code == 403


def test_mfa_setup_and_disable(client, db, doctor_user, doctor_headers):
    # Setup MFA
    resp = client.post("/api/v1/auth/mfa/setup", headers=doctor_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "secret" in data
    assert "qr_uri" in data
    assert "backup_codes" in data

    # Disable MFA using valid TOTP code
    import pyotp
    totp = pyotp.TOTP(data["secret"])
    code = totp.now()
    resp2 = client.post(
        "/api/v1/auth/mfa/disable",
        json={"code": code},
        headers=doctor_headers,
    )
    assert resp2.status_code == 200
