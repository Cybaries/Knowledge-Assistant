from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

class DocumentStatus(models.TextChoices):
    UPLOADING = "UPLOADING", "Uploading"
    PROCESSING = "PROCESSING", "Processing"
    READY = "READY", "Ready"
    FAILED = "FAILED", "Failed"
class Document(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to="documents/")
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="documents"
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=DocumentStatus.choices,
        default=DocumentStatus.UPLOADING,
    )

    def __str__(self):
        return self.title
    class Meta:
     ordering = ["-uploaded_at"]

class DocumentChunk(models.Model):
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name="chunks"
    )
    text = models.TextField()
    embedding = models.JSONField(
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.document.title} - Chunk {self.pk}"
    class Meta:
        ordering = ["created_at"]

    
