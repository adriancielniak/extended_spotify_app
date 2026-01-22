from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Custom User model for Enhanced Spotify App
    """
    email = models.EmailField(unique=True)
    spotify_user_id = models.CharField(max_length=255, blank=True, null=True)
    spotify_access_token = models.TextField(blank=True, null=True)
    spotify_refresh_token = models.TextField(blank=True, null=True)
    spotify_token_expires_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.username
