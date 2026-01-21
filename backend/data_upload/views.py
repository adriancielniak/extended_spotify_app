import os
import json
import zipfile
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
