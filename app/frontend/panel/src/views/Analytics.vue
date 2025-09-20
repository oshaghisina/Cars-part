<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <div class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="py-6">
          <div class="flex items-center justify-between">
            <div>
              <h1 class="text-2xl font-bold text-gray-900">Analytics Dashboard</h1>
              <p class="mt-1 text-sm text-gray-500">
                Comprehensive insights into your business performance
              </p>
            </div>
            
            <!-- Period Selector -->
            <div class="flex items-center space-x-4">
              <select 
                v-model="selectedPeriod" 
                @change="onPeriodChange"
                class="rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              >
                <option value="7d">Last 7 days</option>
                <option value="30d">Last 30 days</option>
                <option value="90d">Last 90 days</option>
                <option value="1y">Last year</option>
              </select>
              
              <button 
                @click="refreshAllData"
                :disabled="isAnyLoading"
                class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
                aria-label="Refresh analytics data"
              >
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                Refresh
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Error Alert -->
    <div v-if="hasError" class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
      <div class="rounded-md bg-red-50 p-4">
        <div class="flex">
          <div class="flex-shrink-0">
            <svg class="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
            </svg>
          </div>
          <div class="ml-3">
            <h3 class="text-sm font-medium text-red-800">
              Error loading analytics
            </h3>
            <div class="mt-2 text-sm text-red-700">
              {{ getError }}
            </div>
            <div class="mt-4">
              <button 
                @click="clearError"
                class="bg-red-50 px-2 py-1.5 rounded-md text-sm font-medium text-red-800 hover:bg-red-100"
              >
                Dismiss
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Tab Navigation -->
      <div class="border-b border-gray-200 mb-8">
        <nav class="-mb-px flex space-x-8">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            @click="activeTab = tab.id"
            :class="[
              activeTab === tab.id
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
              'whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm'
            ]"
          >
            <component :is="tab.icon" class="w-4 h-4 mr-2 inline" />
            {{ tab.name }}
          </button>
        </nav>
      </div>

      <!-- Tab Content -->
      <div class="space-y-8">
        <!-- Dashboard Overview -->
        <div v-if="activeTab === 'dashboard'">
          <DashboardOverview 
            :metrics="getDashboardMetrics"
            :loading="isDashboardLoading"
            @refresh="fetchDashboardMetrics"
          />
        </div>

        <!-- Sales Analytics -->
        <div v-if="activeTab === 'sales'">
          <SalesAnalytics 
            :analytics="getSalesAnalytics"
            :loading="isSalesLoading"
            :period="selectedPeriod"
            @refresh="fetchSalesAnalytics"
            @period-change="onPeriodChange"
          />
        </div>

        <!-- Inventory Analytics -->
        <div v-if="activeTab === 'inventory'">
          <InventoryAnalytics 
            :analytics="getInventoryAnalytics"
            :loading="isInventoryLoading"
            @refresh="fetchInventoryAnalytics"
          />
        </div>

        <!-- Future Analytics Sections -->
        <!-- Customer Analytics, Performance Metrics, and Reports will be added here -->
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useAnalyticsStore } from '@/stores/analytics'
import DashboardOverview from '@/components/analytics/DashboardOverview.vue'
import SalesAnalytics from '@/components/analytics/SalesAnalytics.vue'
import InventoryAnalytics from '@/components/analytics/InventoryAnalytics.vue'
// Missing components - will be implemented later
// import CustomerAnalytics from '@/components/analytics/CustomerAnalytics.vue'
// import PerformanceMetrics from '@/components/analytics/PerformanceMetrics.vue'
// import ReportsSection from '@/components/analytics/ReportsSection.vue'

// Icons
import {
  ChartBarIcon,
  CurrencyDollarIcon,
  CubeIcon,
  UsersIcon,
  CpuChipIcon,
  DocumentTextIcon
} from '@heroicons/vue/24/outline'

// Store
const analyticsStore = useAnalyticsStore()

// Reactive data
const activeTab = ref('dashboard')
const selectedPeriod = ref('30d')

// Computed
const {
  getDashboardMetrics,
  getSalesAnalytics,
  getInventoryAnalytics,
  // getCustomerAnalytics,
  // getPerformanceMetrics,
  // getReports,
  // getCurrentReport,
  isDashboardLoading,
  isSalesLoading,
  isInventoryLoading,
  // isCustomerLoading,
  // isPerformanceLoading,
  // isReportsLoading,
  hasError,
  getError,
  clearError,
  fetchDashboardMetrics,
  fetchSalesAnalytics,
  fetchInventoryAnalytics
} = analyticsStore

const isAnyLoading = computed(() => {
  return isDashboardLoading || isSalesLoading || isInventoryLoading || 
         false // isCustomerLoading || isPerformanceLoading || isReportsLoading
})

// Tabs configuration - only include working tabs for now
const tabs = [
  { id: 'dashboard', name: 'Overview', icon: ChartBarIcon },
  { id: 'sales', name: 'Sales', icon: CurrencyDollarIcon },
  { id: 'inventory', name: 'Inventory', icon: CubeIcon }
  // Future tabs - will be enabled when components are implemented
  // { id: 'customers', name: 'Customers', icon: UsersIcon },
  // { id: 'performance', name: 'Performance', icon: CpuChipIcon },
  // { id: 'reports', name: 'Reports', icon: DocumentTextIcon }
]

// Methods
const onPeriodChange = async (period = selectedPeriod.value) => {
  selectedPeriod.value = period
  analyticsStore.setFilter('period', period)
  
  // Refresh period-dependent data
  await Promise.all([
    analyticsStore.fetchSalesAnalytics(period),
    // analyticsStore.fetchCustomerAnalytics(period),
    analyticsStore.fetchSalesTrendChart(period)
  ])
}

const refreshAllData = async () => {
  await analyticsStore.fetchAllAnalytics(selectedPeriod.value)
}

// const generateReport = async (reportRequest) => {
//   try {
//     await analyticsStore.generateReport(reportRequest)
//   } catch (error) {
//     console.error('Failed to generate report:', error)
//   }
// }

// const exportData = async (exportRequest) => {
//   try {
//     await analyticsStore.exportData(exportRequest)
//   } catch (error) {
//     console.error('Failed to export data:', error)
//   }
// }

// Lifecycle
onMounted(async () => {
  await refreshAllData()
})
</script>

<style scoped>
/* Custom styles for analytics dashboard */
.analytics-card {
  background-color: white;
  border-radius: 0.5rem;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  border: 1px solid #e5e7eb;
  padding: 1.5rem;
}

.metric-card {
  background-color: white;
  border-radius: 0.5rem;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  border: 1px solid #e5e7eb;
  padding: 1.5rem;
  transition: box-shadow 0.15s ease-in-out;
}

.metric-card:hover {
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.chart-container {
  background-color: white;
  border-radius: 0.5rem;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  border: 1px solid #e5e7eb;
  padding: 1.5rem;
}

.loading-skeleton {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
  background-color: #e5e7eb;
  border-radius: 0.25rem;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: .5;
  }
}
</style>
