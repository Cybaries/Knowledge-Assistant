from django.test import SimpleTestCase
from rag.chunking import CHUNK_OVERLAP, CHUNK_SIZE, chunk_text


class ChunkTextTests(SimpleTestCase):
    def test_empty_text_returns_no_chunks(self):
        self.assertEqual(chunk_text(""), [])

    def test_short_text_returns_single_chunk(self):
        text = "This is a short document."

        chunks = chunk_text(text)

        self.assertEqual(chunks, [text])

    def test_long_paragraph_is_split_with_overlap(self):
        text = "A" * 2000

        chunks = chunk_text(text)

        self.assertGreater(len(chunks), 1)

        for chunk in chunks[:-1]:
            self.assertEqual(len(chunk), CHUNK_SIZE)

        self.assertEqual(
            chunks[0][-CHUNK_OVERLAP:],
            chunks[1][:CHUNK_OVERLAP],
        )

    def test_paragraphs_are_combined_until_chunk_limit(self):
        text = (
            "First paragraph. " * 30
            + "\n\n"
            + "Second paragraph. " * 30
        )

        chunks = chunk_text(text)

        self.assertGreater(len(chunks), 1)
        self.assertTrue(all(chunk.strip() for chunk in chunks))