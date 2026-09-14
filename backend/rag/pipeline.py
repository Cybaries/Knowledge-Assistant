from django.db import transaction

from documents.models import Document, DocumentChunk, DocumentStatus
from rag.ai_client import get_embeddings
from rag.chunking import chunk_text
from rag.parsers import parse_document


def process_document(document_id: int) -> None:
    document = Document.objects.get(pk=document_id)

    document.status = DocumentStatus.PROCESSING
    document.save(update_fields=["status"])

    try:
        text = parse_document(document.file.path)
        chunks = chunk_text(text)

        if not chunks:
            raise ValueError("Document produced no chunks.")

        embeddings = get_embeddings(chunks)

        if len(embeddings) != len(chunks):
            raise ValueError("Embedding count does not match chunk count.")

        with transaction.atomic():
            DocumentChunk.objects.filter(document=document).delete()

            DocumentChunk.objects.bulk_create(
                [
                    DocumentChunk(
                        document=document,
                        chunk_index=index,
                        text=chunk,
                        embedding=embedding,
                    )
                    for index, (chunk, embedding) in enumerate(zip(chunks, embeddings))
                ]
            )

            document.status = DocumentStatus.READY
            document.save(update_fields=["status"])

    except Exception:
        document.status = DocumentStatus.FAILED
        document.save(update_fields=["status"])
        raise