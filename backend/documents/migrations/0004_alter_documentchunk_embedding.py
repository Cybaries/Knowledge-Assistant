from django.db import migrations
from pgvector.django import VectorField


class Migration(migrations.Migration):

    dependencies = [
        ("documents", "0003_enable_pgvector"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="documentchunk",
            name="embedding",
        ),
        migrations.AddField(
            model_name="documentchunk",
            name="embedding",
            field=VectorField(
                dimensions=384,
                null=True,
                blank=True,
            ),
        ),
    ]