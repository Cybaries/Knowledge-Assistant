from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from documents.models import Document, DocumentChunk, DocumentStatus
from rag.ai_client import AIServiceError
from rag.pipeline import process_document

User = get_user_model()


class ProcessDocumentTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword",
        )

        self.document = Document.objects.create(
            title="Test Document",
            file=SimpleUploadedFile(
                "test.txt",
                b"First paragraph.\n\nSecond paragraph.",
                content_type="text/plain",
            ),
            owner=self.user,
        )

    @patch("rag.pipeline.get_embeddings")
    @patch("rag.pipeline.parse_document")
    def test_successful_processing(
        self,
        mock_parse_document,
        mock_get_embeddings,
    ):
        mock_parse_document.return_value = (
            "First paragraph.\n\nSecond paragraph."
        )
        mock_get_embeddings.return_value = [
            [0.1] * 384,
        ]

        process_document(self.document.pk)

        self.document.refresh_from_db()

        self.assertEqual(self.document.status, DocumentStatus.READY)
        self.assertEqual(
            DocumentChunk.objects.filter(document=self.document).count(),
            1,
        )

        chunks = list(
            DocumentChunk.objects.filter(document=self.document).order_by(
                "chunk_index"
            )
        )

        self.assertEqual(chunks[0].chunk_index, 0)
        self.assertEqual(len(chunks[0].embedding), 384)

    @patch("rag.pipeline.parse_document")
    def test_parsing_failure_marks_document_failed(self, mock_parse_document):
        mock_parse_document.side_effect = ValueError("Parsing failed")

        with self.assertRaises(ValueError):
            process_document(self.document.pk)

        self.document.refresh_from_db()

        self.assertEqual(self.document.status, DocumentStatus.FAILED)
        self.assertEqual(
            DocumentChunk.objects.filter(document=self.document).count(),
            0,
        )

    @patch("rag.pipeline.get_embeddings")
    @patch("rag.pipeline.parse_document")
    def test_ai_failure_marks_document_failed(
        self,
        mock_parse_document,
        mock_get_embeddings,
    ):
        mock_parse_document.return_value = "Test document text."
        mock_get_embeddings.side_effect = AIServiceError(
            "Embedding service unavailable."
        )

        with self.assertRaises(AIServiceError):
            process_document(self.document.pk)

        self.document.refresh_from_db()

        self.assertEqual(self.document.status, DocumentStatus.FAILED)
        self.assertEqual(
            DocumentChunk.objects.filter(document=self.document).count(),
            0,
        )