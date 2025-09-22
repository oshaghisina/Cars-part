<template>
  <div class="h-64">
    <canvas ref="chartCanvas"></canvas>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from "vue";
import { useAnalyticsStore } from "@/stores/analytics";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
  LineController,
} from "chart.js";

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
  LineController,
);

// Props
const props = defineProps({
  period: {
    type: String,
    default: "30d",
  },
});

// Store
const analyticsStore = useAnalyticsStore();

// Reactive data
const chartCanvas = ref(null);
let chart = null;

// Chart configuration
const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  interaction: {
    intersect: false,
    mode: "index",
  },
  plugins: {
    legend: {
      display: false,
    },
    tooltip: {
      mode: "index",
      intersect: false,
      callbacks: {
        label(context) {
          const label = context.dataset.label || "";
          const value = context.parsed.y;
          return `${label}: $${value.toLocaleString()}`;
        },
      },
    },
  },
  scales: {
    x: {
      display: true,
      title: {
        display: true,
        text: "Date",
      },
      grid: {
        display: false,
      },
    },
    y: {
      display: true,
      title: {
        display: true,
        text: "Revenue ($)",
      },
      beginAtZero: true,
      ticks: {
        callback(value) {
          return `$${value.toLocaleString()}`;
        },
      },
    },
  },
};

// Methods
const createChart = () => {
  if (!chartCanvas.value) return;

  const chartData = analyticsStore.chartsData.salesTrend;

  if (!chartData || !chartData.labels || chartData.labels.length === 0) {
    // Show loading state
    chart = new ChartJS(chartCanvas.value, {
      type: "line",
      data: {
        labels: ["No data available"],
        datasets: [
          {
            label: "Revenue",
            data: [0],
            borderColor: "#E5E7EB",
            backgroundColor: "rgba(229, 231, 235, 0.1)",
            borderWidth: 2,
            fill: true,
            tension: 0.1,
          },
        ],
      },
      options: {
        ...chartOptions,
        plugins: {
          ...chartOptions.plugins,
          tooltip: {
            enabled: false,
          },
        },
      },
    });
    return;
  }

  const data = {
    labels: chartData.labels || [],
    datasets: [
      {
        label: "Revenue",
        data: chartData.datasets?.[0]?.data || [],
        borderColor: "#3B82F6",
        backgroundColor: "rgba(59, 130, 246, 0.1)",
        borderWidth: 2,
        fill: true,
        tension: 0.1,
        pointBackgroundColor: "#3B82F6",
        pointBorderColor: "#FFFFFF",
        pointBorderWidth: 2,
        pointRadius: 4,
        pointHoverRadius: 6,
      },
    ],
  };

  if (chart) {
    chart.destroy();
  }

  chart = new ChartJS(chartCanvas.value, {
    type: "line",
    data,
    options: chartOptions,
  });
};

const updateChart = () => {
  if (!chart) return;

  const chartData = analyticsStore.chartsData.salesTrend;

  if (!chartData) return;

  if (!chartData.labels || chartData.labels.length === 0) {
    chart.data = {
      labels: ["No data available"],
      datasets: [
        {
          label: "Revenue",
          data: [0],
          borderColor: "#E5E7EB",
          backgroundColor: "rgba(229, 231, 235, 0.1)",
          borderWidth: 2,
          fill: true,
          tension: 0.1,
        },
      ],
    };
    chart.update("active");
    return;
  }

  const newData = {
    labels: chartData.labels || [],
    datasets: [
      {
        label: "Revenue",
        data: chartData.datasets?.[0]?.data || [],
        borderColor: "#3B82F6",
        backgroundColor: "rgba(59, 130, 246, 0.1)",
        borderWidth: 2,
        fill: true,
        tension: 0.1,
        pointBackgroundColor: "#3B82F6",
        pointBorderColor: "#FFFFFF",
        pointBorderWidth: 2,
        pointRadius: 4,
        pointHoverRadius: 6,
      },
    ],
  };

  chart.data = newData;
  chart.update("active");
};

// Watch for data changes
watch(
  () => analyticsStore.chartsData.salesTrend,
  () => {
    updateChart();
  },
  { deep: true },
);

// Watch for period changes
watch(
  () => props.period,
  () => {
    analyticsStore.fetchSalesTrendChart(props.period);
  },
);

// Lifecycle
onMounted(() => {
  createChart();
});

onUnmounted(() => {
  if (chart) {
    chart.destroy();
  }
});
</script>
