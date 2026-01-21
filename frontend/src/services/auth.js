import api from './api'

export const authService = {
  async register(username, email, password, passwordConfirm) {
    const response = await api.post('/auth/register/', {
      username,
      email,
      password,
      password_confirm: passwordConfirm
    })
    return response.data
  },

  async login(username, password) {
    const response = await api.post('/auth/login/', {
      username,
      password
    })
    return response.data
  },

  async logout() {
    const response = await api.post('/auth/logout/')
    return response.data
  },

  async getCurrentUser() {
    const response = await api.get('/auth/me/')
    return response.data
  }
}
