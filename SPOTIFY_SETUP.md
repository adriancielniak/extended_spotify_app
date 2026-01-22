# INSTRUKCJE: Jak skonfigurować integrację ze Spotify API

## 1. Utwórz aplikację Spotify:
   - Przejdź do https://developer.spotify.com/dashboard
   - Zaloguj się swoim kontem Spotify
   - Kliknij "Create app"
   - Wypełnij formularz:
     * App name: Enhanced Spotify App
     * App description: Personal app for analyzing Spotify data
     * Redirect URI: http://localhost:8000/api/auth/spotify/callback/
     * Website: http://localhost:5173
     * API: Wybierz "Web API"
   - Zaakceptuj warunki i kliknij "Save"

## 2. Pobierz dane aplikacji:
   - W Dashboard kliknij na swoją aplikację
   - Kliknij "Settings"
   - Skopiuj "Client ID" i "Client Secret"

## 3. Zaktualizuj plik .env:
   Otwórz plik backend/.env i wypełnij:
   
   SPOTIFY_CLIENT_ID=twoj_client_id_tutaj
   SPOTIFY_CLIENT_SECRET=twoj_client_secret_tutaj
   SPOTIFY_REDIRECT_URI=http://localhost:8000/api/auth/spotify/callback/

## 4. Zrestartuj backend:
   docker-compose -f docker-compose.dev.yml restart backend

## 5. Gotowe!
   Teraz możesz połączyć swoje konto Spotify i tworzyć playlisty z Top 50 utworów.
