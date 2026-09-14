from django.db import migrations, models


def populate_chunk_indexes(apps, schema_editor):
    DocumentChunk = apps.get_model("documents", "DocumentChunk")

    document_ids = (
        DocumentChunk.objects.values_list("document_id", flat=True)
        .distinct()
    )

    for document_id in document_ids:
        chunks = DocumentChunk.objects.filter(
            document_id=document_id
        ).order_by("created_at", "pk")

        for index, chunk in enumerate(chunks):
            chunk.chunk_index = index
            chunk.save(update_fields=["chunk_index"])


class Migration(migrations.Migration):

    dependencies = [
        ("documents", "0004_alter_documentchunk_embedding"),
    ]

    operations = [
        migrations.AddField(
            model_name="documentchunk",
            name="chunk_index",
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.RunPython(
            populate_chunk_indexes,
            migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name="documentchunk",
            name="chunk_index",
            field=models.PositiveIntegerField(),
        ),
    ]