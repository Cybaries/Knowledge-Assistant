
from rest_framework import serializers


class QueryRequestSerializer(serializers.Serializer):
    question = serializers.CharField(
        required=True,
        allow_blank=False,
        trim_whitespace=True,
    )
    document_id = serializers.IntegerField(
        required=False,
        min_value=1,
    )


class QuerySourceSerializer(serializers.Serializer):
    document_title = serializers.CharField()
    chunk_index = serializers.IntegerField()


class QueryResponseSerializer(serializers.Serializer):
    answer = serializers.CharField()
    sources = QuerySourceSerializer(many=True)