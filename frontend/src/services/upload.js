import api from './api'

export const uploadService = {
  async uploadSpotifyData(file, onUploadProgress) {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await api.post('/upload/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      onUploadProgress
    })
    return response.data
  },

  async getUploads() {
    const response = await api.get('/upload/list/')
    return response.data
  },

  async getStats() {
    const response = await api.get('/upload/stats/')
    return response.data
  },

  async getTopTracks(startDate = '', endDate = '') {
    const params = {}
    if (startDate) params.start_date = startDate
    if (endDate) params.end_date = endDate
    
    const response = await api.get('/upload/top-tracks/', { params })
    return response.data
  },

  async generateCustomPlaylist(startDate = '', endDate = '', limit = 50) {
    const params = { limit }
    if (startDate) params.start_date = startDate
    if (endDate) params.end_date = endDate
    
    const response = await api.get('/upload/generate-playlist/', { params })
    return response.data
  },

  async getMonthlyStats() {
    const response = await api.get('/upload/monthly-stats/')
    return response.data
  },

  async deleteAllData() {
    const response = await api.delete('/upload/delete-all/')
    return response.data
  }
}
