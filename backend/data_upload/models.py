from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class SpotifyDataUpload(models.Model):
    """
    Model to track Spotify data uploads
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploads')
    file_path = models.CharField(max_length=500)
    file_size = models.BigIntegerField()
    upload_date = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
    processing_status = models.CharField(max_length=50, default='pending')
    
    class Meta:
        ordering = ['-upload_date']
    
    def __str__(self):
        return f"{self.user.username} - {self.upload_date}"


class StreamingHistory(models.Model):
    """
    Model to store individual streaming records from Spotify data
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='streaming_history')
    upload = models.ForeignKey(SpotifyDataUpload, on_delete=models.CASCADE, related_name='records')
    
    # Spotify data fields
    ts = models.DateTimeField()  # timestamp
    username = models.CharField(max_length=255)
    platform = models.CharField(max_length=100, blank=True, null=True)
    ms_played = models.IntegerField()  # milliseconds played
    conn_country = models.CharField(max_length=10, blank=True, null=True)
    ip_addr_decrypted = models.GenericIPAddressField(blank=True, null=True)
    user_agent_decrypted = models.TextField(blank=True, null=True)
    
    # Track info
    master_metadata_track_name = models.CharField(max_length=500, blank=True, null=True)
    master_metadata_album_artist_name = models.CharField(max_length=500, blank=True, null=True)
    master_metadata_album_album_name = models.CharField(max_length=500, blank=True, null=True)
    spotify_track_uri = models.CharField(max_length=255, blank=True, null=True)
    
    # Additional metadata
    episode_name = models.CharField(max_length=500, blank=True, null=True)
    episode_show_name = models.CharField(max_length=500, blank=True, null=True)
    spotify_episode_uri = models.CharField(max_length=255, blank=True, null=True)
    
    reason_start = models.CharField(max_length=100, blank=True, null=True)
    reason_end = models.CharField(max_length=100, blank=True, null=True)
    shuffle = models.BooleanField(default=False, null=True, blank=True)
    skipped = models.BooleanField(default=False, null=True, blank=True)
    offline = models.BooleanField(default=False, null=True, blank=True)
    offline_timestamp = models.BigIntegerField(blank=True, null=True)
    incognito_mode = models.BooleanField(default=False, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-ts']
        indexes = [
            models.Index(fields=['user', 'ts']),
            models.Index(fields=['master_metadata_track_name']),
        ]
    
    def __str__(self):
        return f"{self.master_metadata_track_name} - {self.ts}"
