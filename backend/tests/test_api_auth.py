"""Tests for auth endpoints."""
import pytest


def test_register_new_user(client):
    resp = client.post("/api/v1/auth/register", json={
        "email": "newuser@example.com",
        "password": "password123",
        "full_name": "New User"
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "newuser@example.com"
    assert "id" in data


def test_register_duplicate_email(client):
    payload = {"email": "dup@example.com", "password": "password123"}
    client.post("/api/v1/auth/register", json=payload)
    resp = client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 400


def test_login_success(client):
    client.post("/api/v1/auth/register", json={
        "email": "logintest@example.com",
        "password": "mypassword"
    })
    resp = client.post("/api/v1/auth/login", json={
        "email": "logintest@example.com",
        "password": "mypassword"
    })
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_wrong_password(client):
    resp = client.post("/api/v1/auth/login", json={
        "email": "nonexistent@example.com",
        "password": "wrong"
    })
    assert resp.status_code == 401


def test_protected_route_without_token(client):
    resp = client.get("/api/v1/resumes/")
    assert resp.status_code == 403


def test_health_check(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
