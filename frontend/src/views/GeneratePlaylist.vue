<template>
  <div class="generate-playlist-container">
    <div class="page-header">
      <h1>Generuj Playlistę</h1>
      <p class="subtitle">Wybierz okres i liczbę utworów, aby wygenerować własną playlistę</p>
    </div>

    <div class="filter-section">
      <div class="filter-card">
        <h3>Parametry playlisty</h3>
        
        <div class="form-group">
          <label for="track-count">Liczba utworów:</label>
          <input 
            type="number" 
            id="track-count"
            v-model.number="trackCount" 
            min="1" 
            max="200"
            class="track-count-input"
            placeholder="np. 50"
          >
          <small class="helper-text">Wpisz liczbę od 1 do 200</small>
        </div>

        <div class="date-filter">
          <div class="date-input-group">
            <label>Data od:</label>
            <input 
              type="date" 
              v-model="startDate" 
              class="date-input"
            >
          </div>
          
          <div class="date-input-group">
            <label>Data do:</label>
            <input 
              type="date" 
              v-model="endDate" 
              class="date-input"
            >
          </div>
        </div>

        <div class="button-group">
          <button 
            @click="generatePlaylist" 
            class="btn-generate"
            :disabled="loading || !trackCount"
          >
            {{ loading ? 'Generowanie...' : 'Generuj Playlistę' }}
          </button>
          <button 
            @click="clearFilters" 
            class="btn-clear"
            :disabled="loading"
          >
            Wyczyść
          </button>
        </div>

        <div v-if="message" class="info-message" :class="messageType">
          {{ message }}
        </div>
      </div>
    </div>

    <div v-if="tracks.length > 0" class="tracks-section">
      <div class="tracks-header">
        <h2>Wygenerowana playlista</h2>
        <div class="track-info">
          <span class="track-count-badge">
            {{ tracks.length }} {{ tracks.length === 1 ? 'utwór' : 'utworów' }}
          </span>
          <span v-if="requestedCount && tracks.length < requestedCount" class="warning-badge">
            Znaleziono {{ tracks.length }}/{{ requestedCount }} utworów
          </span>
        </div>
      </div>

      <div class="tracks-list">
        <div 
          v-for="track in tracks" 
          :key="track.rank"
          class="track-card"
        >
          <div class="track-rank">{{ track.rank }}</div>
          <div class="track-info-content">
            <div class="track-name">{{ track.track_name }}</div>
            <div class="track-artist">{{ track.artist_name }}</div>
            <div class="track-album">{{ track.album_name }}</div>
          </div>
          <div class="track-stats">
            <div class="stat">
              <span class="stat-label">Odtworzeń:</span>
              <span class="stat-value">{{ track.play_count }}</span>
            </div>
            <div class="stat">
              <span class="stat-label">Godzin:</span>
              <span class="stat-value">{{ track.total_hours_played }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-else-if="!loading && hasSearched" class="no-results">
      <p>Nie znaleziono utworów dla wybranych kryteriów.</p>
      <p class="hint">Spróbuj zmienić zakres dat lub dodaj więcej danych.</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { uploadService } from '../services/upload'

const router = useRouter()

const tracks = ref([])
const loading = ref(false)
const trackCount = ref(50)
const startDate = ref('')
const endDate = ref('')
const message = ref('')
const messageType = ref('')
const requestedCount = ref(null)
const hasSearched = ref(false)

const generatePlaylist = async () => {
  if (!trackCount.value || trackCount.value < 1) {
    message.value = 'Wprowadź prawidłową liczbę utworów (minimum 1)'
    messageType.value = 'error'
    return
  }

  if (trackCount.value > 200) {
    message.value = 'Maksymalna liczba utworów to 200'
    messageType.value = 'error'
    return
  }

  loading.value = true
  message.value = ''
  hasSearched.value = true
  
  try {
    const response = await uploadService.generateCustomPlaylist(
      startDate.value,
      endDate.value,
      trackCount.value
    )
    
    tracks.value = response.tracks || []
    requestedCount.value = response.requested_count
    
    if (response.message) {
      message.value = response.message
      messageType.value = 'warning'
    } else {
      message.value = `Pomyślnie wygenerowano playlistę z ${tracks.value.length} utworami`
      messageType.value = 'success'
    }
  } catch (error) {
    console.error('Error generating playlist:', error)
    message.value = error.response?.data?.error || 'Wystąpił błąd podczas generowania playlisty'
    messageType.value = 'error'
    tracks.value = []
  } finally {
    loading.value = false
  }
}

const clearFilters = () => {
  trackCount.value = 50
  startDate.value = ''
  endDate.value = ''
  tracks.value = []
  message.value = ''
  requestedCount.value = null
  hasSearched.value = false
}
</script>

<style scoped>
.generate-playlist-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
}

.page-header h1 {
  font-size: 2.5rem;
  margin-bottom: 10px;
  color: #1db954;
}

.subtitle {
  font-size: 1.1rem;
  color: #666;
}

.filter-section {
  margin-bottom: 30px;
}

.filter-card {
  background: white;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.filter-card h3 {
  margin-top: 0;
  margin-bottom: 20px;
  color: #333;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: #333;
}

.track-count-input {
  width: 100%;
  max-width: 300px;
  padding: 12px;
  border: 2px solid #ddd;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.3s;
}

.track-count-input:focus {
  outline: none;
  border-color: #1db954;
}

.helper-text {
  display: block;
  margin-top: 5px;
  color: #666;
  font-size: 0.9rem;
}

.date-filter {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
  margin-bottom: 20px;
}

.date-input-group {
  flex: 1;
  min-width: 200px;
}

.date-input-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: #333;
}

.date-input {
  width: 100%;
  padding: 12px;
  border: 2px solid #ddd;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.3s;
}

.date-input:focus {
  outline: none;
  border-color: #1db954;
}

.button-group {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

.btn-generate {
  background-color: #1db954;
  color: white;
  border: none;
  padding: 12px 30px;
  border-radius: 25px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.3s, transform 0.1s;
}

.btn-generate:hover:not(:disabled) {
  background-color: #1ed760;
  transform: translateY(-2px);
}

.btn-generate:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.btn-clear {
  background-color: #666;
  color: white;
  border: none;
  padding: 12px 30px;
  border-radius: 25px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.3s;
}

.btn-clear:hover:not(:disabled) {
  background-color: #555;
}

.btn-clear:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.info-message {
  margin-top: 15px;
  padding: 12px 20px;
  border-radius: 8px;
  font-weight: 500;
}

.info-message.success {
  background-color: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.info-message.warning {
  background-color: #fff3cd;
  color: #856404;
  border: 1px solid #ffeaa7;
}

.info-message.error {
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.tracks-section {
  background: white;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.tracks-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 15px;
}

.tracks-header h2 {
  margin: 0;
  color: #333;
}

.track-info {
  display: flex;
  gap: 10px;
  align-items: center;
}

.track-count-badge {
  background-color: #1db954;
  color: white;
  padding: 6px 15px;
  border-radius: 20px;
  font-weight: 600;
  font-size: 0.9rem;
}

.warning-badge {
  background-color: #ff9800;
  color: white;
  padding: 6px 15px;
  border-radius: 20px;
  font-weight: 600;
  font-size: 0.9rem;
}

.tracks-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.track-card {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 8px;
  transition: transform 0.2s, box-shadow 0.2s;
}

.track-card:hover {
  transform: translateX(5px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.track-rank {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1db954;
  min-width: 40px;
  text-align: center;
}

.track-info-content {
  flex: 1;
}

.track-name {
  font-size: 1.1rem;
  font-weight: 600;
  color: #333;
  margin-bottom: 4px;
}

.track-artist {
  color: #666;
  margin-bottom: 2px;
}

.track-album {
  color: #999;
  font-size: 0.9rem;
}

.track-stats {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.stat {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.stat-label {
  font-size: 0.85rem;
  color: #666;
}

.stat-value {
  font-size: 1.1rem;
  font-weight: 600;
  color: #333;
}

.no-results {
  text-align: center;
  padding: 60px 20px;
  color: #666;
}

.no-results p {
  font-size: 1.2rem;
  margin: 10px 0;
}

.hint {
  color: #999;
  font-size: 1rem;
}

@media (max-width: 768px) {
  .track-card {
    flex-direction: column;
    align-items: flex-start;
  }

  .track-stats {
    width: 100%;
    justify-content: space-between;
  }

  .date-filter {
    flex-direction: column;
  }

  .button-group {
    flex-direction: column;
  }

  .btn-generate,
  .btn-clear {
    width: 100%;
  }
}
</style>
