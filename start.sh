#!/bin/bash

echo "🎵 Enhanced Spotify App - Setup Script"
echo "======================================="
echo ""

# Sprawdź czy Docker jest zainstalowany
if ! command -v docker &> /dev/null; then
    echo "❌ Docker nie jest zainstalowany. Zainstaluj Docker Desktop."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose nie jest zainstalowany."
    exit 1
fi

echo "✅ Docker i Docker Compose są zainstalowane"
echo ""

# Wybór trybu
echo "Wybierz tryb uruchomienia:"
echo "1) Development (backend w Docker, frontend lokalnie)"
echo "2) Production (wszystko w Docker)"
read -p "Wybór (1/2): " mode

if [ "$mode" == "1" ]; then
    echo ""
    echo "🚀 Uruchamiam tryb development..."
    echo ""
    
    # Uruchom backend i bazę danych
    docker-compose -f docker-compose.dev.yml up -d --build
    
    echo ""
    echo "✅ Backend i baza danych uruchomione!"
    echo ""
    echo "📊 Backend: http://localhost:8000"
    echo "📊 Admin Panel: http://localhost:8000/admin"
    echo "📊 API Docs: http://localhost:8000/api/docs/"
    echo ""
    echo "Aby uruchomić frontend lokalnie:"
    echo "  cd frontend"
    echo "  npm install"
    echo "  npm run dev"
    echo ""
    echo "Frontend będzie dostępny na: http://localhost:5173"
    
elif [ "$mode" == "2" ]; then
    echo ""
    echo "🚀 Uruchamiam tryb production..."
    echo ""
    
    # Uruchom wszystko
    docker-compose up -d --build
    
    echo ""
    echo "✅ Aplikacja uruchomiona!"
    echo ""
    echo "🌐 Frontend: http://localhost"
    echo "📊 Backend API: http://localhost:8000"
    echo "📊 Admin Panel: http://localhost:8000/admin"
    echo "📊 API Docs: http://localhost:8000/api/docs/"
    
else
    echo "❌ Nieprawidłowy wybór"
    exit 1
fi

echo ""
echo "📝 Aby utworzyć superusera dla Django Admin:"
echo "   docker-compose exec backend python manage.py createsuperuser"
echo ""
echo "📝 Aby zobaczyć logi:"
echo "   docker-compose logs -f"
echo ""
echo "📝 Aby zatrzymać aplikację:"
echo "   docker-compose down"
echo ""
