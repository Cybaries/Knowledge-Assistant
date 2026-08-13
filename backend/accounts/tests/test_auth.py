import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django

django.setup()

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


@pytest.mark.django_db
def test_register_user():
    client = APIClient()

    response = client.post(
        "/api/auth/register/",
        {
            "username": "testuser",
            "email": "test@example.com",
            "password": "StrongPass123",
        },
        format="json",
    )

    assert response.status_code == 201
    assert response.data["username"] == "testuser"
    assert response.data["email"] == "test@example.com"

    assert "password" not in response.data

    assert User.objects.filter(username="testuser").exists()


@pytest.mark.django_db
def test_duplicate_username_registration():
    User.objects.create_user(
        username="existinguser",
        email="existing@example.com",
        password="StrongPass123",
    )

    client = APIClient()

    response = client.post(
        "/api/auth/register/",
        {
            "username": "existinguser",
            "email": "another@example.com",
            "password": "StrongPass123",
        },
        format="json",
    )

    assert response.status_code == 400
    assert "username" in response.data

@pytest.mark.django_db
def test_duplicate_username_registration():
    User.objects.create_user(
        username="existinguser",
        email="existing@example.com",
        password="StrongPass123",
    )

    client = APIClient()

    response = client.post(
        "/api/auth/register/",
        {
            "username": "existinguser",
            "email": "another@example.com",
            "password": "StrongPass123",
        },
        format="json",
    )

    assert response.status_code == 400
    assert "username" in response.data

@pytest.mark.django_db
def test_login_with_wrong_password_fails():
    User.objects.create_user(
        username="wrongpassword",
        password="StrongPass123",
    )

    client = APIClient()

    response = client.post(
        "/api/auth/token/",
        {
            "username": "wrongpassword",
            "password": "WrongPassword",
        },
        format="json",
    )

    assert response.status_code == 401


@pytest.mark.django_db
def test_complete_authentication_flow():
    client = APIClient()

    # 1. Register
    register_response = client.post(
        "/api/auth/register/",
        {
            "username": "flowuser",
            "email": "flow@example.com",
            "password": "StrongPass123",
        },
        format="json",
    )

    assert register_response.status_code == 201

    # 2. Login
    login_response = client.post(
        "/api/auth/token/",
        {
            "username": "flowuser",
            "password": "StrongPass123",
        },
        format="json",
    )

    assert login_response.status_code == 200
    assert "access" in login_response.data
    assert "refresh" in login_response.data

    access_token = login_response.data["access"]
    refresh_token = login_response.data["refresh"]

    # 4. Refresh access token
    refresh_response = client.post(
        "/api/auth/token/refresh/",
        {
            "refresh": refresh_token,
        },
        format="json",
    )

    assert refresh_response.status_code == 200
    assert "access" in refresh_response.data

    new_access_token = refresh_response.data["access"]
