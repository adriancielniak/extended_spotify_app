# Enhanced Spotify App (ESA)

Aplikacja do analizy i wizualizacji danych Spotify z dodatkowymi funkcjami tworzenia playlist i map słuchania.

## 🛠️ Stack Technologiczny

- **Backend:** Django 5.0 + Django REST Framework
- **Frontend:** Vue 3 + Vite + Pinia
- **Baza danych:** PostgreSQL 15
- **Konteneryzacja:** Docker + Docker Compose

## 🚀 Instalacja i Uruchomienie

### Wymagania
- Docker Desktop (Docker Engine + Docker Compose)
- Node.js 20+ (tylko do developmentu bez Dockera)
- Python 3.11+ (tylko do developmentu bez Dockera)

### Szybki start z Dockerem (Rekomendowane)

#### Tryb development (z hot-reload backendu)

```bash
# Uruchom wszystkie serwisy
docker-compose -f docker-compose.dev.yml up --build

# Backend będzie dostępny na: http://localhost:8000
# Baza danych: localhost:5432
# Frontend uruchom lokalnie (patrz niżej)
```

#### Uruchom frontend lokalnie (development)

```bash
cd frontend
npm install
npm run dev
# Frontend: http://localhost:5173
```

#### Tryb produkcyjny (pełna aplikacja w Dockerze)

```bash
# Uruchom wszystkie serwisy (backend + frontend + database)
docker-compose up --build

# Frontend dostępny na: http://localhost (port 80)
# Backend API: http://localhost:8000
```

### Uruchomienie bez Dockera (opcjonalnie)

#### Backend

```bash
cd backend

# Utwórz środowisko wirtualne
python -m venv venv
source venv/bin/activate  # Linux/Mac
# lub
venv\Scripts\activate  # Windows

# Zainstaluj zależności
pip install -r requirements.txt

# Skonfiguruj bazę danych PostgreSQL lokalnie
# Edytuj backend/.env i ustaw DB_HOST=localhost

# Wykonaj migracje
python manage.py migrate

# Utwórz superusera (opcjonalnie)
python manage.py createsuperuser

# Uruchom serwer
python manage.py runserver
```

#### Frontend

```bash
cd frontend

# Zainstaluj zależności
npm install

# Uruchom dev server
npm run dev

# Build dla produkcji
npm run build
```

## 📝 Konfiguracja

### Zmienne środowiskowe Backend

Edytuj `backend/.env`:

```env
# Database
DB_NAME=spotify_db
DB_USER=spotify_user
DB_PASSWORD=spotify_pass
DB_HOST=db  # 'localhost' jeśli bez Dockera
DB_PORT=5432

# Django
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1,backend

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# Spotify API (opcjonalnie)
SPOTIFY_CLIENT_ID=
SPOTIFY_CLIENT_SECRET=
```

### Zmienne środowiskowe Frontend

Edytuj `frontend/.env`:

```env
VITE_API_URL=http://localhost:8000/api
```

## 🔧 Użytkowanie

### 1. Rejestracja konta

1. Otwórz aplikację w przeglądarce
2. Kliknij "Zarejestruj się"
3. Wypełnij formularz (nazwa użytkownika, email, hasło)

### 2. Pobierz dane ze Spotify

1. Przejdź do https://www.spotify.com/pl/account/privacy/
2. Przewiń do "Pobierz swoje dane"
3. Zaznacz "Rozszerzona historia streamingu"
4. Poczekaj na email z linkiem do pobrania (może potrwać kilka dni)
5. Pobierz plik ZIP

### 3. Prześlij dane do aplikacji

1. Zaloguj się do aplikacji
2. Przejdź do "Upload" lub "Dashboard"
3. Przeciągnij plik ZIP lub kliknij aby wybrać
4. Poczekaj na przetworzenie danych

### 4. Zobacz statystyki

1. Przejdź do "Dashboard"
2. Zobacz liczbę przesłuchanych utworów i godzin słuchania

## 🐳 Przydatne komendy Docker

```bash
# Uruchom wszystkie serwisy w tle
docker-compose up -d

# Zobacz logi
docker-compose logs -f

# Zobacz logi konkretnego serwisu
docker-compose logs -f backend

# Zatrzymaj wszystkie serwisy
docker-compose down

# Zatrzymaj i usuń voluminy (UWAGA: usunie dane z bazy!)
docker-compose down -v

# Rebuild konkretnego serwisu
docker-compose build backend

# Wykonaj komendę w kontenerze backendu
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser

# Wejdź do kontenera backendu
docker-compose exec backend sh

# Wejdź do bazy danych
docker-compose exec db psql -U spotify_user -d spotify_db
```

## 🗃️ Dostęp do Admin Panel Django

```bash
# Utwórz superusera
docker-compose exec backend python manage.py createsuperuser

# Dostęp do panelu:
# http://localhost:8000/admin
```

## 📊 API Endpoints

### Autoryzacja

- `POST /api/auth/register/` - Rejestracja użytkownika
- `POST /api/auth/login/` - Logowanie
- `POST /api/auth/logout/` - Wylogowanie
- `GET /api/auth/me/` - Informacje o zalogowanym użytkowniku

### Upload danych

- `POST /api/upload/` - Przesłanie pliku ZIP
- `GET /api/upload/list/` - Lista przesłanych plików
- `GET /api/upload/stats/` - Statystyki słuchania

### Dokumentacja API

- Swagger UI: http://localhost:8000/api/docs/
- OpenAPI Schema: http://localhost:8000/api/schema/

## 🔐 Bezpieczeństwo

**WAŻNE:** W środowisku produkcyjnym:

1. Zmień `SECRET_KEY` w `backend/.env`
2. Ustaw `DEBUG=False`
3. Skonfiguruj prawidłowe `ALLOWED_HOSTS`
4. Użyj silnych haseł do bazy danych
5. Skonfiguruj HTTPS
6. Regularnie aktualizuj zależności

## 🐛 Rozwiązywanie problemów

### Backend nie może połączyć się z bazą danych

```bash
# Sprawdź czy baza danych jest uruchomiona
docker-compose ps

# Sprawdź logi bazy danych
docker-compose logs db

# Restart bazy danych
docker-compose restart db
```

### Frontend nie może połączyć się z backendem

1. Sprawdź `frontend/.env` - czy `VITE_API_URL` jest poprawne
2. Sprawdź czy backend działa: http://localhost:8000
3. Sprawdź logi backendu: `docker-compose logs backend`

### Błędy CORS

1. Sprawdź `backend/.env` - `CORS_ALLOWED_ORIGINS`
2. Dodaj adres frontendu do listy
3. Restart backendu: `docker-compose restart backend`

