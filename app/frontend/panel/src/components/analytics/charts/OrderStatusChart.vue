<template>
  <div class="h-64">
    <canvas ref="chartCanvas"></canvas>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from "vue";
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  DoughnutController,
} from "chart.js";

// Register Chart.js components
ChartJS.register(ArcElement, Tooltip, Legend, DoughnutController);

// Props
const props = defineProps({
  data: {
    type: Object,
    default: () => ({}),
  },
});

// Reactive data
const chartCanvas = ref(null);
let chart = null;

// Chart configuration
const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: "bottom",
      labels: {
        usePointStyle: true,
        padding: 20,
        font: {
          size: 12,
        },
      },
    },
    tooltip: {
      callbacks: {
        label(context) {
          const label = context.label || "";
          const value = context.parsed;
          const total = context.dataset.data.reduce((a, b) => a + b, 0);
          const percentage = ((value / total) * 100).toFixed(1);
          return `${label}: ${value} (${percentage}%)`;
        },
      },
    },
  },
};

// Status colors mapping
const statusColors = {
  pending: "#F59E0B",
  completed: "#10B981",
  cancelled: "#EF4444",
  processing: "#3B82F6",
  shipped: "#8B5CF6",
  delivered: "#06B6D4",
};

// Methods
const createChart = () => {
  if (!chartCanvas.value) return;

  const statusData = props.data;

  if (!statusData || Object.keys(statusData).length === 0) {
    // Show empty state
    chart = new ChartJS(chartCanvas.value, {
      type: "doughnut",
      data: {
        labels: ["No data available"],
        datasets: [
          {
            data: [1],
            backgroundColor: ["#E5E7EB"],
            borderWidth: 0,
          },
        ],
      },
      options: {
        ...chartOptions,
        plugins: {
          ...chartOptions.plugins,
          legend: {
            display: false,
          },
        },
      },
    });
    return;
  }

  const labels = Object.keys(statusData);
  const values = Object.values(statusData);
  const backgroundColor = labels.map(
    (status) => statusColors[status.toLowerCase()] || "#6B7280",
  );

  const data = {
    labels,
    datasets: [
      {
        data: values,
        backgroundColor,
        borderWidth: 2,
        borderColor: "#FFFFFF",
      },
    ],
  };

  if (chart) {
    chart.destroy();
  }

  chart = new ChartJS(chartCanvas.value, {
    type: "doughnut",
    data,
    options: chartOptions,
  });
};

const updateChart = () => {
  if (!chart) return;

  const statusData = props.data;

  if (!statusData || Object.keys(statusData).length === 0) {
    chart.data = {
      labels: ["No data available"],
      datasets: [
        {
          data: [1],
          backgroundColor: ["#E5E7EB"],
          borderWidth: 0,
        },
      ],
    };
    chart.update("active");
    return;
  }

  const labels = Object.keys(statusData);
  const values = Object.values(statusData);
  const backgroundColor = labels.map(
    (status) => statusColors[status.toLowerCase()] || "#6B7280",
  );

  const newData = {
    labels,
    datasets: [
      {
        data: values,
        backgroundColor,
        borderWidth: 2,
        borderColor: "#FFFFFF",
      },
    ],
  };

  chart.data = newData;
  chart.update("active");
};

// Watch for data changes
watch(
  () => props.data,
  () => {
    updateChart();
  },
  { deep: true },
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
