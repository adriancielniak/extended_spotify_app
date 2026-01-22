<template>
  <div class="top-tracks">
    <header class="top-tracks-header">
      <h1>🎵 Top 50 Najpopularniejszych Utworów</h1>
      <router-link to="/dashboard" class="btn btn-secondary">
        ← Powrót do dashboardu
      </router-link>
    </header>

    <div class="content">
      <div v-if="loading" class="loading">
        <p>Ładowanie najpopularniejszych utworów...</p>
      </div>

      <div v-else-if="error" class="error">
        <p>{{ error }}</p>
        <button @click="loadTopTracks" class="btn btn-primary">Spróbuj ponownie</button>
      </div>

      <div v-else-if="tracks.length === 0" class="empty">
        <p>Brak danych do wyświetlenia. Prześlij swoje dane Spotify, aby zobaczyć statystyki!</p>
        <router-link to="/upload" class="btn btn-primary">
          Prześlij dane
        </router-link>
      </div>

      <div v-else class="tracks-list">
        <div class="stats-summary">
          <div class="date-filter">
            <div class="date-input-group">
              <label for="start-date">Data od:</label>
              <input 
                type="date" 
                id="start-date" 
                v-model="startDate"
                class="date-input"
              >
            </div>
            
            <div class="date-input-group">
              <label for="end-date">Data do:</label>
              <input 
                type="date" 
                id="end-date" 
                v-model="endDate"
                class="date-input"
              >
            </div>
            
            <button @click="loadTopTracks" class="btn-generate">Generuj</button>
            <button @click="clearDates" class="btn-clear-dates">Wyczyść</button>
          </div>
          
          <p>Twoje {{ tracks.length }} najpopularniejszych utworów</p>
          
          <!-- Spotify connection and playlist creation -->
          <div class="spotify-actions">
            <div v-if="!spotifyConnected" class="spotify-connect">
              <p class="info-text">Połącz konto Spotify, aby utworzyć playlistę</p>
              <button @click="connectSpotify" class="btn btn-spotify" :disabled="connectingSpotify">
                <span v-if="!connectingSpotify">🎧 Połącz ze Spotify</span>
                <span v-else>Łączenie...</span>
              </button>
            </div>
            
            <div v-else class="spotify-connected">
              <p class="success-text">✅ Spotify połączony</p>
              <div class="button-group">
                <button @click="createPlaylist" class="btn btn-create-playlist" :disabled="creatingPlaylist">
                  <span v-if="!creatingPlaylist">➕ Utwórz playlistę z Top 50</span>
                  <span v-else>Tworzenie...</span>
                </button>
                <button @click="disconnectSpotify" class="btn btn-disconnect">
                  Rozłącz
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Success message after playlist creation -->
        <div v-if="playlistCreated" class="playlist-success">
          <h3>🎉 Playlista utworzona!</h3>
          <p>Twoja playlista "{{ playlistName }}" została utworzona w Spotify</p>
          <a :href="playlistUrl" target="_blank" class="btn btn-open-spotify">
            Otwórz w Spotify
          </a>
        </div>

        <div class="tracks-table-container">
          <table class="tracks-table">
            <thead>
              <tr>
                <th class="rank-col">#</th>
                <th class="track-col">Utwór</th>
                <th class="artist-col">Artysta</th>
                <th class="album-col">Album</th>
                <th class="plays-col">Odtworzeń</th>
                <th class="hours-col">Godzin</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="track in tracks" :key="track.rank" class="track-row">
                <td class="rank-col">
                  <span class="rank-badge" :class="getRankClass(track.rank)">
                    {{ track.rank }}
                  </span>
                </td>
                <td class="track-col">
                  <div class="track-name">{{ track.track_name }}</div>
                </td>
                <td class="artist-col">{{ track.artist_name }}</td>
                <td class="album-col">{{ track.album_name }}</td>
                <td class="plays-col">
                  <span class="play-count">{{ track.play_count }}</span>
                </td>
                <td class="hours-col">
                  <span class="hours-count">{{ track.total_hours_played }}h</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { uploadService } from '../services/upload'
import { spotifyService } from '../services/spotify'

const route = useRoute()

const tracks = ref([])
const loading = ref(true)
const error = ref(null)
const startDate = ref('')
const endDate = ref('')
const spotifyConnected = ref(false)
const connectingSpotify = ref(false)
const creatingPlaylist = ref(false)
const playlistCreated = ref(false)
const playlistName = ref('')
const playlistUrl = ref('')

onMounted(async () => {
  await loadTopTracks()
  await checkSpotifyConnection()
  
  // Check if user just connected Spotify
  if (route.query.spotify_connected === 'true') {
    // Refresh connection status
    await checkSpotifyConnection()
    // Show success message
    console.log('Spotify connected successfully!')
  }
  
  // Check for errors from Spotify OAuth
  if (route.query.error) {
    error.value = `Błąd połączenia ze Spotify: ${route.query.error}`
  }
})

async function loadTopTracks() {
  loading.value = true
  error.value = null
  
  try {
    tracks.value = await uploadService.getTopTracks(startDate.value, endDate.value)
  } catch (err) {
    console.error('Error loading top tracks:', err)
    error.value = 'Nie udało się załadować najpopularniejszych utworów. Spróbuj ponownie.'
  } finally {
    loading.value = false
  }
}

function clearDates() {
  startDate.value = ''
  endDate.value = ''
  loadTopTracks()
}

async function checkSpotifyConnection() {
  try {
    const status = await spotifyService.getConnectionStatus()
    spotifyConnected.value = status.connected && !status.expired
  } catch (err) {
    console.error('Error checking Spotify connection:', err)
    spotifyConnected.value = false
  }
}

async function connectSpotify() {
  connectingSpotify.value = true
  
  try {
    const { auth_url } = await spotifyService.getAuthUrl('top-tracks')
    // Redirect to Spotify authorization
    window.location.href = auth_url
  } catch (err) {
    console.error('Error connecting to Spotify:', err)
    error.value = 'Nie udało się połączyć ze Spotify. Spróbuj ponownie.'
    connectingSpotify.value = false
  }
}

async function disconnectSpotify() {
  try {
    await spotifyService.disconnect()
    spotifyConnected.value = false
    playlistCreated.value = false
  } catch (err) {
    console.error('Error disconnecting Spotify:', err)
    error.value = 'Nie udało się rozłączyć Spotify.'
  }
}

async function createPlaylist() {
  creatingPlaylist.value = true
  error.value = null
  
  try {
    const result = await spotifyService.createPlaylist()
    
    if (result.success) {
      playlistCreated.value = true
      playlistName.value = result.playlist_name
      playlistUrl.value = result.playlist_url
    } else {
      error.value = result.error || 'Nie udało się utworzyć playlisty'
    }
  } catch (err) {
    console.error('Error creating playlist:', err)
    error.value = err.response?.data?.error || 'Nie udało się utworzyć playlisty. Spróbuj ponownie.'
  } finally {
    creatingPlaylist.value = false
  }
}

function getRankClass(rank) {
  if (rank === 1) return 'gold'
  if (rank === 2) return 'silver'
  if (rank === 3) return 'bronze'
  if (rank <= 10) return 'top-10'
  return ''
}
</script>

<style scoped>
.top-tracks {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
}

.top-tracks-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #1DB954;
}

.top-tracks-header h1 {
  color: #1DB954;
  margin: 0;
  font-size: 2rem;
}

.content {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.loading, .error, .empty {
  text-align: center;
  padding: 3rem;
  color: #666;
}

.error {
  color: #dc3545;
}

.stats-summary {
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
  text-align: center;
}

.date-filter {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1.5rem;
  margin-bottom: 1rem;
  padding: 1.5rem;
  background: white;
  border-radius: 6px;
  flex-wrap: wrap;
}

.date-input-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.date-input-group label {
  font-weight: 500;
  color: #333;
  white-space: nowrap;
}

.date-input {
  padding: 0.5rem 1rem;
  border: 2px solid #1db954;
  border-radius: 8px;
  background: white;
  color: #333;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.date-input:hover {
  background: #f8f9fa;
  border-color: #1ed760;
}

.date-input:focus {
  outline: none;
  border-color: #1ed760;
  box-shadow: 0 0 0 3px rgba(29, 185, 84, 0.1);
}

.btn-generate {
  padding: 0.5rem 1.5rem;
  background: #1db954;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-generate:hover {
  background: #1ed760;
  transform: translateY(-1px);
}

.btn-clear-dates {
  padding: 0.5rem 1.5rem;
  background: #6c757d;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-clear-dates:hover {
  background: #5a6268;
  transform: translateY(-1px);
}

.stats-summary p {
  margin: 0 0 1rem 0;
  font-size: 1.1rem;
  color: #333;
  font-weight: 500;
}

.spotify-actions {
  margin-top: 1.5rem;
}

.spotify-connect, .spotify-connected {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.info-text {
  color: #666;
  font-size: 0.95rem;
  margin: 0;
}

.success-text {
  color: #1DB954;
  font-weight: 600;
  margin: 0;
}

.button-group {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  justify-content: center;
}

.btn-spotify {
  background: #1DB954;
  color: white;
  font-size: 1.1rem;
  padding: 1rem 2rem;
}

.btn-spotify:hover:not(:disabled) {
  background: #1ed760;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(29, 185, 84, 0.4);
}

.btn-create-playlist {
  background: linear-gradient(135deg, #1DB954, #1ed760);
  color: white;
  font-size: 1rem;
  padding: 0.875rem 1.75rem;
}

.btn-create-playlist:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(29, 185, 84, 0.4);
}

.btn-disconnect {
  background: #6c757d;
  color: white;
}

.btn-disconnect:hover {
  background: #5a6268;
}

.playlist-success {
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: linear-gradient(135deg, #d4edda, #c3e6cb);
  border-radius: 12px;
  border-left: 4px solid #1DB954;
  text-align: center;
}

.playlist-success h3 {
  color: #155724;
  margin: 0 0 0.5rem 0;
}

.playlist-success p {
  color: #155724;
  margin: 0 0 1rem 0;
}

.btn-open-spotify {
  background: #1DB954;
  color: white;
  display: inline-block;
  text-decoration: none;
}

.btn-open-spotify:hover {
  background: #1ed760;
}

.tracks-table-container {
  overflow-x: auto;
}

.tracks-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.95rem;
}

.tracks-table thead {
  background: #f8f9fa;
  position: sticky;
  top: 0;
  z-index: 10;
}

.tracks-table th {
  padding: 1rem 0.75rem;
  text-align: left;
  font-weight: 600;
  color: #333;
  border-bottom: 2px solid #dee2e6;
}

.tracks-table td {
  padding: 1rem 0.75rem;
  border-bottom: 1px solid #e9ecef;
}

.track-row:hover {
  background: #f8f9fa;
  transition: background 0.2s;
}

.rank-col {
  width: 60px;
  text-align: center;
}

.track-col {
  min-width: 250px;
  font-weight: 500;
}

.artist-col {
  min-width: 200px;
  color: #666;
}

.album-col {
  min-width: 200px;
  color: #888;
  font-size: 0.9rem;
}

.plays-col, .hours-col {
  width: 100px;
  text-align: center;
}

.rank-badge {
  display: inline-block;
  width: 32px;
  height: 32px;
  line-height: 32px;
  border-radius: 50%;
  background: #e9ecef;
  color: #666;
  font-weight: 600;
  font-size: 0.9rem;
}

.rank-badge.gold {
  background: linear-gradient(135deg, #FFD700, #FFA500);
  color: white;
  box-shadow: 0 2px 8px rgba(255, 215, 0, 0.4);
}

.rank-badge.silver {
  background: linear-gradient(135deg, #C0C0C0, #A8A8A8);
  color: white;
  box-shadow: 0 2px 8px rgba(192, 192, 192, 0.4);
}

.rank-badge.bronze {
  background: linear-gradient(135deg, #CD7F32, #B8860B);
  color: white;
  box-shadow: 0 2px 8px rgba(205, 127, 50, 0.4);
}

.rank-badge.top-10 {
  background: #1DB954;
  color: white;
}

.track-name {
  color: #000;
  font-weight: 500;
}

.play-count {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  background: #e7f5ff;
  color: #1971c2;
  border-radius: 12px;
  font-weight: 600;
}

.hours-count {
  color: #666;
  font-weight: 500;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 25px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 500;
  text-decoration: none;
  display: inline-block;
  transition: all 0.3s;
}

.btn-primary {
  background: #1DB954;
  color: white;
}

.btn-primary:hover {
  background: #1ed760;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(29, 185, 84, 0.3);
}

.btn-secondary {
  background: #f8f9fa;
  color: #333;
}

.btn-secondary:hover {
  background: #e9ecef;
}

@media (max-width: 768px) {
  .top-tracks {
    padding: 1rem;
  }

  .top-tracks-header {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }

  .tracks-table {
    font-size: 0.85rem;
  }

  .tracks-table th,
  .tracks-table td {
    padding: 0.5rem 0.5rem;
  }

  .album-col {
    display: none;
  }
}
</style>
