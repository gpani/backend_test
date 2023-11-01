from rest_framework import serializers


class FileUploadSerializer(serializers.Serializer):
    customers = serializers.FileField()
    products = serializers.FileField()
    orders = serializers.FileField()
