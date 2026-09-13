from django.db import migrations
from pgvector.django import VectorExtension


class Migration(migrations.Migration):

    dependencies = [
        ("documents", "0002_alter_document_options_document_status_documentchunk"),
    ]

    operations = [
        VectorExtension(),
    ]
