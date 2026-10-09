
from documents.models import DocumentChunk
from pgvector.django import CosineDistance
from rag.ai_client import get_embeddings


def get_relevant_chunks(
    user,
    question: str,
    document_id: int | None = None,
    top_k: int = 5,
) -> list[DocumentChunk]:
    query_vector = get_embeddings([question])[0]

    queryset = DocumentChunk.objects.filter(
        document__owner=user,
        embedding__isnull=False,
    ).select_related("document")

    if document_id is not None:
        queryset = queryset.filter(document_id=document_id)

    return list(
        queryset.annotate(
            distance=CosineDistance("embedding", query_vector)
        )
        .order_by("distance")[:top_k]
    )