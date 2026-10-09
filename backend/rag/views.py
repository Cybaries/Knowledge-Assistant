from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from rag.ai_client import AIServiceError, generate
from rag.retrieval import get_relevant_chunks
from rag.serializers import QueryRequestSerializer, QueryResponseSerializer


class QueryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        request=QueryRequestSerializer,
        responses=QueryResponseSerializer,
    )
    def post(self, request):
        request_serializer = QueryRequestSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)

        question = request_serializer.validated_data["question"]
        document_id = request_serializer.validated_data.get("document_id")

        try:
            chunks = get_relevant_chunks(
                user=request.user,
                question=question,
                document_id=document_id,
                top_k=5,
            )
        except AIServiceError:
            return Response(
                {
                    "detail": (
                        "The AI service is temporarily unavailable. "
                        "Please try again later."
                    )
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        if not chunks:
            response_data = {
                "answer": "I don't know based on the available documents.",
                "sources": [],
            }
            response_serializer = QueryResponseSerializer(data=response_data)
            response_serializer.is_valid(raise_exception=True)
            return Response(
                response_serializer.data,
                status=status.HTTP_200_OK,
            )

        context = "\n\n".join(
            f"Source: {chunk.document.title}\n{chunk.text}" for chunk in chunks
        )

        prompt = f"""You are a document question-answering assistant.
Answer the question using only the supplied context.
If the context does not contain the answer, say:
"I don't know based on the available documents."
Do not invent facts or use outside knowledge.

Context:
{context}

Question:
{question}

Answer:"""

        try:
            answer = generate(prompt)
        except AIServiceError:
            return Response(
                {
                    "detail": (
                        "The AI service is temporarily unavailable. "
                        "Please try again later."
                    )
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        response_data = {
            "answer": answer,
            "sources": [
                {
                    "document_title": chunk.document.title,
                    "chunk_index": chunk.chunk_index,
                }
                for chunk in chunks
            ],
        }

        response_serializer = QueryResponseSerializer(data=response_data)
        response_serializer.is_valid(raise_exception=True)

        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK,
        )
