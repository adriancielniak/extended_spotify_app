# Analiza Wzorców Projektowych w Extended Spotify App

## Spis Treści
1. [Wprowadzenie](#wprowadzenie)
2. [Architektura Aplikacji](#architektura-aplikacji)
3. [Zidentyfikowane Wzorce Projektowe](#zidentyfikowane-wzorce-projektowe)
4. [Podsumowanie](#podsumowanie)

---

## Wprowadzenie

Extended Spotify App to aplikacja webowa umożliwiająca analizę historii słuchania muzyki z Spotify. Aplikacja składa się z:
- **Backend**: Django 5.0.1 + Django REST Framework + PostgreSQL
- **Frontend**: Vue 3 + Vite + Chart.js
- **Infrastruktura**: Docker, Nginx

---

## Architektura Aplikacji

```
┌─────────────────┐         ┌──────────────────┐         ┌──────────────┐
│   Vue 3 SPA     │ ◄─────► │   Nginx (proxy)  │ ◄─────► │  Django REST │
│   (Frontend)    │         │                  │         │   Framework  │
└─────────────────┘         └──────────────────┘         └──────┬───────┘
                                                                 │
                                                                 ▼
                                                         ┌──────────────┐
                                                         │ PostgreSQL   │
                                                         │   Database   │
                                                         └──────────────┘
```

---

## Zidentyfikowane Wzorce Projektowe

### 1. **Model View Controller (MVC)** / **Model-View-ViewModel (MVVM)**
**Kategoria**: Wzorce prezentacji internetowych

**Implementacja**:
- **Backend (MVC)**:
  - **Model**: `backend/data_upload/models.py` - `SpotifyDataUpload`, `StreamingHistory`
  - **View**: `backend/data_upload/views.py` - funkcje API view
  - **Controller**: Django REST Framework + routing
  
- **Frontend (MVVM)**:
  - **Model**: Store Pinia (`frontend/src/stores/auth.js`)
  - **View**: Komponenty Vue (`frontend/src/views/*.vue`)
  - **ViewModel**: Composition API + reactive state

**Przykład**:
```python
# Model
class StreamingHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ts = models.DateTimeField()
    ms_played = models.IntegerField()
    # ... inne pola

# View/Controller
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_top_tracks(request):
    query = StreamingHistory.objects.filter(user=request.user)
    # ... logika przetwarzania
    return Response(result)
```

---

### 2. **Repository**
**Kategoria**: Wzorce odwzorowań obiektów i relacyjnych metadanych

**Implementacja**: Django ORM działa jako warstwa Repository, enkapsulując dostęp do danych

**Przykład**:
```python
# Abstrakcja nad bazą danych - nie ma bezpośrednich zapytań SQL
query = StreamingHistory.objects.filter(
    user=request.user,
    master_metadata_track_name__isnull=False
).values('master_metadata_track_name', 'master_metadata_album_artist_name')
 .annotate(play_count=models.Count('id'))
 .order_by('-play_count')[:50]
```

**Korzyści**:
- Centralizacja logiki dostępu do danych
- Możliwość łatwej zmiany źródła danych
- Testowanie bez faktycznej bazy danych

---

### 3. **Data Mapper**
**Kategoria**: Wzorce architektury źródła danych

**Implementacja**: Django ORM mapuje obiekty Python na rekordy bazy danych, całkowicie oddzielając logikę domenową od struktury bazy

**Przykład**:
```python
# Model domeny jest niezależny od szczegółów bazy danych
class StreamingHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ts = models.DateTimeField()
    ms_played = models.IntegerField()
    
    # Django ORM automatycznie mapuje na tabele SQL
    # CREATE TABLE streaming_history (
    #     id SERIAL PRIMARY KEY,
    #     user_id INTEGER REFERENCES auth_user(id),
    #     ts TIMESTAMP,
    #     ms_played INTEGER
    # )
```

---

### 4. **Identity Field**
**Kategoria**: Wzorce struktury dla mapowania obiektowo-relacyjnego

**Implementacja**: Każdy model Django ma automatyczny klucz główny `id`

**Przykład**:
```python
class SpotifyDataUpload(models.Model):
    # Django automatycznie dodaje:
    # id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file_path = models.CharField(max_length=500)
```

---

### 5. **Foreign Key Mapping**
**Kategoria**: Wzorce struktury dla mapowania obiektowo-relacyjnego

**Implementacja**: Relacje między tabelami za pomocą kluczy obcych

**Przykład**:
```python
class StreamingHistory(models.Model):
    # Klucz obcy do użytkownika
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='streaming_history')
    
    # Klucz obcy do uploadu
    upload = models.ForeignKey(SpotifyDataUpload, on_delete=models.CASCADE, related_name='records')
```

**Opis**: `ForeignKey` mapuje relację 1:N między tabelami w bazie danych

---

### 6. **Gateway**
**Kategoria**: Wzorce podstawowe

**Implementacja**: 
- **API Gateway**: `frontend/src/services/api.js` - centralizuje komunikację z backendem
- **Service Classes**: `frontend/src/services/auth.js`, `frontend/src/services/upload.js`

**Przykład**:
```javascript
// api.js - Gateway do backendu
const api = axios.create({
  baseURL: '/api',
  withCredentials: true,
  headers: { 'Content-Type': 'application/json' }
})

// auth.js - Gateway dla operacji autentykacji
export const authService = {
  async login(username, password) {
    const response = await api.post('/auth/login/', { username, password })
    return response.data
  },
  async logout() {
    const response = await api.post('/auth/logout/')
    return response.data
  }
}
```

**Korzyści**:
- Pojedynczy punkt dostępu do zewnętrznych systemów
- Łatwe mockowanie w testach
- Centralizacja konfiguracji (CSRF, credentials)

---

### 7. **Service Layer**
**Kategoria**: Wzorce logiki dziedziny

**Implementacja**: 
- **Backend**: Funkcje view w `views.py` tworzą warstwę serwisową między API a logiką biznesową
- **Frontend**: Store Pinia + service classes

**Przykład**:
```python
# Backend Service Layer
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_monthly_listening_stats(request):
    """
    Service method: pobiera statystyki, przetwarza dane, zwraca wynik
    """
    # 1. Pobierz dane
    query = StreamingHistory.objects.filter(user=request.user)
    
    # 2. Agregacja i transformacja
    monthly_stats = query.annotate(
        month=TruncMonth('ts')
    ).values('month').annotate(
        play_count=Count('id'),
        total_hours=Sum('ms_played') / (1000 * 60 * 60)
    ).order_by('month')
    
    # 3. Formatowanie wyniku
    result = [{
        'month': format_month_polish(stat['month']),
        'play_count': stat['play_count'],
        'hours': round(stat['total_hours'], 2)
    } for stat in monthly_stats]
    
    return Response(result)
```

```javascript
// Frontend Service Layer (Pinia Store)
export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const isAuthenticated = ref(false)

  async function login(username, password) {
    // Warstwa serwisowa obsługuje cały proces logowania
    loading.value = true
    try {
      const userData = await authService.login(username, password)
      user.value = userData
      isAuthenticated.value = true
      return userData
    } catch (err) {
      error.value = err.response?.data?.error || 'Login failed'
      throw err
    } finally {
      loading.value = false
    }
  }
})
```

**Korzyści**:
- Oddzielenie logiki biznesowej od warstwy prezentacji
- Możliwość ponownego wykorzystania logiki
- Transakcyjność operacji

---

### 8. **Front Controller**
**Kategoria**: Wzorce prezentacji internetowych

**Implementacja**: 
- **Backend**: Django URL dispatcher (`urls.py`)
- **Frontend**: Vue Router (`frontend/src/router/index.js`)
- **Nginx**: Reverse proxy routing

**Przykład**:
```javascript
// Vue Router - Front Controller
const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/dashboard', component: Dashboard, meta: { requiresAuth: true } },
    { path: '/upload', component: Upload, meta: { requiresAuth: true } },
    { path: '/charts', component: Charts, meta: { requiresAuth: true } }
  ]
})

// Navigation Guard - centralna kontrola dostępu
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else {
    next()
  }
})
```

```python
# Django URL dispatcher
urlpatterns = [
    path('upload/', upload_spotify_data, name='upload'),
    path('top-tracks/', get_top_tracks, name='top-tracks'),
    path('monthly-stats/', get_monthly_listening_stats, name='monthly-stats'),
]
```

---

### 9. **Data Transfer Object (DTO)**
**Kategoria**: Wzorce dystrybucji

**Implementacja**: Django REST Framework Serializers

**Przykład**:
```python
class SpotifyDataUploadSerializer(serializers.ModelSerializer):
    """
    DTO - transferuje dane między warstwami bez logiki biznesowej
    """
    class Meta:
        model = SpotifyDataUpload
        fields = ('id', 'file_path', 'file_size', 'upload_date', 'processed', 'processing_status')
        read_only_fields = ('id', 'upload_date', 'processed', 'processing_status')

# Użycie
upload = SpotifyDataUpload.objects.create(...)
serialized_data = SpotifyDataUploadSerializer(upload).data
return Response(serialized_data)
```

**Korzyści**:
- Redukcja liczby wywołań sieciowych (przesyła wiele danych naraz)
- Enkapsulacja danych przesyłanych przez sieć
- Walidacja danych wejściowych

---

### 10. **Mapper**
**Kategoria**: Wzorce podstawowe

**Implementacja**: Serializery DRF przekształcają obiekty Python na JSON i odwrotnie

**Przykład**:
```python
# Automatyczne mapowanie Model → JSON
class StreamingHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = StreamingHistory
        fields = '__all__'

# Python object → JSON
history = StreamingHistory.objects.first()
json_data = StreamingHistorySerializer(history).data

# JSON → Python object
serializer = StreamingHistorySerializer(data=request.data)
if serializer.is_valid():
    history = serializer.save()
```

---

### 11. **Transaction Script**
**Kategoria**: Wzorce logiki dziedziny

**Implementacja**: Funkcje view wykonują transakcje biznesowe krok po kroku

**Przykład**:
```python
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_spotify_data(request):
    """
    Transaction Script: sekwencja kroków dla procesu uploadu
    """
    # 1. Walidacja
    if 'file' not in request.FILES:
        return Response({'error': 'No file provided'}, status=400)
    
    uploaded_file = request.FILES['file']
    
    if not uploaded_file.name.endswith('.zip'):
        return Response({'error': 'File must be a ZIP archive'}, status=400)
    
    # 2. Przygotowanie katalogu
    user_upload_dir = os.path.join(settings.UPLOAD_DIR, str(request.user.id))
    os.makedirs(user_upload_dir, exist_ok=True)
    
    # 3. Zapis pliku
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    file_path = os.path.join(user_upload_dir, f'spotify_data_{timestamp}.zip')
    
    with open(file_path, 'wb+') as destination:
        for chunk in uploaded_file.chunks():
            destination.write(chunk)
    
    # 4. Utworzenie rekordu w bazie
    upload = SpotifyDataUpload.objects.create(
        user=request.user,
        file_path=file_path,
        file_size=uploaded_file.size,
        processing_status='uploaded'
    )
    
    # 5. Przetwarzanie
    try:
        process_spotify_zip(upload, file_path)
        upload.processed = True
        upload.processing_status = 'completed'
        upload.save()
        
        return Response({'message': 'Success', 'upload': SpotifyDataUploadSerializer(upload).data})
    except Exception as e:
        upload.processing_status = 'failed'
        upload.save()
        return Response({'error': f'Error: {str(e)}'}, status=500)
```

**Charakterystyka**:
- Proceduralna organizacja logiki biznesowej
- Każda operacja jest osobną procedurą
- Brak złożonego modelu domenowego

---

### 12. **Template View**
**Kategoria**: Wzorce prezentacji internetowych

**Implementacja**: Komponenty Vue jako szablony z logiką prezentacji

**Przykład**:
```vue
<!-- Charts.vue - Template View -->
<template>
  <div class="charts-container">
    <h2>Statystyki słuchania</h2>
    
    <!-- Template zawiera strukturę i binding danych -->
    <div v-if="loading" class="loading">Ładowanie...</div>
    
    <div v-else-if="error" class="error">{{ error }}</div>
    
    <div v-else class="chart-wrapper">
      <canvas ref="chartCanvas"></canvas>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { uploadService } from '../services/upload'
import { Chart } from 'chart.js/auto'

const chartCanvas = ref(null)
const monthlyData = ref([])
const loading = ref(true)
const error = ref(null)

onMounted(async () => {
  try {
    monthlyData.value = await uploadService.getMonthlyStats()
    await nextTick()
    createChart()
  } catch (err) {
    error.value = 'Błąd ładowania danych'
  } finally {
    loading.value = false
  }
})

function createChart() {
  // Logika renderowania wykresu
}
</script>
```

---

### 13. **Lazy Load / Proxy (częściowo)**
**Kategoria**: Wzorce zachowań dla mapowania obiektowo-relacyjnego

**Implementacja**: Django ORM z `select_related()` i `prefetch_related()` - optymalizacja ładowania relacji

**Przykład**:
```python
# Bez optymalizacji - N+1 queries
uploads = SpotifyDataUpload.objects.all()
for upload in uploads:
    print(upload.user.username)  # Każda iteracja = osobne zapytanie SQL

# Z optymalizacją - 1 query z JOIN
uploads = SpotifyDataUpload.objects.select_related('user').all()
for upload in uploads:
    print(upload.user.username)  # Wszystko pobrane jednym zapytaniem
```

**Implementacja w kodzie**:
```python
def process_streaming_history_file(upload, json_path):
    records = []
    for item in data:
        record = StreamingHistory(
            user=upload.user,  # Wykorzystuje już załadowany obiekt
            upload=upload,
            # ... inne pola
        )
        records.append(record)
    
    # Bulk create - optymalizacja zapisu
    StreamingHistory.objects.bulk_create(records, batch_size=1000)
```

---

### 14. **Remote Facade**
**Kategoria**: Wzorce dystrybucji

**Implementacja**: Django REST Framework API jako fasada dla frontendu

**Przykład**:
```python
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_top_tracks(request):
    """
    Remote Facade - uproszczony interfejs dla klienta
    Ukrywa złożoność agregacji, filtrowania i formatowania danych
    """
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    
    # Złożona logika ukryta za prostym endpointem
    query = StreamingHistory.objects.filter(
        user=request.user,
        master_metadata_track_name__isnull=False
    )
    
    # Walidacja i parsowanie dat
    if start_date_str:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        query = query.filter(ts__gte=start_date)
    
    if end_date_str:
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        query = query.filter(ts__lt=end_date + timedelta(days=1))
    
    # Agregacja
    top_tracks = (
        query
        .values('master_metadata_track_name', 'master_metadata_album_artist_name', 'master_metadata_album_album_name')
        .annotate(play_count=Count('id'), total_ms_played=Sum('ms_played'))
        .order_by('-play_count')[:50]
    )
    
    # Formatowanie wyniku
    result = []
    for idx, track in enumerate(top_tracks, start=1):
        result.append({
            'rank': idx,
            'track_name': track['master_metadata_track_name'],
            'artist_name': track['master_metadata_album_artist_name'],
            'play_count': track['play_count'],
            'total_hours_played': round(track['total_ms_played'] / (1000 * 60 * 60), 2)
        })
    
    return Response(result)
```

**Korzyści**:
- Redukcja liczby wywołań sieciowych (jedna fasada zamiast wielu zapytań)
- Ukrycie złożoności backendu
- Łatwiejsza optymalizacja wydajności

---

### 15. **Server Session State**
**Kategoria**: Wzorce stanu sesji

**Implementacja**: Django Session Framework przechowuje stan sesji na serwerze

**Przykład**:
```python
# Backend - sesja przechowywana w bazie danych
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        # ... konfiguracja
    }
}

SESSION_ENGINE = 'django.contrib.sessions.backends.db'  # Sesje w bazie danych

# Login - tworzenie sesji
@api_view(['POST'])
def login_view(request):
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)  # Tworzy sesję na serwerze
        request.session.save()
        
        response = Response(UserSerializer(user).data)
        response.set_cookie(
            key='sessionid',
            value=request.session.session_key,  # ID sesji
            max_age=86400
        )
        return response
```

```javascript
// Frontend - przesyła tylko session ID w cookie
const api = axios.create({
  baseURL: '/api',
  withCredentials: true  // Automatyczne przesyłanie cookies
})
```

**Korzyści**:
- Bezpieczniejsze (dane sesji nie są u klienta)
- Możliwość przechowywania dużych ilości danych
- Kontrola nad sesjami (np. wymuszenie wylogowania)

---

### 16. **Value Object** (częściowo)
**Kategoria**: Wzorce podstawowe

**Implementacja**: Serializowane dane w odpowiedziach API

**Przykład**:
```python
# Funkcja zwraca Value Object (niemodyfikowalny słownik danych)
def get_monthly_listening_stats(request):
    result = []
    for stat in monthly_stats:
        # Value Object - reprezentuje wartość, nie encję
        month_data = {
            'month': format_month_polish(stat['month']),
            'play_count': stat['play_count'],
            'hours': round(stat['total_hours'], 2)
        }
        result.append(month_data)
    
    return Response(result)
```

**Charakterystyka**:
- Obiekt reprezentuje wartość, nie ma tożsamości
- Niemodyfikowalny po utworzeniu
- Porównywany przez wartości, nie przez referencję

---

### 17. **Query Object**
**Kategoria**: Wzorce odwzorowań obiektów i relacyjnych metadanych

**Implementacja**: Django ORM QuerySet API

**Przykład**:
```python
# QueryObject - enkapsuluje logikę zapytań
query = StreamingHistory.objects.filter(
    user=request.user,
    master_metadata_track_name__isnull=False
)

# Dynamiczne budowanie zapytania
if start_date_str:
    query = query.filter(ts__gte=start_date)

if end_date_str:
    query = query.filter(ts__lt=end_date)

# Agregacja jako część Query Object
top_tracks = (
    query
    .values('master_metadata_track_name', 'master_metadata_album_artist_name')
    .annotate(play_count=Count('id'), total_ms_played=Sum('ms_played'))
    .order_by('-play_count')[:50]
)
```

**Korzyści**:
- Zapytania są obiektami pierwszej klasy
- Łatwe komponowanie i modyfikowanie zapytań
- Lazy evaluation (wykonanie dopiero przy iteracji)

---

### 18. **Layer Supertype**
**Kategoria**: Wzorce podstawowe

**Implementacja**: `models.Model` jako bazowa klasa dla wszystkich modeli Django

**Przykład**:
```python
# Django definiuje Layer Supertype dla wszystkich modeli
class Model(metaclass=ModelBase):
    # Wspólna funkcjonalność: save(), delete(), pk, objects, itp.
    pass

# Wszystkie modele dziedziczą z Layer Supertype
class SpotifyDataUpload(models.Model):  # ← Layer Supertype
    # Automatycznie dostaje: id, save(), delete(), objects, etc.
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file_path = models.CharField(max_length=500)
    
class StreamingHistory(models.Model):  # ← Layer Supertype
    # Automatycznie dostaje: id, save(), delete(), objects, etc.
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ts = models.DateTimeField()
```

**Korzyści**:
- Eliminuje duplikację kodu
- Centralizuje wspólną funkcjonalność
- Ułatwia rozszerzanie

---

### 19. **Registry** (częściowo)
**Kategoria**: Wzorce podstawowe

**Implementacja**: Django App Registry, Vue Router

**Przykład**:
```python
# Django App Registry - INSTALLED_APPS
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'rest_framework',
    'authentication',  # ← Zarejestrowana aplikacja
    'data_upload',     # ← Zarejestrowana aplikacja
]
```

```javascript
// Vue Component Registry
import Dashboard from '../views/Dashboard.vue'
import Charts from '../views/Charts.vue'

// Rejestracja routów
const routes = [
  { path: '/dashboard', name: 'Dashboard', component: Dashboard },
  { path: '/charts', name: 'Charts', component: Charts }
]
```

---

### 20. **Page Controller**
**Kategoria**: Wzorce prezentacji internetowych

**Implementacja**: Osobne komponenty Vue dla każdej strony + dedykowane endpointy API

**Przykład**:
```javascript
// TopTracks.vue - Page Controller dla strony top utworów
export default {
  name: 'TopTracks',
  setup() {
    const tracks = ref([])
    const startDate = ref('')
    const endDate = ref('')
    
    async function loadTopTracks() {
      // Kontroler strony zarządza logiką tej konkretnej strony
      const params = {}
      if (startDate.value) params.start_date = startDate.value
      if (endDate.value) params.end_date = endDate.value
      
      tracks.value = await uploadService.getTopTracks(params)
    }
    
    return { tracks, startDate, endDate, loadTopTracks }
  }
}
```

```python
# Backend - osobny endpoint dla każdej strony
@api_view(['GET'])
def get_top_tracks(request):
    """Page Controller backend dla strony TopTracks"""
    # Logika specyficzna dla tej strony
    pass

@api_view(['GET'])
def get_monthly_listening_stats(request):
    """Page Controller backend dla strony Charts"""
    # Inna logika dla innej strony
    pass
```

**Charakterystyka**:
- Każda strona ma dedykowany kontroler
- Kontroler obsługuje całą logikę strony
- Prostsza struktura niż Front Controller dla złożonych operacji

---

### 21. **Separated Interface**
**Kategoria**: Wzorce podstawowe

**Implementacja**: 
- Frontend: Service interfaces (`services/*.js`) oddzielone od komponentów
- Backend: Serializery oddzielają interfejs API od modeli

**Przykład**:
```javascript
// Interfejs (kontrakt) oddzielony od implementacji
// frontend/src/services/upload.js
export const uploadService = {
  async uploadFile(file) { /* implementacja */ },
  async getTopTracks(params) { /* implementacja */ },
  async deleteAllData() { /* implementacja */ }
}

// Komponenty używają interfejsu, nie znają szczegółów implementacji
// frontend/src/views/Dashboard.vue
import { uploadService } from '../services/upload'

async function handleDelete() {
  await uploadService.deleteAllData()  // Używa interfejsu
}
```

**Korzyści**:
- Łatwiejsze testowanie (mockowanie interfejsów)
- Redukcja zależności między warstwami
- Możliwość podmiany implementacji

---

### 22. **Unit of Work** (częściowo)
**Kategoria**: Wzorce zachowań dla mapowania obiektowo-relacyjnego

**Implementacja**: Django database transactions

**Przykład**:
```python
from django.db import transaction

@transaction.atomic  # Unit of Work - wszystko lub nic
def process_spotify_zip(upload, file_path):
    """
    Transakcja obejmuje wiele operacji:
    - Ekstrakcję pliku
    - Przetwarzanie JSON
    - Bulk create rekordów
    """
    extract_dir = file_path.replace('.zip', '_extracted')
    os.makedirs(extract_dir, exist_ok=True)
    
    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)
    
    for root, dirs, files in os.walk(extract_dir):
        for file in files:
            if file.startswith('Streaming_History'):
                json_path = os.path.join(root, file)
                process_streaming_history_file(upload, json_path)
    
    # Jeśli coś się nie uda, wszystko zostanie wycofane (rollback)

# Bulk create - optymalizacja w ramach Unit of Work
def process_streaming_history_file(upload, json_path):
    records = []
    for item in data:
        records.append(StreamingHistory(...))
    
    # Jedna transakcja dla wszystkich rekordów
    StreamingHistory.objects.bulk_create(records, batch_size=1000)
```

**Korzyści**:
- Zapewnia spójność danych
- Automatyczny rollback przy błędzie
- Optymalizacja (mniej zapytań do bazy)

---

### 23. **Metadata Mapping** (częściowo)
**Kategoria**: Wzorce odwzorowań obiektów i relacyjnych metadanych

**Implementacja**: Django model `Meta` class - metadane modelu określają mapowanie

**Przykład**:
```python
class SpotifyDataUpload(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file_path = models.CharField(max_length=500)
    upload_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        # Metadata określa szczegóły mapowania
        ordering = ['-upload_date']  # Domyślne sortowanie
        db_table = 'spotify_data_upload'  # Nazwa tabeli
        indexes = [
            models.Index(fields=['user', '-upload_date']),  # Indeksy
        ]
        verbose_name = 'Spotify Data Upload'
        verbose_name_plural = 'Spotify Data Uploads'
```

---

### 24. **Optimistic Offline Lock** (potencjał do implementacji)
**Kategoria**: Wzorce współbieżności autonomicznej

**Stan**: Obecnie nie implementowane, ale możliwe do dodania w przyszłości

**Potencjalne użycie**: Edycja danych użytkownika przez wielu administratorów

**Przykład**:
```python
# Możliwa implementacja z version field
class SpotifyDataUpload(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file_path = models.CharField(max_length=500)
    version = models.IntegerField(default=0)  # Dla optimistic locking
    
    def save(self, *args, **kwargs):
        # Sprawdź wersję przed zapisem
        if self.pk:
            old_version = self.version
            self.version += 1
            updated = SpotifyDataUpload.objects.filter(
                pk=self.pk,
                version=old_version
            ).update(version=self.version)
            
            if not updated:
                raise ConcurrentUpdateError()
        
        super().save(*args, **kwargs)
```

---

## Wzorce NIE użyte w projekcie

### Nieobecne wzorce z uzasadnieniem:

1. **Active Record** - Zastąpiony przez Data Mapper (Django ORM)
2. **Table Data Gateway / Row Data Gateway** - Zastąpiony przez Repository (ORM)
3. **Table Module** - Nie używany, zastąpiony przez Service Layer
4. **Domain Model** - Prostsza aplikacja, używamy Transaction Script
5. **Service Stub** - Brak zewnętrznych serwisów do mockowania w produkcji
6. **Plugin** - Brak systemu wtyczek
7. **Money / Special Case** - Brak operacji finansowych
8. **Association Table Mapping** - Brak relacji many-to-many
9. **Single/Class/Concrete Table Inheritance** - Brak hierarchii dziedziczenia w modelach
10. **Two Step View / Transform View** - SPA (Vue) renderuje widoki po stronie klienta
11. **Application Controller** - Prostszy Page Controller wystarczy
12. **Client Session State** - Używamy Server Session State
13. **Pessimistic Offline Lock / Coarse-Grained Lock / Implicit Lock** - Brak konfliktów współbieżności
14. **Dependent Mapping / Embedded Value / Serialized LOB** - Proste mapowanie 1:1 wystarczy

---

## Podsumowanie

### Statystyka użytych wzorców:

| Kategoria | Liczba wzorców | Przykłady |
|-----------|----------------|-----------|
| **Prezentacji internetowych** | 5 | MVC/MVVM, Front Controller, Template View, Page Controller |
| **Źródła danych** | 2 | Repository, Data Mapper |
| **Mapowanie OR** | 5 | Identity Field, Foreign Key Mapping, Unit of Work, Lazy Load, Metadata Mapping |
| **Logiki dziedziny** | 2 | Transaction Script, Service Layer |
| **Dystrybucji** | 2 | Remote Facade, DTO |
| **Podstawowe** | 5 | Gateway, Mapper, Layer Supertype, Separated Interface, Value Object |
| **Stanu sesji** | 1 | Server Session State |
| **Odwzorowań** | 1 | Query Object |

**Łącznie: 23 wzorce zidentyfikowane**

---

### Kluczowe obserwacje:

1. **Django + DRF** implementują wiele wzorców out-of-the-box:
   - Data Mapper (ORM)
   - Repository (QuerySet API)
   - Unit of Work (transactions)
   - Layer Supertype (models.Model)
   - Identity Field (automatic pk)
   - Foreign Key Mapping

2. **Vue 3 + Vue Router** realizują wzorce frontendowe:
   - MVVM (Composition API + reactive state)
   - Front Controller (Vue Router)
   - Template View (Single File Components)
   - Page Controller (route components)

3. **REST API** jako Remote Facade:
   - DRF serializery = DTO + Mapper
   - Service classes = Separated Interface
   - API endpoints = Service Layer

4. **Sesje i bezpieczeństwo**:
   - Server Session State (Django sessions w PostgreSQL)
   - Gateway pattern (axios + CSRF handling)

5. **Brak złożonych wzorców**:
   - Nie ma Domain Model (wystarczy Transaction Script)
   - Nie ma wzorców dziedziczenia (płaska struktura modeli)
   - Nie ma wzorców konfliktów (brak współbieżnej edycji)

---

## Wnioski

Aplikacja **Extended Spotify App** implementuje **23 wzorce projektowe** z literatury Enterprise Patterns. Architektura oparta na Django REST Framework + Vue 3 naturalnie wymusza użycie wielu wzorców, co zapewnia:

- ✅ **Separację warstw** (frontend ↔ API ↔ database)
- ✅ **Łatwą testowalność** (Separated Interface, Gateway)
- ✅ **Skalowalność** (Repository, Service Layer)
- ✅ **Bezpieczeństwo** (Server Session State, Remote Facade)
- ✅ **Utrzymywalność** (Layer Supertype, Transaction Script)

Framework Django DRF dostarcza implementacje wzorców "za darmo", co pozwala skupić się na logice biznesowej zamiast na infrastrukturze. Vue 3 z kolei implementuje wzorce prezentacji (MVVM, Front Controller) w sposób idiomatyczny dla nowoczesnych frameworków SPA.

---

**Data utworzenia**: 22 stycznia 2026  
**Autor analizy**: Analiza przeprowadzona dla projektu zaliczeniowego z Wzorców Projektowych  
**Wersja aplikacji**: Extended Spotify App v1.0
