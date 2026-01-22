import requests
import base64
from datetime import datetime, timedelta
from urllib.parse import urlencode
from django.conf import settings
from django.shortcuts import redirect
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def spotify_auth_url(request):
    """
    Generate Spotify OAuth authorization URL
    """
    import json
    # Include user_id and redirect path in state to track user across OAuth flow
    redirect_to = request.GET.get('redirect_to', 'dashboard')
    state_data = {
        'user_id': request.user.id,
        'redirect_to': redirect_to
    }
    state = json.dumps(state_data)
    
    params = {
        'client_id': settings.SPOTIFY_CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': settings.SPOTIFY_REDIRECT_URI,
        'scope': settings.SPOTIFY_SCOPES,
        'state': state,
        'show_dialog': 'true'
    }
    
    auth_url = f"https://accounts.spotify.com/authorize?{urlencode(params)}"
    
    return Response({'auth_url': auth_url})


@api_view(['GET'])
@permission_classes([AllowAny])
def spotify_callback(request):
    """
    Handle Spotify OAuth callback - receives code from Spotify
    """
    import json
    code = request.GET.get('code')
    error = request.GET.get('error')
    state = request.GET.get('state')
    
    if error:
        return redirect(f'http://127.0.0.1/top-tracks?error={error}')
    
    if not code:
        return redirect('http://127.0.0.1/top-tracks?error=no_code')
    
    if not state:
        return redirect('http://127.0.0.1/top-tracks?error=no_state')
    
    # Parse state to get user_id and redirect path
    try:
        state_data = json.loads(state)
        user_id = state_data.get('user_id')
        redirect_to = state_data.get('redirect_to', 'dashboard')
    except (json.JSONDecodeError, AttributeError):
        return redirect('http://127.0.0.1/top-tracks?error=invalid_state')
    
    # Exchange code for access token
    token_url = 'https://accounts.spotify.com/api/token'
    
    credentials = f"{settings.SPOTIFY_CLIENT_ID}:{settings.SPOTIFY_CLIENT_SECRET}"
    b64_credentials = base64.b64encode(credentials.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {b64_credentials}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': settings.SPOTIFY_REDIRECT_URI
    }
    
    try:
        response = requests.post(token_url, headers=headers, data=data)
        
        if response.status_code != 200:
            return redirect(f'http://127.0.0.1/{redirect_to}?error=token_exchange_failed')
        
        token_data = response.json()
        access_token = token_data.get('access_token')
        refresh_token = token_data.get('refresh_token')
        expires_in = token_data.get('expires_in', 3600)
        
        # Get user profile to find Spotify user ID
        profile_url = 'https://api.spotify.com/v1/me'
        profile_headers = {
            'Authorization': f'Bearer {access_token}'
        }
        
        profile_response = requests.get(profile_url, headers=profile_headers)
        
        if profile_response.status_code != 200:
            return redirect(f'http://127.0.0.1/{redirect_to}?error=profile_fetch_failed')
        
        profile_data = profile_response.json()
        spotify_user_id = profile_data.get('id')
        
        # Save tokens to user model
        from authentication.models import User
        try:
            user = User.objects.get(id=int(user_id))
            user.spotify_user_id = spotify_user_id
            user.spotify_access_token = access_token
            user.spotify_refresh_token = refresh_token
            user.spotify_token_expires_at = datetime.now() + timedelta(seconds=expires_in)
            user.save()
        except (User.DoesNotExist, ValueError, TypeError):
            return redirect(f'http://127.0.0.1/{redirect_to}?error=user_not_found')
        
        # Redirect back to frontend
        return redirect(f'http://127.0.0.1/{redirect_to}?spotify_connected=true')
        
    except requests.exceptions.RequestException as e:
        return redirect(f'http://127.0.0.1/{redirect_to}?error=network_error')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def exchange_spotify_code(request):
    """
    Exchange authorization code for access token
    Frontend sends the code here after receiving it from Spotify
    """
    import json
    code = request.data.get('code')
    
    if not code:
        return Response(
            {'error': 'Authorization code is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Exchange code for access token
    token_url = 'https://accounts.spotify.com/api/token'
    
    credentials = f"{settings.SPOTIFY_CLIENT_ID}:{settings.SPOTIFY_CLIENT_SECRET}"
    b64_credentials = base64.b64encode(credentials.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {b64_credentials}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': settings.SPOTIFY_REDIRECT_URI
    }
    
    response = requests.post(token_url, headers=headers, data=data)
    
    if response.status_code != 200:
        return redirect(f'http://localhost:5173/top-tracks?error=token_exchange_failed')
    
    token_data = response.json()
    access_token = token_data.get('access_token')
    refresh_token = token_data.get('refresh_token')
    expires_in = token_data.get('expires_in', 3600)
    
    # Get user profile to find Spotify user ID
    profile_url = 'https://api.spotify.com/v1/me'
    profile_headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    profile_response = requests.get(profile_url, headers=profile_headers)
    
    if profile_response.status_code != 200:
        return redirect('http://localhost:5173/top-tracks?error=profile_fetch_failed')
    
    profile_data = profile_response.json()
    spotify_user_id = profile_data.get('id')
    
    # Get user from state parameter (user_id)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def exchange_spotify_code(request):
    """
    Exchange authorization code for access token
    Frontend sends the code here after receiving it from Spotify
    """
    import json
    code = request.data.get('code')
    
    if not code:
        return Response(
            {'error': 'Authorization code is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Exchange code for access token
    token_url = 'https://accounts.spotify.com/api/token'
    
    credentials = f"{settings.SPOTIFY_CLIENT_ID}:{settings.SPOTIFY_CLIENT_SECRET}"
    b64_credentials = base64.b64encode(credentials.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {b64_credentials}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': settings.SPOTIFY_REDIRECT_URI
    }
    
    try:
        response = requests.post(token_url, headers=headers, data=data)
        
        if response.status_code != 200:
            return Response(
                {'error': 'Failed to exchange code for token', 'details': response.text},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        token_data = response.json()
        access_token = token_data.get('access_token')
        refresh_token = token_data.get('refresh_token')
        expires_in = token_data.get('expires_in', 3600)
        
        # Get user profile to find Spotify user ID
        profile_url = 'https://api.spotify.com/v1/me'
        profile_headers = {
            'Authorization': f'Bearer {access_token}'
        }
        
        profile_response = requests.get(profile_url, headers=profile_headers)
        
        if profile_response.status_code != 200:
            return Response(
                {'error': 'Failed to fetch Spotify profile'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        profile_data = profile_response.json()
        spotify_user_id = profile_data.get('id')
        
        # Save tokens to user model
        user = request.user
        user.spotify_user_id = spotify_user_id
        user.spotify_access_token = access_token
        user.spotify_refresh_token = refresh_token
        user.spotify_token_expires_at = datetime.now() + timedelta(seconds=expires_in)
        user.save()
        
        return Response({
            'success': True,
            'spotify_user_id': spotify_user_id
        })
        
    except requests.exceptions.RequestException as e:
        return Response(
            {'error': 'Network error during token exchange', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def spotify_connection_status(request):
    """
    Check if user has connected Spotify account
    """
    user = request.user
    
    if not user.spotify_access_token or not user.spotify_token_expires_at:
        return Response({'connected': False})
    
    is_expired = datetime.now() >= user.spotify_token_expires_at.replace(tzinfo=None)
    
    return Response({
        'connected': True,
        'expired': is_expired,
        'spotify_user_id': user.spotify_user_id
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def disconnect_spotify(request):
    """
    Disconnect Spotify account (clear tokens from user model)
    """
    user = request.user
    user.spotify_access_token = None
    user.spotify_refresh_token = None
    user.spotify_user_id = None
    user.spotify_token_expires_at = None
    user.save()
    
    return Response({'status': 'disconnected'})
