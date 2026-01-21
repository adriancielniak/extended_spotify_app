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
        <router-link to="/upload" class="btn btn-primary">
          Prześlij dane Spotify
        </router-link>
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
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { uploadService } from '../services/upload'

const router = useRouter()
const authStore = useAuthStore()

const stats = ref(null)
const uploads = ref([])

onMounted(async () => {
  try {
    stats.value = await uploadService.getStats()
    uploads.value = await uploadService.getUploads()
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

.btn-logout {
  background-color: #191414;
  color: white;
}

.btn-logout:hover {
  background-color: #282828;
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
</style>
