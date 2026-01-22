import api from './api'

export const spotifyService = {
  async getAuthUrl(redirectTo = 'dashboard') {
    const response = await api.get('/auth/spotify/auth-url/', {
      params: { redirect_to: redirectTo }
    })
    return response.data
  },

  async getConnectionStatus() {
    const response = await api.get('/auth/spotify/status/')
    return response.data
  },

  async disconnect() {
    const response = await api.post('/auth/spotify/disconnect/')
    return response.data
  },

  async createPlaylist() {
    const response = await api.post('/upload/create-playlist/')
    return response.data
  }
}
