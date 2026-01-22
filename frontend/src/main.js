import { createApp } from 'vue'
import { createPinia } from 'pinia'
import './style.css'
import App from './App.vue'
import router from './router'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

app.mount('#app')

// Check authentication in background after mounting
import { useAuthStore } from './stores/auth'
const authStore = useAuthStore()
authStore.checkAuth().catch(() => {
  // Silently fail - user not authenticated
})
