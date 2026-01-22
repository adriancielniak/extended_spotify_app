import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import Home from '../views/Home.vue'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import Dashboard from '../views/Dashboard.vue'
import Upload from '../views/Upload.vue'
import TopTracks from '../views/TopTracks.vue'
import GeneratePlaylist from '../views/GeneratePlaylist.vue'
import Charts from '../views/Charts.vue'
import SpotifyCallback from '../views/SpotifyCallback.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/register',
    name: 'Register',
    component: Register
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: Dashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/upload',
    name: 'Upload',
    component: Upload,
    meta: { requiresAuth: true }
  },
  {
    path: '/top-tracks',
    name: 'TopTracks',
    component: TopTracks,
    meta: { requiresAuth: true }
  },
  {
    path: '/generate-playlist',
    name: 'GeneratePlaylist',
    component: GeneratePlaylist,
    meta: { requiresAuth: true }
  },
  {
    path: '/charts',
    name: 'Charts',
    component: Charts,
    meta: { requiresAuth: true }
  },
  {
    path: '/spotify/callback',
    name: 'SpotifyCallback',
    component: SpotifyCallback,
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guard
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else {
    next()
  }
})

export default router
