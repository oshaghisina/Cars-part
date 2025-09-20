<template>
  <div class="space-y-6">
    <!-- Key Metrics Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <!-- Total Revenue -->
      <div class="metric-card">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-green-100 rounded-md flex items-center justify-center">
              <CurrencyDollarIcon class="w-5 h-5 text-green-600" />
            </div>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Total Revenue</p>
            <p class="text-2xl font-semibold text-gray-900">
              {{ formatCurrency(metrics.total_revenue) }}
            </p>
          </div>
        </div>
      </div>

      <!-- Total Orders -->
      <div class="metric-card">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-blue-100 rounded-md flex items-center justify-center">
              <ShoppingBagIcon class="w-5 h-5 text-blue-600" />
            </div>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Total Orders</p>
            <p class="text-2xl font-semibold text-gray-900">
              {{ formatNumber(metrics.total_orders) }}
            </p>
          </div>
        </div>
      </div>

      <!-- Total Parts -->
      <div class="metric-card">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-purple-100 rounded-md flex items-center justify-center">
              <CubeIcon class="w-5 h-5 text-purple-600" />
            </div>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Total Parts</p>
            <p class="text-2xl font-semibold text-gray-900">
              {{ formatNumber(metrics.total_parts) }}
            </p>
          </div>
        </div>
      </div>

      <!-- Total Leads -->
      <div class="metric-card">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-yellow-100 rounded-md flex items-center justify-center">
              <UsersIcon class="w-5 h-5 text-yellow-600" />
            </div>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Total Leads</p>
            <p class="text-2xl font-semibold text-gray-900">
              {{ formatNumber(metrics.total_leads) }}
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Secondary Metrics -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <!-- Active Parts -->
      <div class="metric-card">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-500">Active Parts</p>
            <p class="text-xl font-semibold text-gray-900">
              {{ formatNumber(metrics.active_parts) }}
            </p>
            <p class="text-xs text-gray-500 mt-1">
              {{ ((metrics.active_parts / metrics.total_parts) * 100).toFixed(1) }}% of total
            </p>
          </div>
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-green-100 rounded-md flex items-center justify-center">
              <CheckCircleIcon class="w-5 h-5 text-green-600" />
            </div>
          </div>
        </div>
      </div>

      <!-- Pending Orders -->
      <div class="metric-card">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-500">Pending Orders</p>
            <p class="text-xl font-semibold text-gray-900">
              {{ formatNumber(metrics.pending_orders) }}
            </p>
            <p class="text-xs text-gray-500 mt-1">
              {{ ((metrics.pending_orders / metrics.total_orders) * 100).toFixed(1) }}% of total
            </p>
          </div>
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-yellow-100 rounded-md flex items-center justify-center">
              <ClockIcon class="w-5 h-5 text-yellow-600" />
            </div>
          </div>
        </div>
      </div>

      <!-- New Leads -->
      <div class="metric-card">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-500">New Leads</p>
            <p class="text-xl font-semibold text-gray-900">
              {{ formatNumber(metrics.new_leads) }}
            </p>
            <p class="text-xs text-gray-500 mt-1">
              {{ ((metrics.new_leads / metrics.total_leads) * 100).toFixed(1) }}% of total
            </p>
          </div>
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-blue-100 rounded-md flex items-center justify-center">
              <UserPlusIcon class="w-5 h-5 text-blue-600" />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Charts Row -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Parts by Category Chart -->
      <div class="chart-container">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-medium text-gray-900">Parts by Category</h3>
          <button 
            @click="$emit('refresh')"
            :disabled="loading"
            class="text-sm text-blue-600 hover:text-blue-800 disabled:opacity-50"
          >
            Refresh
          </button>
        </div>
        <div v-if="loading" class="h-64 flex items-center justify-center">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
        <div v-else class="h-64">
          <PartsByCategoryChart />
        </div>
      </div>

      <!-- Revenue Trend Chart -->
      <div class="chart-container">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-medium text-gray-900">Revenue Trend</h3>
          <button 
            @click="$emit('refresh')"
            :disabled="loading"
            class="text-sm text-blue-600 hover:text-blue-800 disabled:opacity-50"
          >
            Refresh
          </button>
        </div>
        <div v-if="loading" class="h-64 flex items-center justify-center">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
        <div v-else class="h-64">
          <RevenueTrendChart />
        </div>
      </div>
    </div>

    <!-- Quick Stats -->
    <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h3 class="text-lg font-medium text-gray-900 mb-4">Quick Statistics</h3>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="text-center">
          <p class="text-2xl font-semibold text-gray-900">{{ formatNumber(metrics.total_categories) }}</p>
          <p class="text-sm text-gray-500">Categories</p>
        </div>
        <div class="text-center">
          <p class="text-2xl font-semibold text-gray-900">{{ formatNumber(metrics.total_vehicles) }}</p>
          <p class="text-sm text-gray-500">Vehicle Models</p>
        </div>
        <div class="text-center">
          <p class="text-2xl font-semibold text-gray-900">{{ formatNumber(metrics.total_users) }}</p>
          <p class="text-sm text-gray-500">Users</p>
        </div>
        <div class="text-center">
          <p class="text-2xl font-semibold text-gray-900">{{ formatNumber(metrics.active_users) }}</p>
          <p class="text-sm text-gray-500">Active Users</p>
        </div>
      </div>
    </div>

    <!-- Date Range Info -->
    <div v-if="metrics.date_range" class="bg-blue-50 rounded-lg p-4">
      <div class="flex items-center">
        <InformationCircleIcon class="w-5 h-5 text-blue-600 mr-2" />
        <p class="text-sm text-blue-800">
          Data shown for period: 
          <span class="font-medium">{{ formatDate(metrics.date_range.from) }}</span> 
          to 
          <span class="font-medium">{{ formatDate(metrics.date_range.to) }}</span>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { 
  CurrencyDollarIcon, 
  ShoppingBagIcon, 
  CubeIcon, 
  UsersIcon,
  CheckCircleIcon,
  ClockIcon,
  UserPlusIcon,
  InformationCircleIcon
} from '@heroicons/vue/24/outline'
import PartsByCategoryChart from './charts/PartsByCategoryChart.vue'
import RevenueTrendChart from './charts/RevenueTrendChart.vue'

// Props
defineProps({
  metrics: {
    type: Object,
    required: true
  },
  loading: {
    type: Boolean,
    default: false
  }
})

// Emits
defineEmits(['refresh'])

// Utility functions
const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(amount)
}

const formatNumber = (value) => {
  return new Intl.NumberFormat('en-US').format(value)
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}
</script>
