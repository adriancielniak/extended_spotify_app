from django.contrib import admin
from .models import SpotifyDataUpload, StreamingHistory


@admin.register(SpotifyDataUpload)
class SpotifyDataUploadAdmin(admin.ModelAdmin):
    list_display = ('user', 'upload_date', 'file_size', 'processed', 'processing_status')
    list_filter = ('processed', 'processing_status', 'upload_date')
    search_fields = ('user__username',)


@admin.register(StreamingHistory)
class StreamingHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'master_metadata_track_name', 'master_metadata_album_artist_name', 'ts', 'ms_played')
    list_filter = ('ts', 'conn_country', 'platform')
    search_fields = ('master_metadata_track_name', 'master_metadata_album_artist_name', 'user__username')
    date_hierarchy = 'ts'
