<template>
  <div class="charts-container">
    <div class="page-header">
      <h1>📊 Statystyki i Wykresy</h1>
      <p class="subtitle">Analizuj swoje nawyki słuchania muzyki</p>
    </div>

    <div v-if="loading" class="loading-container">
      <div class="spinner"></div>
      <p>Ładowanie statystyk...</p>
    </div>

    <div v-else-if="error" class="error-container">
      <p class="error-message">{{ error }}</p>
      <button @click="loadMonthlyStats" class="btn-retry">Spróbuj ponownie</button>
    </div>

    <div v-else class="charts-section">
      <!-- Monthly Listening Chart -->
      <div class="chart-card">
        <div class="chart-header">
          <h2>🎵 Miesięczne słuchanie muzyki</h2>
          <div class="chart-info">
            <span class="info-badge">{{ monthlyData.length }} miesięcy</span>
            <span class="info-badge total">{{ totalHours }} godzin łącznie</span>
          </div>
        </div>
        
        <div v-if="monthlyData.length === 0" class="no-data">
          <p>Brak danych do wyświetlenia</p>
          <p class="hint">Prześlij swoje dane Spotify, aby zobaczyć statystyki</p>
        </div>

        <div v-else class="chart-wrapper">
          <canvas ref="monthlyChart" id="monthlyChart"></canvas>
        </div>

        <div v-if="monthlyData.length > 0" class="chart-stats">
          <div class="stat-box">
            <span class="stat-label">Średnio miesięcznie:</span>
            <span class="stat-value">{{ averageMonthly }} h</span>
          </div>
          <div class="stat-box">
            <span class="stat-label">Najaktywniejszy miesiąc:</span>
            <span class="stat-value">{{ mostActiveMonth }}</span>
          </div>
          <div class="stat-box">
            <span class="stat-label">Najwięcej godzin:</span>
            <span class="stat-value">{{ maxHours }} h</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { uploadService } from '../services/upload'
import {
  Chart,
  CategoryScale,
  LinearScale,
  BarElement,
  BarController,
  Title,
  Tooltip,
  Legend
} from 'chart.js'

// Register Chart.js components
Chart.register(
  CategoryScale,
  LinearScale,
  BarElement,
  BarController,
  Title,
  Tooltip,
  Legend
)

const monthlyData = ref([])
const loading = ref(true)
const error = ref('')
const monthlyChart = ref(null)
let chartInstance = null

const totalHours = computed(() => {
  const total = monthlyData.value.reduce((sum, item) => sum + item.total_hours, 0)
  return Math.round(total)
})

const averageMonthly = computed(() => {
  if (monthlyData.value.length === 0) return 0
  return Math.round(totalHours.value / monthlyData.value.length)
})

const mostActiveMonth = computed(() => {
  if (monthlyData.value.length === 0) return '-'
  const max = monthlyData.value.reduce((prev, current) => 
    (prev.total_hours > current.total_hours) ? prev : current
  )
  return max.month_label
})

const maxHours = computed(() => {
  if (monthlyData.value.length === 0) return 0
  return Math.max(...monthlyData.value.map(d => d.total_hours))
})

const loadMonthlyStats = async () => {
  loading.value = true
  error.value = ''
  
  try {
    console.log('Loading monthly stats...')
    const data = await uploadService.getMonthlyStats()
    console.log('Received data:', data)
    console.log('Data length:', data.length)
    monthlyData.value = data
    
    // Wait for DOM update with multiple ticks
    await nextTick()
    await nextTick()
    
    // Additional delay to ensure canvas is rendered
    setTimeout(() => {
      console.log('Creating chart...')
      createChart()
    }, 100)
  } catch (err) {
    console.error('Error loading monthly stats:', err)
    error.value = err.response?.data?.error || 'Wystąpił błąd podczas ładowania statystyk'
  } finally {
    loading.value = false
  }
}

const createChart = () => {
  console.log('=== CREATE CHART START ===')
  console.log('Canvas ref:', monthlyChart.value)
  console.log('Data length:', monthlyData.value.length)
  
  if (!monthlyChart.value) {
    console.error('Canvas element is null!')
    return
  }
  
  if (monthlyData.value.length === 0) {
    console.error('No data available!')
    return
  }
  
  // Destroy existing chart
  if (chartInstance) {
    console.log('Destroying existing chart')
    chartInstance.destroy()
    chartInstance = null
  }

  const ctx = monthlyChart.value.getContext('2d')
  
  if (!ctx) {
    console.error('Could not get 2d context from canvas')
    return
  }
  
  const labels = monthlyData.value.map(d => d.month_label)
  const hours = monthlyData.value.map(d => d.total_hours)
  
  console.log('Labels:', labels.slice(0, 3), '...')
  console.log('Hours:', hours.slice(0, 3), '...')
  
  try {
    chartInstance = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: 'Godziny słuchania',
          data: hours,
          backgroundColor: '#1db954',
          borderColor: '#1db954',
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: true
          }
        }
      }
    })
    
    console.log('Chart created successfully!')
    console.log('Chart data:', chartInstance.data)
    console.log('=== CREATE CHART END ===')
  } catch (err) {
    console.error('Error creating chart:', err)
  }
}

onMounted(() => {
  loadMonthlyStats()
})
</script>

<style scoped>
.charts-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.page-header {
  text-align: center;
  margin-bottom: 40px;
}

.page-header h1 {
  font-size: 2.5rem;
  margin-bottom: 10px;
  color: #1db954;
}

.subtitle {
  font-size: 1.1rem;
  color: #666;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #1db954;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-container {
  text-align: center;
  padding: 60px 20px;
}

.error-message {
  color: #dc3545;
  font-size: 1.1rem;
  margin-bottom: 20px;
}

.btn-retry {
  background-color: #1db954;
  color: white;
  border: none;
  padding: 12px 30px;
  border-radius: 25px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.3s;
}

.btn-retry:hover {
  background-color: #1ed760;
}

.charts-section {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.chart-card {
  background: white;
  border-radius: 16px;
  padding: 30px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
  flex-wrap: wrap;
  gap: 15px;
}

.chart-header h2 {
  margin: 0;
  color: #333;
  font-size: 1.8rem;
}

.chart-info {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.info-badge {
  background-color: #e8f5e9;
  color: #2e7d32;
  padding: 8px 16px;
  border-radius: 20px;
  font-weight: 600;
  font-size: 0.9rem;
}

.info-badge.total {
  background-color: #1db954;
  color: white;
}

.no-data {
  text-align: center;
  padding: 60px 20px;
  color: #666;
}

.no-data p {
  font-size: 1.2rem;
  margin: 10px 0;
}

.hint {
  color: #999;
  font-size: 1rem;
}

.chart-wrapper {
  margin: 20px 0;
  padding: 20px 0;
  min-height: 400px;
  position: relative;
  background-color: #ffffff;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
}

.chart-wrapper canvas {
  max-height: 400px;
  width: 100% !important;
  height: 400px !important;
  display: block !important;
}

.chart-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-top: 30px;
  padding-top: 30px;
  border-top: 2px solid #f0f0f0;
}

.stat-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
  background: linear-gradient(135deg, #f8f9fa, #e9ecef);
  border-radius: 12px;
  transition: transform 0.2s;
}

.stat-box:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stat-label {
  font-size: 0.9rem;
  color: #666;
  margin-bottom: 8px;
  text-align: center;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: bold;
  color: #1db954;
}

@media (max-width: 768px) {
  .page-header h1 {
    font-size: 2rem;
  }

  .chart-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .chart-wrapper {
    min-height: 300px;
  }

  .chart-wrapper canvas {
    max-height: 300px;
    height: 300px !important;
  }

  .chart-stats {
    grid-template-columns: 1fr;
  }
}
</style>
