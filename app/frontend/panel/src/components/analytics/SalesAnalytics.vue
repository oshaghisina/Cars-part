<template>
  <div class="space-y-6">
    <!-- Sales Overview Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <!-- Total Revenue -->
      <div class="metric-card">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div
              class="w-8 h-8 bg-green-100 rounded-md flex items-center justify-center"
            >
              <CurrencyDollarIcon class="w-5 h-5 text-green-600" />
            </div>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Total Revenue</p>
            <p class="text-2xl font-semibold text-gray-900">
              {{ formatCurrency(analytics.total_revenue) }}
            </p>
          </div>
        </div>
      </div>

      <!-- Revenue Growth -->
      <div class="metric-card">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div
              class="w-8 h-8 bg-blue-100 rounded-md flex items-center justify-center"
            >
              <ArrowTrendingUpIcon class="w-5 h-5 text-blue-600" />
            </div>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Revenue Growth</p>
            <p class="text-2xl font-semibold" :class="getRevenueGrowthColor">
              {{ formatPercentage(analytics.revenue_growth) }}
            </p>
          </div>
        </div>
      </div>

      <!-- Total Orders -->
      <div class="metric-card">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div
              class="w-8 h-8 bg-purple-100 rounded-md flex items-center justify-center"
            >
              <ShoppingBagIcon class="w-5 h-5 text-purple-600" />
            </div>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Total Orders</p>
            <p class="text-2xl font-semibold text-gray-900">
              {{ formatNumber(analytics.total_orders) }}
            </p>
          </div>
        </div>
      </div>

      <!-- Average Order Value -->
      <div class="metric-card">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div
              class="w-8 h-8 bg-yellow-100 rounded-md flex items-center justify-center"
            >
              <ChartBarIcon class="w-5 h-5 text-yellow-600" />
            </div>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Avg Order Value</p>
            <p class="text-2xl font-semibold text-gray-900">
              {{ formatCurrency(getAverageOrderValue) }}
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Charts Row -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Revenue Trend -->
      <div class="chart-container">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-medium text-gray-900">Revenue Trend</h3>
          <div class="flex items-center space-x-2">
            <select
              v-model="chartPeriod"
              class="text-sm border-gray-300 rounded-md"
              @change="onChartPeriodChange"
            >
              <option value="7d">7 days</option>
              <option value="30d">30 days</option>
              <option value="90d">90 days</option>
              <option value="1y">1 year</option>
            </select>
            <button
              :disabled="loading"
              class="text-sm text-blue-600 hover:text-blue-800 disabled:opacity-50"
              @click="$emit('refresh')"
            >
              Refresh
            </button>
          </div>
        </div>
        <div v-if="loading" class="h-64 flex items-center justify-center">
          <div
            class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"
          ></div>
        </div>
        <div v-else class="h-64">
          <RevenueTrendChart :period="chartPeriod" />
        </div>
      </div>

      <!-- Order Status Distribution -->
      <div class="chart-container">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-medium text-gray-900">
            Order Status Distribution
          </h3>
          <button
            :disabled="loading"
            class="text-sm text-blue-600 hover:text-blue-800 disabled:opacity-50"
            @click="$emit('refresh')"
          >
            Refresh
          </button>
        </div>
        <div v-if="loading" class="h-64 flex items-center justify-center">
          <div
            class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"
          ></div>
        </div>
        <div v-else class="h-64">
          <OrderStatusChart :data="analytics.status_distribution" />
        </div>
      </div>
    </div>

    <!-- Top Customers Table -->
    <div class="chart-container">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-medium text-gray-900">Top Customers</h3>
        <button
          :disabled="loading"
          class="text-sm text-blue-600 hover:text-blue-800 disabled:opacity-50"
          @click="$emit('refresh')"
        >
          Refresh
        </button>
      </div>

      <div v-if="loading" class="space-y-3">
        <div v-for="i in 5" :key="i" class="loading-skeleton h-12"></div>
      </div>

      <div v-else class="overflow-hidden">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                Customer
              </th>
              <th
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                Total Revenue
              </th>
              <th
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                Orders
              </th>
              <th
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                Avg Order Value
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr
              v-for="customer in analytics.top_customers"
              :key="customer.customer_name"
            >
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div class="flex-shrink-0 h-8 w-8">
                    <div
                      class="h-8 w-8 rounded-full bg-gray-200 flex items-center justify-center"
                    >
                      <UserIcon class="h-4 w-4 text-gray-600" />
                    </div>
                  </div>
                  <div class="ml-4">
                    <div class="text-sm font-medium text-gray-900">
                      {{ customer.customer_name }}
                    </div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {{ formatCurrency(customer.total_revenue) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {{ formatNumber(customer.order_count) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {{
                  formatCurrency(customer.total_revenue / customer.order_count)
                }}
              </td>
            </tr>
          </tbody>
        </table>

        <div
          v-if="analytics.top_customers.length === 0"
          class="text-center py-8"
        >
          <UserIcon class="mx-auto h-12 w-12 text-gray-400" />
          <h3 class="mt-2 text-sm font-medium text-gray-900">
            No customers found
          </h3>
          <p class="mt-1 text-sm text-gray-500">
            No customer data available for the selected period.
          </p>
        </div>
      </div>
    </div>

    <!-- Revenue Trends Table -->
    <div class="chart-container">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-medium text-gray-900">Revenue Trends</h3>
        <button
          :disabled="loading"
          class="text-sm text-blue-600 hover:text-blue-800 disabled:opacity-50"
          @click="$emit('refresh')"
        >
          Refresh
        </button>
      </div>

      <div v-if="loading" class="space-y-3">
        <div v-for="i in 7" :key="i" class="loading-skeleton h-10"></div>
      </div>

      <div v-else class="overflow-hidden">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                Date
              </th>
              <th
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                Revenue
              </th>
              <th
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                Orders
              </th>
              <th
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                Avg Order Value
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr
              v-for="trend in analytics.revenue_trends.slice(-7)"
              :key="trend.date"
            >
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {{ formatDate(trend.date) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {{ formatCurrency(trend.revenue) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {{ formatNumber(trend.orders) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {{ formatCurrency(trend.revenue / trend.orders) }}
              </td>
            </tr>
          </tbody>
        </table>

        <div
          v-if="analytics.revenue_trends.length === 0"
          class="text-center py-8"
        >
          <ChartBarIcon class="mx-auto h-12 w-12 text-gray-400" />
          <h3 class="mt-2 text-sm font-medium text-gray-900">
            No revenue data
          </h3>
          <p class="mt-1 text-sm text-gray-500">
            No revenue trends available for the selected period.
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import {
  CurrencyDollarIcon,
  ArrowTrendingUpIcon,
  ShoppingBagIcon,
  ChartBarIcon,
  UserIcon,
} from "@heroicons/vue/24/outline";
import RevenueTrendChart from "./charts/RevenueTrendChart.vue";
import OrderStatusChart from "./charts/OrderStatusChart.vue";

// Props
const props = defineProps({
  analytics: {
    type: Object,
    required: true,
  },
  loading: {
    type: Boolean,
    default: false,
  },
  period: {
    type: String,
    default: "30d",
  },
});

// Emits
const emit = defineEmits(["refresh", "period-change"]);

// Reactive data
const chartPeriod = ref(props.period);

// Computed
const getAverageOrderValue = computed(() => {
  if (props.analytics.total_orders === 0) return 0;
  return props.analytics.total_revenue / props.analytics.total_orders;
});

const getRevenueGrowthColor = computed(() => {
  const growth = props.analytics.revenue_growth;
  if (growth > 0) return "text-green-600";
  if (growth < 0) return "text-red-600";
  return "text-gray-600";
});

// Methods
const onChartPeriodChange = () => {
  emit("period-change", chartPeriod.value);
};

const formatCurrency = (amount) => {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(amount);
};

const formatNumber = (value) => {
  return new Intl.NumberFormat("en-US").format(value);
};

const formatPercentage = (value, decimals = 1) => {
  return `${value.toFixed(decimals)}%`;
};

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
  });
};
</script>
