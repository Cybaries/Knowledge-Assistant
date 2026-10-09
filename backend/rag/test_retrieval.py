from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from documents.models import Document, DocumentChunk, DocumentStatus
from rag.retrieval import get_relevant_chunks

User = get_user_model()


class RetrievalTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="retrieval_user",
            password="test-password",
        )
        self.other_user = User.objects.create_user(
            username="other_user",
            password="test-password",
        )

        self.document = Document.objects.create(
            title="My document",
            owner=self.user,
            status=DocumentStatus.READY,
        )
        self.other_document = Document.objects.create(
            title="Other user's document",
            owner=self.other_user,
            status=DocumentStatus.READY,
        )

        self.close_chunk = DocumentChunk.objects.create(
            document=self.document,
            chunk_index=0,
            text="A close match",
            embedding=[1.0] + [0.0] * 383,
        )
        self.far_chunk = DocumentChunk.objects.create(
            document=self.document,
            chunk_index=1,
            text="A less relevant match",
            embedding=[0.0, 1.0] + [0.0] * 382,
        )
        self.other_user_chunk = DocumentChunk.objects.create(
            document=self.other_document,
            chunk_index=0,
            text="Private information",
            embedding=[1.0] + [0.0] * 383,
        )

    @patch("rag.retrieval.get_embeddings")
    def test_chunks_are_ranked_by_cosine_distance(self, mock_embeddings):
        mock_embeddings.return_value = [[1.0] + [0.0] * 383]

        results = get_relevant_chunks(
            user=self.user,
            question="Find a close match",
        )

        self.assertEqual(
            [chunk.pk for chunk in results],
            [self.close_chunk.pk, self.far_chunk.pk],
        )

    @patch("rag.retrieval.get_embeddings")
    def test_only_returns_chunks_owned_by_user(self, mock_embeddings):
        mock_embeddings.return_value = [[1.0] + [0.0] * 383]

        results = get_relevant_chunks(
            user=self.user,
            question="Find relevant information",
        )

        self.assertTrue(results)
        self.assertTrue(
            all(chunk.document.owner_id == self.user.pk for chunk in results)
        )
        self.assertNotIn(
            self.other_user_chunk.pk,
            [chunk.pk for chunk in results],
        )

    @patch("rag.retrieval.get_embeddings")
    def test_can_filter_by_document_id(self, mock_embeddings):
        mock_embeddings.return_value = [[1.0] + [0.0] * 383]

        results = get_relevant_chunks(
            user=self.user,
            question="Find relevant information",
            document_id=self.document.pk,
        )

        self.assertTrue(results)
        self.assertTrue(all(chunk.document_id == self.document.pk for chunk in results))

    @patch("rag.retrieval.get_embeddings")
    def test_cannot_retrieve_another_users_document_by_id(self, mock_embeddings):
        mock_embeddings.return_value = [[1.0] + [0.0] * 383]

        results = get_relevant_chunks(
            user=self.user,
            question="Find private information",
            document_id=self.other_document.pk,
        )

        self.assertEqual(results, [])
