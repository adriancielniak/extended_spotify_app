<template>
  <div class="dashboard">
    <header class="dashboard-header">
      <h1>Dashboard</h1>
      <div class="user-info">
        <span>Witaj, {{ authStore.user?.username }}!</span>
        <button @click="handleLogout" class="btn btn-logout">Wyloguj</button>
      </div>
    </header>

    <div class="dashboard-content">
      <!-- Success message for Spotify connection -->
      <div v-if="spotifyConnected" class="spotify-success">
        <p>✅ Spotify połączony! Możesz teraz tworzyć playlisty z Top 50 utworów.</p>
      </div>
      
      <div class="stats-card" v-if="stats">
        <h2>📊 Twoje statystyki</h2>
        <div class="stats-grid">
          <div class="stat-item">
            <span class="stat-value">{{ stats.total_records }}</span>
            <span class="stat-label">Nagrań</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ stats.total_hours_played }}</span>
            <span class="stat-label">Godzin słuchania</span>
          </div>
        </div>
      </div>

      <div class="actions-card">
        <h2>🎵 Akcje</h2>
        <div class="actions-buttons">
          <router-link to="/upload" class="btn btn-primary">
            Prześlij dane Spotify
          </router-link>
          <router-link to="/top-tracks" class="btn btn-success">
            Zobacz Top 50 utworów
          </router-link>
          <router-link to="/generate-playlist" class="btn btn-generate">
            Generuj Playlistę
          </router-link>
          <router-link to="/charts" class="btn btn-charts">
            📊 Statystyki i Wykresy
          </router-link>
        </div>
      </div>

      <div class="uploads-card" v-if="uploads.length > 0">
        <h2>📁 Twoje przesłane pliki</h2>
        <ul class="uploads-list">
          <li v-for="upload in uploads" :key="upload.id">
            <div class="upload-info">
              <span class="upload-date">{{ formatDate(upload.upload_date) }}</span>
              <span class="upload-size">{{ formatSize(upload.file_size) }}</span>
              <span class="upload-status" :class="upload.processing_status">
                {{ upload.processing_status }}
              </span>
            </div>
          </li>
        </ul>
        <div class="danger-zone">
          <h3>⚠️ Strefa niebezpieczna</h3>
          <p>Usuń wszystkie dane o słuchaniu, aby załadować nowy plik ZIP</p>
          <button 
            @click="confirmDeleteAll" 
            class="btn-delete-all"
            :disabled="deleting"
          >
            {{ deleting ? 'Usuwanie...' : 'Usuń wszystkie dane' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { uploadService } from '../services/upload'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const stats = ref(null)
const uploads = ref([])
const spotifyConnected = ref(false)
const deleting = ref(false)

onMounted(async () => {
  try {
    stats.value = await uploadService.getStats()
    uploads.value = await uploadService.getUploads()
    
    // Check if just connected Spotify
    if (route.query.spotify_connected === 'true') {
      spotifyConnected.value = true
      // Clear query param after 3 seconds
      setTimeout(() => {
        spotifyConnected.value = false
        router.replace('/dashboard')
      }, 3000)
    }
  } catch (error) {
    console.error('Error fetching data:', error)
  }
})

async function handleLogout() {
  await authStore.logout()
  router.push('/')
}

function formatDate(dateString) {
  return new Date(dateString).toLocaleDateString('pl-PL', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function formatSize(bytes) {
  const mb = bytes / (1024 * 1024)
  return `${mb.toFixed(2)} MB`
}

async function confirmDeleteAll() {
  const confirmed = confirm(
    '⚠️ UWAGA!\n\n' +
    'Czy na pewno chcesz usunąć WSZYSTKIE dane o słuchaniu?\n\n' +
    'Ta operacja:\n' +
    '• Usunie wszystkie nagrania o odtwarzaniu\n' +
    '• Usunie wszystkie przesłane pliki\n' +
    '• Jest NIEODWRACALNA\n\n' +
    'Po usunięciu będziesz mógł załadować nowy plik ZIP.\n\n' +
    'Kontynuować?'
  )
  
  if (!confirmed) return
  
  deleting.value = true
  
  try {
    const result = await uploadService.deleteAllData()
    alert(
      `✅ Sukces!\n\n` +
      `Usunięto:\n` +
      `• ${result.deleted_streaming_records} nagrań o słuchaniu\n` +
      `• ${result.deleted_uploads} przesłanych plików\n\n` +
      `Możesz teraz załadować nowy plik ZIP.`
    )
    
    // Refresh data
    stats.value = null
    uploads.value = []
    
    // Reload stats
    try {
      stats.value = await uploadService.getStats()
      uploads.value = await uploadService.getUploads()
    } catch (error) {
      console.log('No data after deletion')
    }
  } catch (error) {
    console.error('Error deleting data:', error)
    alert(
      '❌ Błąd!\n\n' +
      'Nie udało się usunąć danych.\n' +
      (error.response?.data?.error || 'Spróbuj ponownie później.')
    )
  } finally {
    deleting.value = false
  }
}
</script>

<style scoped>
.dashboard {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.dashboard-header h1 {
  color: #1db954;
}

.user-info {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.dashboard-content {
  display: grid;
  gap: 2rem;
}

.spotify-success {
  background: linear-gradient(135deg, #d4edda, #c3e6cb);
  padding: 1rem 1.5rem;
  border-radius: 0.5rem;
  border-left: 4px solid #1DB954;
  animation: slideIn 0.3s ease-out;
}

.spotify-success p {
  margin: 0;
  color: #155724;
  font-weight: 500;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.stats-card, .actions-card, .uploads-card {
  background: white;
  padding: 2rem;
  border-radius: 1rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

h2 {
  margin-bottom: 1.5rem;
  color: #333;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 2rem;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1rem;
  background: #f9f9f9;
  border-radius: 0.5rem;
}

.stat-value {
  font-size: 2.5rem;
  font-weight: bold;
  color: #1db954;
}

.stat-label {
  color: #666;
  margin-top: 0.5rem;
}

.btn {
  padding: 1rem 2rem;
  border: none;
  border-radius: 0.5rem;
  font-weight: bold;
  cursor: pointer;
  text-decoration: none;
  display: inline-block;
  transition: background-color 0.2s;
}

.btn-primary {
  background-color: #1db954;
  color: white;
}

.btn-primary:hover {
  background-color: #1ed760;
}

.btn-success {
  background-color: #28a745;
  color: white;
}

.btn-success:hover {
  background-color: #218838;
}

.btn-generate {
  background-color: #8b5cf6;
  color: white;
}

.btn-generate:hover {
  background-color: #7c3aed;
}

.btn-charts {
  background-color: #ff6b35;
  color: white;
}

.btn-charts:hover {
  background-color: #ff5722;
}

.btn-logout {
  background-color: #191414;
  color: white;
}

.btn-logout:hover {
  background-color: #282828;
}

.actions-buttons {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.uploads-list {
  list-style: none;
  padding: 0;
}

.uploads-list li {
  padding: 1rem;
  border-bottom: 1px solid #eee;
}

.uploads-list li:last-child {
  border-bottom: none;
}

.upload-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.upload-status {
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.875rem;
  font-weight: bold;
}

.upload-status.completed {
  background-color: #d4edda;
  color: #155724;
}

.upload-status.uploaded {
  background-color: #d1ecf1;
  color: #0c5460;
}

.upload-status.failed {
  background-color: #f8d7da;
  color: #721c24;
}

.danger-zone {
  margin-top: 30px;
  padding: 20px;
  background: linear-gradient(135deg, #fff5f5, #ffe5e5);
  border: 2px solid #ff4444;
  border-radius: 12px;
}

.danger-zone h3 {
  margin-top: 0;
  color: #d32f2f;
  font-size: 1.2rem;
}

.danger-zone p {
  color: #666;
  margin-bottom: 15px;
}

.btn-delete-all {
  background-color: #d32f2f;
  color: white;
  border: none;
  padding: 12px 30px;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.3s, transform 0.1s;
}

.btn-delete-all:hover:not(:disabled) {
  background-color: #b71c1c;
  transform: translateY(-2px);
}

.btn-delete-all:disabled {
  background-color: #ccc;
  cursor: not-allowed;
  transform: none;
}
</style>
