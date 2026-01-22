# Przykładowe dane testowe

## Struktura danych Spotify (dla testów)

Pliki JSON w ZIP powinny mieć następującą strukturę:

### Streaming_History.json

```json
[
  {
    "ts": "2023-12-01T10:30:00Z",
    "username": "testuser",
    "platform": "Android OS 14",
    "ms_played": 240000,
    "conn_country": "PL",
    "ip_addr_decrypted": "192.168.1.1",
    "user_agent_decrypted": "Spotify/8.7.0",
    "master_metadata_track_name": "Bohemian Rhapsody",
    "master_metadata_album_artist_name": "Queen",
    "master_metadata_album_album_name": "A Night at the Opera",
    "spotify_track_uri": "spotify:track:4u7EnebtmKWzUH433cf5Qv",
    "episode_name": null,
    "episode_show_name": null,
    "spotify_episode_uri": null,
    "reason_start": "trackdone",
    "reason_end": "trackdone",
    "shuffle": false,
    "skipped": false,
    "offline": false,
    "offline_timestamp": null,
    "incognito_mode": false
  }
]
```

## Tworzenie testowego ZIP

```bash
# Utwórz katalog testowy
mkdir test_spotify_data
cd test_spotify_data

# Utwórz plik JSON z danymi testowymi
cat > Streaming_History_0.json << 'EOF'
[
  {
    "ts": "2023-12-01T10:30:00Z",
    "username": "testuser",
    "platform": "Android OS 14",
    "ms_played": 240000,
    "conn_country": "PL",
    "ip_addr_decrypted": "192.168.1.1",
    "user_agent_decrypted": "Spotify/8.7.0",
    "master_metadata_track_name": "Bohemian Rhapsody",
    "master_metadata_album_artist_name": "Queen",
    "master_metadata_album_album_name": "A Night at the Opera",
    "spotify_track_uri": "spotify:track:4u7EnebtmKWzUH433cf5Qv",
    "episode_name": null,
    "episode_show_name": null,
    "spotify_episode_uri": null,
    "reason_start": "trackdone",
    "reason_end": "trackdone",
    "shuffle": false,
    "skipped": false,
    "offline": false,
    "offline_timestamp": null,
    "incognito_mode": false
  },
  {
    "ts": "2023-12-01T11:00:00Z",
    "username": "testuser",
    "platform": "Android OS 14",
    "ms_played": 180000,
    "conn_country": "PL",
    "master_metadata_track_name": "Stairway to Heaven",
    "master_metadata_album_artist_name": "Led Zeppelin",
    "master_metadata_album_album_name": "Led Zeppelin IV",
    "spotify_track_uri": "spotify:track:5CQ30WqJwcep0pYcV4AMNc",
    "reason_start": "clickrow",
    "reason_end": "trackdone",
    "shuffle": false,
    "skipped": false,
    "offline": false,
    "incognito_mode": false
  }
]
EOF

# Utwórz ZIP
zip -r ../test_spotify_data.zip .
cd ..
rm -rf test_spotify_data

echo "✅ Utworzono test_spotify_data.zip"
```

## Testowe konto użytkownika

```
Username: testuser
Email: test@example.com
Password: testpass123
```

## Weryfikacja po uploaderze

Po przesłaniu danych testowych, sprawdź:

1. Dashboard powinien pokazać:
   - 2 nagrania
   - ~0.12 godziny słuchania (240000 + 180000 ms = 420000 ms = 7 min)

2. Admin Panel (http://localhost:8000/admin):
   - SpotifyDataUpload: 1 wpis (status: completed)
   - StreamingHistory: 2 wpisy

3. API Response (/api/upload/stats/):
```json
{
  "total_records": 2,
  "total_hours_played": 0.12,
  "total_milliseconds": 420000
}
```
