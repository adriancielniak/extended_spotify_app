from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload_spotify_data, name='upload_spotify_data'),
    path('list/', views.get_uploads, name='get_uploads'),
    path('stats/', views.get_streaming_stats, name='get_streaming_stats'),
    path('top-tracks/', views.get_top_tracks, name='get_top_tracks'),
    path('generate-playlist/', views.generate_custom_playlist, name='generate_custom_playlist'),
    path('monthly-stats/', views.get_monthly_listening_stats, name='get_monthly_listening_stats'),
    path('delete-all/', views.delete_all_streaming_data, name='delete_all_streaming_data'),
    path('create-playlist/', views.create_spotify_playlist, name='create_spotify_playlist'),
]
