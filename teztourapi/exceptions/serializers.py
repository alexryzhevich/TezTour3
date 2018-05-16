from rest_framework import serializers


class ErrorMessageSerializer(serializers.Serializer):
    code = serializers.IntegerField()
    message = serializers.CharField()
