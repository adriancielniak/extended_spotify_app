from django.urls import path
from . import views, spotify_views

urlpatterns = [
    path('csrf/', views.get_csrf_token, name='csrf_token'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('me/', views.current_user, name='current_user'),
    
    # Spotify OAuth
    path('spotify/auth-url/', spotify_views.spotify_auth_url, name='spotify_auth_url'),
    path('spotify/callback/', spotify_views.spotify_callback, name='spotify_callback'),
    path('spotify/exchange-code/', spotify_views.exchange_spotify_code, name='exchange_spotify_code'),
    path('spotify/status/', spotify_views.spotify_connection_status, name='spotify_connection_status'),
    path('spotify/disconnect/', spotify_views.disconnect_spotify, name='disconnect_spotify'),
]
