from rest_framework import serializers
from .models import SpotifyDataUpload, StreamingHistory


class SpotifyDataUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpotifyDataUpload
        fields = ('id', 'file_path', 'file_size', 'upload_date', 'processed', 'processing_status')
        read_only_fields = ('id', 'upload_date', 'processed', 'processing_status')


class StreamingHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = StreamingHistory
        fields = '__all__'
        read_only_fields = ('id', 'created_at')
