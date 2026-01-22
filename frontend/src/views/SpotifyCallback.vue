<template>
  <div class="spotify-callback">
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>Łączenie z kontem Spotify...</p>
    </div>
    <div v-else-if="error" class="error">
      <h2>Wystąpił błąd</h2>
      <p>{{ error }}</p>
      <button @click="goToTopTracks" class="btn">Spróbuj ponownie</button>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '../services/api'

export default {
  name: 'SpotifyCallback',
  setup() {
    const router = useRouter()
    const route = useRoute()
    const loading = ref(true)
    const error = ref(null)

    const goToTopTracks = () => {
      router.push('/top-tracks')
    }

    const exchangeCode = async (code) => {
      try {
        const response = await api.post('/auth/spotify/exchange-code/', { code })
        
        if (response.data.success) {
          // Redirect to top-tracks with success message
          router.push('/top-tracks?spotify_connected=true')
        } else {
          error.value = 'Nie udało się połączyć z kontem Spotify'
          loading.value = false
        }
      } catch (err) {
        console.error('Error exchanging code:', err)
        error.value = err.response?.data?.error || 'Wystąpił błąd podczas łączenia z Spotify'
        loading.value = false
      }
    }

    onMounted(() => {
      // Get code and state from URL query parameters
      const code = route.query.code
      const errorParam = route.query.error
      const state = route.query.state

      if (errorParam) {
        error.value = `Spotify OAuth error: ${errorParam}`
        loading.value = false
        return
      }

      if (!code) {
        error.value = 'Brak kodu autoryzacji w URL'
        loading.value = false
        return
      }

      // Exchange the code for access token
      exchangeCode(code)
    })

    return {
      loading,
      error,
      goToTopTracks
    }
  }
}
</script>

<style scoped>
.spotify-callback {
  max-width: 600px;
  margin: 50px auto;
  padding: 20px;
  text-align: center;
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #1db954;
  border-radius: 50%;
  width: 50px;
  height: 50px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error {
  background-color: #fee;
  border: 1px solid #f88;
  border-radius: 8px;
  padding: 20px;
}

.error h2 {
  color: #c00;
  margin-bottom: 10px;
}

.btn {
  background-color: #1db954;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 20px;
  cursor: pointer;
  font-size: 16px;
  margin-top: 20px;
}

.btn:hover {
  background-color: #1ed760;
}
</style>
