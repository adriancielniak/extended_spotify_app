import { defineStore } from 'pinia'
import { ref } from 'vue'
import { authService } from '../services/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const isAuthenticated = ref(false)
  const loading = ref(false)
  const error = ref(null)

  async function login(username, password) {
    loading.value = true
    error.value = null
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

  async function register(username, email, password, passwordConfirm) {
    loading.value = true
    error.value = null
    try {
      const userData = await authService.register(username, email, password, passwordConfirm)
      user.value = userData
      isAuthenticated.value = true
      return userData
    } catch (err) {
      error.value = err.response?.data || 'Registration failed'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function logout() {
    try {
      await authService.logout()
      user.value = null
      isAuthenticated.value = false
    } catch (err) {
      console.error('Logout error:', err)
    }
  }

  async function fetchCurrentUser() {
    loading.value = true
    try {
      const userData = await authService.getCurrentUser()
      user.value = userData
      isAuthenticated.value = true
      return userData
    } catch (err) {
      user.value = null
      isAuthenticated.value = false
      // Don't throw error on initial check
      return null
    } finally {
      loading.value = false
    }
  }

  async function checkAuth() {
    // Check if user is authenticated on app startup
    try {
      await fetchCurrentUser()
    } catch (err) {
      // Silently fail - user is not authenticated
    }
  }

  return {
    user,
    isAuthenticated,
    loading,
    error,
    login,
    register,
    logout,
    fetchCurrentUser,
    checkAuth
  }
})
