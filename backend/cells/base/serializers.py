from rest_framework import serializers


class FileUploadSerializer(serializers.Serializer):
    session_id = serializers.CharField(max_length=255, required=True)
    files = serializers.ListField(
        child=serializers.FileField(),
        allow_empty=False,
        write_only=True
    )


class SessionIdSerializer(serializers.Serializer):
    session_id = serializers.CharField(max_length=255, required=True)
