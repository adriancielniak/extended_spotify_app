<template>
  <div class="register-container">
    <div class="register-card">
      <h2>Zarejestruj się</h2>
      
      <div v-if="errorMessage" class="error-message">
        {{ errorMessage }}
      </div>

      <form @submit.prevent="handleRegister">
        <div class="form-group">
          <label for="username">Nazwa użytkownika</label>
          <input
            id="username"
            v-model="username"
            type="text"
            required
            placeholder="Wybierz nazwę użytkownika"
          />
        </div>

        <div class="form-group">
          <label for="email">Email</label>
          <input
            id="email"
            v-model="email"
            type="email"
            required
            placeholder="Wprowadź email"
          />
        </div>

        <div class="form-group">
          <label for="password">Hasło</label>
          <input
            id="password"
            v-model="password"
            type="password"
            required
            minlength="8"
            placeholder="Wprowadź hasło (min. 8 znaków)"
          />
        </div>

        <div class="form-group">
          <label for="passwordConfirm">Potwierdź hasło</label>
          <input
            id="passwordConfirm"
            v-model="passwordConfirm"
            type="password"
            required
            minlength="8"
            placeholder="Potwierdź hasło"
          />
        </div>

        <button type="submit" class="btn btn-primary" :disabled="authStore.loading">
          {{ authStore.loading ? 'Rejestracja...' : 'Zarejestruj się' }}
        </button>
      </form>

      <p class="login-link">
        Masz już konto? <router-link to="/login">Zaloguj się</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const username = ref('')
const email = ref('')
const password = ref('')
const passwordConfirm = ref('')

const errorMessage = computed(() => {
  if (authStore.error) {
    if (typeof authStore.error === 'string') {
      return authStore.error
    }
    // Handle object errors from Django
    const errors = []
    for (const [field, messages] of Object.entries(authStore.error)) {
      if (Array.isArray(messages)) {
        errors.push(`${field}: ${messages.join(', ')}`)
      } else {
        errors.push(`${field}: ${messages}`)
      }
    }
    return errors.join('\n')
  }
  return null
})

async function handleRegister() {
  try {
    await authStore.register(
      username.value,
      email.value,
      password.value,
      passwordConfirm.value
    )
    router.push('/dashboard')
  } catch (error) {
    console.error('Registration error:', error)
  }
}
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 80vh;
  padding: 2rem;
}

.register-card {
  background: white;
  padding: 2rem;
  border-radius: 1rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
}

h2 {
  text-align: center;
  margin-bottom: 2rem;
  color: #1db954;
}

.form-group {
  margin-bottom: 1.5rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 0.5rem;
  font-size: 1rem;
}

input:focus {
  outline: none;
  border-color: #1db954;
}

.btn {
  width: 100%;
  padding: 1rem;
  border: none;
  border-radius: 0.5rem;
  font-size: 1rem;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-primary {
  background-color: #1db954;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #1ed760;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error-message {
  background-color: #fee;
  color: #c33;
  padding: 1rem;
  border-radius: 0.5rem;
  margin-bottom: 1rem;
  white-space: pre-line;
}

.login-link {
  text-align: center;
  margin-top: 1rem;
}

.login-link a {
  color: #1db954;
  text-decoration: none;
  font-weight: bold;
}

.login-link a:hover {
  text-decoration: underline;
}
</style>
