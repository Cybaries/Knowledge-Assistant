from rest_framework import permissions, viewsets

from rag.pipeline import process_document

from .models import Document
from .serializers import DocumentSerializer


class DocumentViewSet(viewsets.ModelViewSet):
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Document.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        document = serializer.save(owner=self.request.user)
        process_document(document.pk)
