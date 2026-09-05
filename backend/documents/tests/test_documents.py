import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from documents.models import Document
from rest_framework.test import APIClient

User = get_user_model()


def create_test_file(name="test.txt"):
    return SimpleUploadedFile(
        name,
        b"Test document content.",
        content_type="text/plain",
    )


@pytest.mark.django_db
def test_user_can_only_list_own_documents():
    user1 = User.objects.create_user(
        username="user1",
        password="StrongPass123",
    )

    user2 = User.objects.create_user(
        username="user2",
        password="StrongPass123",
    )

    Document.objects.create(
        title="User 1 Document",
        owner=user1,
        file=create_test_file("user1.txt"),
    )

    Document.objects.create(
        title="User 2 Document",
        owner=user2,
        file=create_test_file("user2.txt"),
    )

    client = APIClient()

    client.force_authenticate(user=user1)

    response = client.get("/api/documents/")

    assert response.status_code == 200

    titles = [
    document["title"]
    for document in response.data["results"]
]

    assert "User 1 Document" in titles
    assert "User 2 Document" not in titles

@pytest.mark.django_db
def test_user_cannot_retrieve_another_users_document():
    user1 = User.objects.create_user(
        username="user1",
        password="StrongPass123",
    )

    user2 = User.objects.create_user(
        username="user2",
        password="StrongPass123",
    )

    document = Document.objects.create(
        title="Private Document",
        owner=user2,
        file=create_test_file("private.txt"),
    )

    client = APIClient()
    client.force_authenticate(user=user1)

    response = client.get(
        f"/api/documents/{document.id}/"
    )

    assert response.status_code == 404

@pytest.mark.django_db
def test_user_can_upload_valid_file():
    user = User.objects.create_user(
        username="uploaduser",
        password="StrongPass123",
    )

    client = APIClient()
    client.force_authenticate(user=user)

    file = SimpleUploadedFile(
        "document.txt",
        b"Valid document content.",
        content_type="text/plain",
    )

    response = client.post(
        "/api/documents/",
        {
            "title": "Valid Document",
            "file": file,
        },
        format="multipart",
    )

    assert response.status_code == 201
    assert Document.objects.filter(
        title="Valid Document",
        owner=user,
    ).exists()

@pytest.mark.django_db
def test_upload_rejects_invalid_file_type():
    user = User.objects.create_user(
        username="invalidtype",
        password="StrongPass123",
    )

    client = APIClient()
    client.force_authenticate(user=user)

    file = SimpleUploadedFile(
        "malicious.exe",
        b"Not a valid document.",
        content_type="application/octet-stream",
    )

    response = client.post(
        "/api/documents/",
        {
            "title": "Invalid File",
            "file": file,
        },
        format="multipart",
    )

    assert response.status_code == 400
    assert "file" in response.data

@pytest.mark.django_db
def test_upload_rejects_large_file():
    user = User.objects.create_user(
        username="largefile",
        password="StrongPass123",
    )

    client = APIClient()
    client.force_authenticate(user=user)

    large_content = b"x" * (10 * 1024 * 1024 + 1)

    file = SimpleUploadedFile(
        "large.txt",
        large_content,
        content_type="text/plain",
    )

    response = client.post(
        "/api/documents/",
        {
            "title": "Large File",
            "file": file,
        },
        format="multipart",
    )

    assert response.status_code == 400
    assert "file" in response.data