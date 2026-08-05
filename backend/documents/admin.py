from django.contrib import admin

from .models import Document, DocumentChunk


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "owner",
        "status",
        "uploaded_at",
    )

    search_fields = (
        "title",
        "owner__username",
    )

    list_filter = (
        "status",
        "uploaded_at",
    )


@admin.register(DocumentChunk)
class DocumentChunkAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "document",
        "created_at",
    )