<template>
  <div class="upload">
    <div class="upload-container">
      <h1>Prześlij dane Spotify</h1>
      <p class="instruction">
        Prześlij swój plik ZIP z danymi ze Spotify. 
        <a href="https://www.spotify.com/pl/account/privacy/" target="_blank">
          Pobierz swoje dane ze Spotify
        </a>
      </p>

      <div v-if="uploadError" class="error-message">
        {{ uploadError }}
      </div>

      <div v-if="uploadSuccess" class="success-message">
        {{ uploadSuccess }}
      </div>

      <div class="upload-area" @drop.prevent="handleDrop" @dragover.prevent>
        <input
          ref="fileInput"
          type="file"
          accept=".zip"
          @change="handleFileSelect"
          style="display: none"
        />
        
        <div v-if="!selectedFile" class="upload-prompt" @click="$refs.fileInput.click()">
          <div class="upload-icon">📁</div>
          <p>Przeciągnij i upuść plik ZIP tutaj lub kliknij, aby wybrać</p>
        </div>

        <div v-else class="file-selected">
          <div class="file-info">
            <span class="file-name">{{ selectedFile.name }}</span>
            <span class="file-size">{{ formatSize(selectedFile.size) }}</span>
          </div>
          <button @click="clearFile" class="btn-clear">✕</button>
        </div>
      </div>

      <div v-if="uploading" class="upload-progress">
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: uploadProgress + '%' }"></div>
        </div>
        <p>Przesyłanie: {{ uploadProgress }}%</p>
      </div>

      <div class="actions">
        <button
          v-if="selectedFile && !uploading"
          @click="handleUpload"
          class="btn btn-primary"
        >
          Prześlij
        </button>
        <router-link to="/dashboard" class="btn btn-secondary">
          Powrót do dashboardu
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { uploadService } from '../services/upload'

const router = useRouter()

const fileInput = ref(null)
const selectedFile = ref(null)
const uploading = ref(false)
const uploadProgress = ref(0)
const uploadError = ref(null)
const uploadSuccess = ref(null)

function handleFileSelect(event) {
  const file = event.target.files[0]
  if (file && file.name.endsWith('.zip')) {
    selectedFile.value = file
    uploadError.value = null
  } else {
    uploadError.value = 'Proszę wybrać plik ZIP'
  }
}

function handleDrop(event) {
  const file = event.dataTransfer.files[0]
  if (file && file.name.endsWith('.zip')) {
    selectedFile.value = file
    uploadError.value = null
  } else {
    uploadError.value = 'Proszę wybrać plik ZIP'
  }
}

function clearFile() {
  selectedFile.value = null
  uploadProgress.value = 0
  uploadError.value = null
  uploadSuccess.value = null
}

async function handleUpload() {
  if (!selectedFile.value) return

  uploading.value = true
  uploadError.value = null
  uploadSuccess.value = null

  try {
    await uploadService.uploadSpotifyData(
      selectedFile.value,
      (progressEvent) => {
        uploadProgress.value = Math.round(
          (progressEvent.loaded * 100) / progressEvent.total
        )
      }
    )

    uploadSuccess.value = 'Plik został pomyślnie przesłany i przetworzony!'
    selectedFile.value = null
    uploadProgress.value = 0

    setTimeout(() => {
      router.push('/dashboard')
    }, 2000)
  } catch (error) {
    uploadError.value = error.response?.data?.error || 'Błąd podczas przesyłania pliku'
  } finally {
    uploading.value = false
  }
}

function formatSize(bytes) {
  const mb = bytes / (1024 * 1024)
  return `${mb.toFixed(2)} MB`
}
</script>

<style scoped>
.upload {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
}

.upload-container {
  background: white;
  padding: 2rem;
  border-radius: 1rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

h1 {
  color: #1db954;
  margin-bottom: 1rem;
}

.instruction {
  margin-bottom: 2rem;
  color: #666;
}

.instruction a {
  color: #1db954;
  text-decoration: none;
}

.instruction a:hover {
  text-decoration: underline;
}

.upload-area {
  border: 2px dashed #ddd;
  border-radius: 1rem;
  padding: 3rem;
  margin-bottom: 2rem;
  transition: border-color 0.2s;
}

.upload-area:hover {
  border-color: #1db954;
}

.upload-prompt {
  text-align: center;
  cursor: pointer;
}

.upload-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.file-selected {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.file-info {
  display: flex;
  flex-direction: column;
}

.file-name {
  font-weight: bold;
  margin-bottom: 0.5rem;
}

.file-size {
  color: #666;
  font-size: 0.875rem;
}

.btn-clear {
  background: #e74c3c;
  color: white;
  border: none;
  border-radius: 50%;
  width: 2rem;
  height: 2rem;
  cursor: pointer;
  font-size: 1.2rem;
}

.upload-progress {
  margin-bottom: 2rem;
}

.progress-bar {
  height: 1rem;
  background: #eee;
  border-radius: 0.5rem;
  overflow: hidden;
  margin-bottom: 0.5rem;
}

.progress-fill {
  height: 100%;
  background: #1db954;
  transition: width 0.3s;
}

.actions {
  display: flex;
  gap: 1rem;
}

.btn {
  padding: 1rem 2rem;
  border: none;
  border-radius: 0.5rem;
  font-weight: bold;
  cursor: pointer;
  text-decoration: none;
  display: inline-block;
  transition: background-color 0.2s;
}

.btn-primary {
  background-color: #1db954;
  color: white;
}

.btn-primary:hover {
  background-color: #1ed760;
}

.btn-secondary {
  background-color: #191414;
  color: white;
}

.btn-secondary:hover {
  background-color: #282828;
}

.error-message {
  background-color: #fee;
  color: #c33;
  padding: 1rem;
  border-radius: 0.5rem;
  margin-bottom: 1rem;
}

.success-message {
  background-color: #d4edda;
  color: #155724;
  padding: 1rem;
  border-radius: 0.5rem;
  margin-bottom: 1rem;
}
</style>
