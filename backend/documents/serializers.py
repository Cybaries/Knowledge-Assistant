from pathlib import Path

from rest_framework import serializers

from .models import Document


class DocumentSerializer(serializers.ModelSerializer):
    ALLOWED_EXTENSIONS = {
        ".pdf",
        ".txt",
        ".docx",
    }

    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

    class Meta:
        model = Document
        fields = (
            "id",
            "title",
            "file",
            "owner",
            "uploaded_at",
            "status",
        )
        read_only_fields = (
            "id",
            "owner",
            "uploaded_at",
            "status",
        )

    def validate_file(self, file):
        extension = Path(file.name).suffix.lower()

        if extension not in self.ALLOWED_EXTENSIONS:
            raise serializers.ValidationError(
                "Unsupported file type. " "Allowed types: PDF, TXT, DOCX."
            )

        if file.size > self.MAX_FILE_SIZE:
            raise serializers.ValidationError("File size must not exceed 10 MB.")

        return file
