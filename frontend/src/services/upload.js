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
  }
}
