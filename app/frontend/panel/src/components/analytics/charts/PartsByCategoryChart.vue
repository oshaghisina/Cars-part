<template>
  <div class="h-64">
    <canvas ref="chartCanvas"></canvas>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useAnalyticsStore } from '@/stores/analytics'
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  DoughnutController
} from 'chart.js'

// Register Chart.js components
ChartJS.register(ArcElement, Tooltip, Legend, DoughnutController)

// Store
const analyticsStore = useAnalyticsStore()

// Reactive data
const chartCanvas = ref(null)
let chart = null

// Chart configuration
const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom',
      labels: {
        usePointStyle: true,
        padding: 20,
        font: {
          size: 12
        }
      }
    },
    tooltip: {
      callbacks: {
        label: function(context) {
          const label = context.label || ''
          const value = context.parsed
          const total = context.dataset.data.reduce((a, b) => a + b, 0)
          const percentage = ((value / total) * 100).toFixed(1)
          return `${label}: ${value} (${percentage}%)`
        }
      }
    }
  }
}

// Chart colors
const colors = [
  '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', 
  '#9966FF', '#FF9F40', '#FF6384', '#C9CBCF',
  '#4BC0C0', '#FF6384', '#36A2EB', '#FFCE56'
]

// Methods
const createChart = () => {
  if (!chartCanvas.value) return

  const chartData = analyticsStore.chartsData.partsByCategory
  
  if (!chartData) {
    // Show loading state
    chart = new ChartJS(chartCanvas.value, {
      type: 'doughnut',
      data: {
        labels: ['Loading...'],
        datasets: [{
          data: [1],
          backgroundColor: ['#E5E7EB'],
          borderWidth: 0
        }]
      },
      options: {
        ...chartOptions,
        plugins: {
          ...chartOptions.plugins,
          legend: {
            display: false
          }
        }
      }
    })
    return
  }

  const data = {
    labels: chartData.labels || [],
    datasets: [{
      data: chartData.datasets?.[0]?.data || [],
      backgroundColor: colors.slice(0, chartData.labels?.length || 0),
      borderWidth: 2,
      borderColor: '#FFFFFF'
    }]
  }

  if (chart) {
    chart.destroy()
  }

  chart = new ChartJS(chartCanvas.value, {
    type: 'doughnut',
    data,
    options: chartOptions
  })
}

const updateChart = () => {
  if (!chart) return

  const chartData = analyticsStore.chartsData.partsByCategory
  
  if (!chartData) return

  const newData = {
    labels: chartData.labels || [],
    datasets: [{
      data: chartData.datasets?.[0]?.data || [],
      backgroundColor: colors.slice(0, chartData.labels?.length || 0),
      borderWidth: 2,
      borderColor: '#FFFFFF'
    }]
  }

  chart.data = newData
  chart.update('active')
}

// Watch for data changes
watch(() => analyticsStore.chartsData.partsByCategory, () => {
  updateChart()
}, { deep: true })

// Lifecycle
onMounted(() => {
  createChart()
})

onUnmounted(() => {
  if (chart) {
    chart.destroy()
  }
})
</script>
