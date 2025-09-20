<template>
  <div class="h-64">
    <canvas ref="chartCanvas"></canvas>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  BarController
} from 'chart.js'

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  BarController
)

// Props
const props = defineProps({
  data: {
    type: Array,
    default: () => []
  }
})

// Reactive data
const chartCanvas = ref(null)
let chart = null

// Chart configuration
const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false
    },
    tooltip: {
      callbacks: {
        label: function(context) {
          const label = context.label || ''
          const value = context.parsed.y
          return `${label}: ${value} parts`
        }
      }
    }
  },
  scales: {
    x: {
      display: true,
      title: {
        display: true,
        text: 'Brand'
      },
      grid: {
        display: false
      }
    },
    y: {
      display: true,
      title: {
        display: true,
        text: 'Number of Parts'
      },
      beginAtZero: true,
      ticks: {
        stepSize: 1
      }
    }
  }
}

// Methods
const createChart = () => {
  if (!chartCanvas.value) return

  const brandData = props.data.slice(0, 10) // Show top 10 brands
  
  if (!brandData || brandData.length === 0) {
    // Show empty state
    chart = new ChartJS(chartCanvas.value, {
      type: 'bar',
      data: {
        labels: ['No data available'],
        datasets: [{
          data: [0],
          backgroundColor: '#E5E7EB',
          borderWidth: 0
        }]
      },
      options: {
        ...chartOptions,
        plugins: {
          ...chartOptions.plugins,
          tooltip: {
            enabled: false
          }
        }
      }
    })
    return
  }

  const labels = brandData.map(item => item.brand)
  const values = brandData.map(item => item.count)

  const data = {
    labels,
    datasets: [{
      label: 'Parts Count',
      data: values,
      backgroundColor: '#3B82F6',
      borderColor: '#2563EB',
      borderWidth: 1
    }]
  }

  if (chart) {
    chart.destroy()
  }

  chart = new ChartJS(chartCanvas.value, {
    type: 'bar',
    data,
    options: chartOptions
  })
}

const updateChart = () => {
  if (!chart) return

  const brandData = props.data.slice(0, 10) // Show top 10 brands
  
  if (!brandData || brandData.length === 0) {
    chart.data = {
      labels: ['No data available'],
      datasets: [{
        data: [0],
        backgroundColor: '#E5E7EB',
        borderWidth: 0
      }]
    }
    chart.update('active')
    return
  }

  const labels = brandData.map(item => item.brand)
  const values = brandData.map(item => item.count)

  const newData = {
    labels,
    datasets: [{
      label: 'Parts Count',
      data: values,
      backgroundColor: '#3B82F6',
      borderColor: '#2563EB',
      borderWidth: 1
    }]
  }

  chart.data = newData
  chart.update('active')
}

// Watch for data changes
watch(() => props.data, () => {
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
