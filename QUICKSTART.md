# 🚀 Szybki Start

## Najszybszy sposób uruchomienia (Rekomendowany)

### Krok 1: Uruchom skrypt setupu

```bash
./start.sh
```

Wybierz opcję **1** dla developmentu lub **2** dla produkcji.

### Krok 2: Utwórz superusera (opcjonalnie)

```bash
docker-compose exec backend python manage.py createsuperuser
```

### Krok 3: Otwórz aplikację

- **Frontend:** http://localhost:5173 (development) lub http://localhost (production)
- **Backend API:** http://localhost:8000
- **Admin Panel:** http://localhost:8000/admin
- **API Docs:** http://localhost:8000/api/docs/

## Alternatywny sposób (ręczny)

### Development

```bash
# Uruchom backend i bazę danych
docker-compose -f docker-compose.dev.yml up -d --build

# W nowym terminalu uruchom frontend
cd frontend
npm install
npm run dev
```

### Production

```bash
# Uruchom wszystko
docker-compose up -d --build
```

## Pierwsze kroki w aplikacji

1. **Zarejestruj się** - http://localhost:5173/register
2. **Pobierz dane ze Spotify** - https://www.spotify.com/pl/account/privacy/
3. **Prześlij ZIP** - Zaloguj się i przejdź do Upload
4. **Zobacz statystyki** - Dashboard

## Zatrzymanie aplikacji

```bash
docker-compose down
```

## Problemy?

Sprawdź logi:
```bash
docker-compose logs -f backend
```

Więcej informacji w [README.md](README.md)
