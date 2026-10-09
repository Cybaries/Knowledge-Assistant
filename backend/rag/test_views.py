
from unittest.mock import patch

from django.contrib.auth import get_user_model
from documents.models import Document, DocumentChunk, DocumentStatus
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class QueryViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="query_user",
            password="test-password",
        )
        self.client.force_authenticate(user=self.user)

        self.document = Document.objects.create(
            title="Knowledge Assistant Guide",
            owner=self.user,
            status=DocumentStatus.READY,
        )

        self.chunk = DocumentChunk.objects.create(
            document=self.document,
            chunk_index=0,
            text="The project uses Django and PostgreSQL.",
            embedding=[1.0] + [0.0] * 383,
        )

        self.url = "/api/rag/query/"

    @patch("rag.views.generate")
    @patch("rag.views.get_relevant_chunks")
    def test_returns_answer_and_sources(
        self, mock_retrieval, mock_generate
    ):
        mock_retrieval.return_value = [self.chunk]
        mock_generate.return_value = "The project uses Django and PostgreSQL."

        response = self.client.post(
            self.url,
            {"question": "Which technologies does the project use?"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["answer"],
            "The project uses Django and PostgreSQL.",
        )
        self.assertEqual(
            response.data["sources"],
            [
                {
                    "document_title": "Knowledge Assistant Guide",
                    "chunk_index": 0,
                }
            ],
        )
        mock_generate.assert_called_once()

    @patch("rag.views.generate")
    @patch("rag.views.get_relevant_chunks")
    def test_no_chunks_returns_unknown_without_generating(
        self, mock_retrieval, mock_generate
    ):
        mock_retrieval.return_value = []

        response = self.client.post(
            self.url,
            {"question": "What does the document say?"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("I don't know", response.data["answer"])
        self.assertEqual(response.data["sources"], [])
        mock_generate.assert_not_called()

    def test_unauthenticated_request_returns_401(self):
        self.client.force_authenticate(user=None)

        response = self.client.post(
            self.url,
            {"question": "What does the document say?"},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_blank_question_is_rejected(self):
        response = self.client.post(
            self.url,
            {"question": "   "},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )