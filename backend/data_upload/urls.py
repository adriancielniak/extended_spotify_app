from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload_spotify_data, name='upload_spotify_data'),
    path('list/', views.get_uploads, name='get_uploads'),
    path('stats/', views.get_streaming_stats, name='get_streaming_stats'),
]
