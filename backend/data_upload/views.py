import os
import json
import zipfile
import requests
from datetime import datetime
from django.conf import settings
from django.db import models
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from .models import SpotifyDataUpload, StreamingHistory
from .serializers import SpotifyDataUploadSerializer


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload_spotify_data(request):
    """
    Upload Spotify data ZIP file
    """
    if 'file' not in request.FILES:
        return Response(
            {'error': 'No file provided'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    uploaded_file = request.FILES['file']
    
    # Validate file type
    if not uploaded_file.name.endswith('.zip'):
        return Response(
            {'error': 'File must be a ZIP archive'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Create user-specific upload directory
    user_upload_dir = os.path.join(settings.UPLOAD_DIR, str(request.user.id))
    os.makedirs(user_upload_dir, exist_ok=True)
    
    # Save uploaded file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    file_path = os.path.join(user_upload_dir, f'spotify_data_{timestamp}.zip')
    
    with open(file_path, 'wb+') as destination:
        for chunk in uploaded_file.chunks():
            destination.write(chunk)
    
    # Create upload record
    upload = SpotifyDataUpload.objects.create(
        user=request.user,
        file_path=file_path,
        file_size=uploaded_file.size,
        processing_status='uploaded'
    )
    
    # Process the ZIP file
    try:
        process_spotify_zip(upload, file_path)
        upload.processed = True
        upload.processing_status = 'completed'
        upload.save()
        
        return Response(
            {
                'message': 'File uploaded and processed successfully',
                'upload': SpotifyDataUploadSerializer(upload).data
            },
            status=status.HTTP_201_CREATED
        )
    except Exception as e:
        upload.processing_status = 'failed'
        upload.save()
        return Response(
            {'error': f'Error processing file: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def process_spotify_zip(upload, file_path):
    """
    Process Spotify data ZIP file and extract streaming history
    """
    extract_dir = file_path.replace('.zip', '_extracted')
    os.makedirs(extract_dir, exist_ok=True)
    
    # Extract ZIP file
    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)
    
    # Find and process streaming history JSON files
    for root, dirs, files in os.walk(extract_dir):
        for file in files:
            if file.startswith('Streaming_History') and file.endswith('.json'):
                json_path = os.path.join(root, file)
                process_streaming_history_file(upload, json_path)


def process_streaming_history_file(upload, json_path):
    """
    Process individual streaming history JSON file
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    records = []
    for item in data:
        # Parse timestamp
        ts = datetime.fromisoformat(item.get('ts', '').replace('Z', '+00:00'))
        
        # Create streaming history record
        record = StreamingHistory(
            user=upload.user,
            upload=upload,
            ts=ts,
            username=item.get('username', ''),
            platform=item.get('platform', ''),
            ms_played=item.get('ms_played', 0),
            conn_country=item.get('conn_country', ''),
            ip_addr_decrypted=item.get('ip_addr_decrypted', None),
            user_agent_decrypted=item.get('user_agent_decrypted', ''),
            master_metadata_track_name=item.get('master_metadata_track_name', ''),
            master_metadata_album_artist_name=item.get('master_metadata_album_artist_name', ''),
            master_metadata_album_album_name=item.get('master_metadata_album_album_name', ''),
            spotify_track_uri=item.get('spotify_track_uri', ''),
            episode_name=item.get('episode_name', ''),
            episode_show_name=item.get('episode_show_name', ''),
            spotify_episode_uri=item.get('spotify_episode_uri', ''),
            reason_start=item.get('reason_start', ''),
            reason_end=item.get('reason_end', ''),
            shuffle=item.get('shuffle', False),
            skipped=item.get('skipped', False),
            offline=item.get('offline', False),
            offline_timestamp=item.get('offline_timestamp', None),
            incognito_mode=item.get('incognito_mode', False),
        )
        records.append(record)
    
    # Bulk create records for better performance
    StreamingHistory.objects.bulk_create(records, batch_size=1000)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_uploads(request):
    """
    Get all uploads for the current user
    """
    uploads = SpotifyDataUpload.objects.filter(user=request.user)
    serializer = SpotifyDataUploadSerializer(uploads, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_streaming_stats(request):
    """
    Get basic streaming statistics for the user
    """
    total_records = StreamingHistory.objects.filter(user=request.user).count()
    total_ms_played = StreamingHistory.objects.filter(user=request.user).aggregate(
        total=models.Sum('ms_played')
    )['total'] or 0
    
    total_hours = total_ms_played / (1000 * 60 * 60)
    
    return Response({
        'total_records': total_records,
        'total_hours_played': round(total_hours, 2),
        'total_milliseconds': total_ms_played
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_top_tracks(request):
    """
    Get top 50 most played tracks for the user
    Supports date range filtering via query parameters:
    - start_date: Start date in YYYY-MM-DD format
    - end_date: End date in YYYY-MM-DD format
    """
    from datetime import timedelta
    
    # Get date range filters
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    
    # Build base query
    query = StreamingHistory.objects.filter(
        user=request.user,
        master_metadata_track_name__isnull=False  # Exclude null track names
    )
    
    # Apply date range filter
    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            query = query.filter(ts__gte=start_date)
        except ValueError:
            return Response(
                {'error': 'Invalid start_date format. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            # Include the entire end date (until 23:59:59)
            end_date = end_date + timedelta(days=1)
            query = query.filter(ts__lt=end_date)
        except ValueError:
            return Response(
                {'error': 'Invalid end_date format. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    # Group by track name, artist, and album, then count plays
    top_tracks = (
        query
        .values(
            'master_metadata_track_name',
            'master_metadata_album_artist_name',
            'master_metadata_album_album_name'
        )
        .annotate(
            play_count=models.Count('id'),
            total_ms_played=models.Sum('ms_played')
        )
        .order_by('-play_count')[:50]
    )
    
    # Convert to list and add ranking
    result = []
    for idx, track in enumerate(top_tracks, start=1):
        total_hours = track['total_ms_played'] / (1000 * 60 * 60)
        result.append({
            'rank': idx,
            'track_name': track['master_metadata_track_name'],
            'artist_name': track['master_metadata_album_artist_name'],
            'album_name': track['master_metadata_album_album_name'],
            'play_count': track['play_count'],
            'total_hours_played': round(total_hours, 2)
        })
    
    return Response(result)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def generate_custom_playlist(request):
    """
    Generate custom playlist with specified parameters
    Query parameters:
    - start_date: Start date in YYYY-MM-DD format
    - end_date: End date in YYYY-MM-DD format
    - limit: Number of tracks (default 50, max 200)
    """
    from datetime import timedelta
    
    # Get parameters
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    limit = request.GET.get('limit', '50')
    
    # Validate and parse limit
    try:
        limit = int(limit)
        if limit < 1:
            limit = 1
        elif limit > 200:
            limit = 200
    except ValueError:
        return Response(
            {'error': 'Invalid limit. Must be a number between 1 and 200'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Build base query
    query = StreamingHistory.objects.filter(
        user=request.user,
        master_metadata_track_name__isnull=False
    )
    
    # Apply date range filter
    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            query = query.filter(ts__gte=start_date)
        except ValueError:
            return Response(
                {'error': 'Invalid start_date format. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            end_date = end_date + timedelta(days=1)
            query = query.filter(ts__lt=end_date)
        except ValueError:
            return Response(
                {'error': 'Invalid end_date format. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    # Group and get top tracks
    top_tracks = (
        query
        .values(
            'master_metadata_track_name',
            'master_metadata_album_artist_name',
            'master_metadata_album_album_name'
        )
        .annotate(
            play_count=models.Count('id'),
            total_ms_played=models.Sum('ms_played')
        )
        .order_by('-play_count')[:limit]
    )
    
    # Convert to list
    tracks_list = list(top_tracks)
    actual_count = len(tracks_list)
    
    # Add ranking
    result = []
    for idx, track in enumerate(tracks_list, start=1):
        total_hours = track['total_ms_played'] / (1000 * 60 * 60)
        result.append({
            'rank': idx,
            'track_name': track['master_metadata_track_name'],
            'artist_name': track['master_metadata_album_artist_name'],
            'album_name': track['master_metadata_album_album_name'],
            'play_count': track['play_count'],
            'total_hours_played': round(total_hours, 2)
        })
    
    return Response({
        'tracks': result,
        'requested_count': limit,
        'actual_count': actual_count,
        'message': f'Found {actual_count} out of {limit} requested tracks' if actual_count < limit else None
    })


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_all_streaming_data(request):
    """
    Delete all streaming data and uploads for the authenticated user
    """
    try:
        # Count records before deletion
        streaming_count = StreamingHistory.objects.filter(user=request.user).count()
        upload_count = SpotifyDataUpload.objects.filter(user=request.user).count()
        
        # Delete all streaming history
        StreamingHistory.objects.filter(user=request.user).delete()
        
        # Delete all upload records
        SpotifyDataUpload.objects.filter(user=request.user).delete()
        
        return Response({
            'success': True,
            'message': 'All data deleted successfully',
            'deleted_streaming_records': streaming_count,
            'deleted_uploads': upload_count
        })
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    # Format the response
    tracks_data = []
    for idx, track in enumerate(top_tracks, 1):
        tracks_data.append({
            'rank': idx,
            'track_name': track['master_metadata_track_name'],
            'artist_name': track['master_metadata_album_artist_name'] or 'Unknown Artist',
            'album_name': track['master_metadata_album_album_name'] or 'Unknown Album',
            'play_count': track['play_count'],
            'total_hours_played': round(track['total_ms_played'] / (1000 * 60 * 60), 2),
            'spotify_track_uri': None  # Will be populated if available
        })
    
    return Response(tracks_data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_spotify_playlist(request):
    """
    Create a Spotify playlist from top 50 tracks
    """
    user = request.user
    
    # Check if user has connected Spotify
    if not user.spotify_access_token or not user.spotify_user_id:
        return Response(
            {'error': 'Spotify account not connected. Please connect your Spotify account first.'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    # Check if token is expired
    if user.spotify_token_expires_at and datetime.now() >= user.spotify_token_expires_at.replace(tzinfo=None):
        return Response(
            {'error': 'Spotify token expired. Please reconnect your Spotify account.'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    access_token = user.spotify_access_token
    spotify_user_id = user.spotify_user_id
    
    # Get top tracks with Spotify URIs
    top_tracks = (
        StreamingHistory.objects
        .filter(
            user=request.user,
            master_metadata_track_name__isnull=False,
            spotify_track_uri__isnull=False  # Only tracks with valid Spotify URIs
        )
        .values(
            'master_metadata_track_name',
            'master_metadata_album_artist_name',
            'spotify_track_uri'
        )
        .annotate(
            play_count=models.Count('id')
        )
        .order_by('-play_count')[:50]
    )
    
    if not top_tracks:
        return Response(
            {'error': 'No tracks with Spotify URIs found in your data.'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Extract unique track URIs
    track_uris = list(set([track['spotify_track_uri'] for track in top_tracks]))
    
    # Create playlist
    playlist_name = f"Top 50 - {datetime.now().strftime('%Y-%m-%d')}"
    playlist_description = f"Your top 50 most played tracks generated by Enhanced Spotify App"
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # Create empty playlist
    create_playlist_url = f'https://api.spotify.com/v1/users/{spotify_user_id}/playlists'
    create_data = {
        'name': playlist_name,
        'description': playlist_description,
        'public': False
    }
    
    create_response = requests.post(create_playlist_url, headers=headers, json=create_data)
    
    if create_response.status_code not in [200, 201]:
        return Response(
            {'error': 'Failed to create playlist on Spotify', 'details': create_response.json()},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    playlist_data = create_response.json()
    playlist_id = playlist_data['id']
    playlist_url = playlist_data['external_urls']['spotify']
    
    # Add tracks to playlist (Spotify allows max 100 tracks per request)
    add_tracks_url = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'
    
    # Add tracks in batches of 100
    for i in range(0, len(track_uris), 100):
        batch = track_uris[i:i+100]
        add_data = {'uris': batch}
        
        add_response = requests.post(add_tracks_url, headers=headers, json=add_data)
        
        if add_response.status_code not in [200, 201]:
            # Playlist created but tracks not added - still return success with warning
            return Response({
                'success': True,
                'warning': 'Playlist created but some tracks could not be added',
                'playlist_id': playlist_id,
                'playlist_url': playlist_url,
                'tracks_added': i
            })
    
    return Response({
        'success': True,
        'playlist_id': playlist_id,
        'playlist_url': playlist_url,
        'playlist_name': playlist_name,
        'tracks_added': len(track_uris)
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_monthly_listening_stats(request):
    """
    Get monthly listening statistics showing total hours listened per month
    """
    # Get all streaming history for the user
    streaming_data = StreamingHistory.objects.filter(
        user=request.user,
        ts__isnull=False
    ).values(
        'ts', 'ms_played'
    ).order_by('ts')
    
    if not streaming_data:
        return Response([])
    
    # Group by year-month
    from collections import defaultdict
    monthly_stats = defaultdict(lambda: {'total_ms': 0, 'play_count': 0})
    
    for record in streaming_data:
        # Format: YYYY-MM
        month_key = record['ts'].strftime('%Y-%m')
        monthly_stats[month_key]['total_ms'] += record['ms_played']
        monthly_stats[month_key]['play_count'] += 1
    
    # Convert to list and calculate hours
    result = []
    for month_key in sorted(monthly_stats.keys()):
        stats = monthly_stats[month_key]
        total_hours = stats['total_ms'] / (1000 * 60 * 60)
        
        # Parse month for better display
        year, month = month_key.split('-')
        month_names = {
            '01': 'Styczeń', '02': 'Luty', '03': 'Marzec', '04': 'Kwiecień',
            '05': 'Maj', '06': 'Czerwiec', '07': 'Lipiec', '08': 'Sierpień',
            '09': 'Wrzesień', '10': 'Październik', '11': 'Listopad', '12': 'Grudzień'
        }
        
        result.append({
            'month': month_key,
            'month_label': f'{month_names[month]} {year}',
            'total_hours': round(total_hours, 2),
            'play_count': stats['play_count']
        })
    
    return Response(result)
