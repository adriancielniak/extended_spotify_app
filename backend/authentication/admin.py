from django.contrib import admin
from django.contrib.auth import get_user_model

User = get_user_model()

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'spotify_user_id', 'created_at')
    search_fields = ('username', 'email')
    list_filter = ('created_at',)
