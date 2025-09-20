<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="bg-white shadow rounded-lg p-6">
      <div class="flex justify-between items-center">
        <div>
          <h1 class="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p class="text-gray-600 mt-2">Welcome to your China Car Parts admin panel</p>
        </div>
        <div class="flex space-x-3">
          <button
            @click="refreshDashboard"
            :disabled="dashboardStore.loading"
            class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
          >
            <svg class="w-4 h-4 mr-2" :class="{ 'animate-spin': dashboardStore.loading }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            {{ dashboardStore.loading ? 'Refreshing...' : 'Refresh' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Error Message -->
    <div v-if="dashboardStore.error" class="rounded-md bg-red-50 p-4">
      <div class="flex">
        <div class="flex-shrink-0">
          <svg class="h-5 w-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
          </svg>
        </div>
        <div class="ml-3">
          <h3 class="text-sm font-medium text-red-800">Error loading dashboard</h3>
          <div class="mt-2 text-sm text-red-700">
            {{ dashboardStore.error }}
          </div>
        </div>
      </div>
    </div>

    <!-- Key Metrics -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <MetricCard
        icon="🔧"
        label="Total Parts"
        :value="dashboardStore.metrics.totalParts"
        color="blue"
        description="Auto parts in inventory"
      />
      
      <MetricCard
        icon="🚗"
        label="Total Vehicles"
        :value="dashboardStore.metrics.totalVehicles"
        color="green"
        description="Brands, models & trims"
      />
      
      <MetricCard
        icon="📁"
        label="Categories"
        :value="dashboardStore.metrics.totalCategories"
        color="purple"
        description="Part categories"
      />
      
      <MetricCard
        icon="📦"
        label="Total Orders"
        :value="dashboardStore.metrics.totalOrders"
        color="orange"
        description="Customer orders"
      />
    </div>

    <!-- Secondary Metrics -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <MetricCard
        icon="✅"
        label="Active Parts"
        :value="dashboardStore.metrics.activeParts"
        color="green"
        description="Currently available"
      />
      
      <MetricCard
        icon="⏳"
        label="Pending Orders"
        :value="dashboardStore.metrics.pendingOrders"
        color="yellow"
        description="Awaiting processing"
      />
      
      <MetricCard
        icon="👥"
        label="Total Leads"
        :value="dashboardStore.metrics.totalLeads"
        color="indigo"
        description="Potential customers"
      />
      
      <MetricCard
        icon="🆕"
        label="New Leads"
        :value="dashboardStore.metrics.newLeads"
        color="pink"
        description="Recent inquiries"
      />
    </div>

    <!-- Charts Section -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Parts by Category -->
      <ChartCard
        title="Parts by Category"
        :data="dashboardStore.charts.partsByCategory"
        :loading="dashboardStore.loading"
        @refresh="refreshCharts"
      >
        <template #default="{ data }">
          <div class="space-y-3">
            <div v-for="item in data.slice(0, 5)" :key="item.name" class="flex items-center justify-between">
              <div class="flex items-center space-x-3">
                <div class="w-3 h-3 bg-blue-500 rounded-full"></div>
                <span class="text-sm font-medium text-gray-900">{{ item.name }}</span>
              </div>
              <span class="text-sm font-medium text-gray-900">{{ item.value }}</span>
            </div>
            <div v-if="data.length === 0" class="text-center text-gray-500 text-sm">
              No category data available
            </div>
          </div>
        </template>
      </ChartCard>

      <!-- Parts by Brand -->
      <ChartCard
        title="Parts by Brand"
        :data="dashboardStore.charts.partsByBrand"
        :loading="dashboardStore.loading"
        @refresh="refreshCharts"
      >
        <template #default="{ data }">
          <div class="space-y-3">
            <div v-for="item in data.slice(0, 5)" :key="item.name" class="flex items-center justify-between">
              <div class="flex items-center space-x-3">
                <div class="w-3 h-3 bg-green-500 rounded-full"></div>
                <span class="text-sm font-medium text-gray-900">{{ item.name }}</span>
              </div>
              <span class="text-sm font-medium text-gray-900">{{ item.value }}</span>
            </div>
            <div v-if="data.length === 0" class="text-center text-gray-500 text-sm">
              No brand data available
            </div>
          </div>
        </template>
      </ChartCard>
    </div>

    <!-- Recent Activity and System Health -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Recent Orders -->
      <ActivityList
        title="Recent Orders"
        :items="dashboardStore.recentActivity.recentOrders"
        :loading="dashboardStore.loading"
        type="orders"
        @viewAll="navigateToOrders"
      />

      <!-- Recent Parts -->
      <ActivityList
        title="Recent Parts"
        :items="dashboardStore.recentActivity.recentParts"
        :loading="dashboardStore.loading"
        type="parts"
        @viewAll="navigateToParts"
      />

      <!-- System Health -->
      <SystemHealth
        :health="dashboardStore.systemHealth"
        :loading="dashboardStore.loading"
        @refresh="refreshHealth"
      />
    </div>

    <!-- Quick Actions -->
    <div class="bg-white shadow rounded-lg p-6">
      <h3 class="text-lg font-medium text-gray-900 mb-4">Quick Actions</h3>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <button
          @click="navigateToParts"
          class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
          Add Part
        </button>
        
        <button
          @click="navigateToVehicles"
          class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
        >
          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
          Add Vehicle
        </button>
        
        <button
          @click="navigateToCategories"
          class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-purple-600 hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500"
        >
          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
          Add Category
        </button>
        
        <button
          @click="navigateToOrders"
          class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-orange-600 hover:bg-orange-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-orange-500"
        >
          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
          View Orders
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useDashboardStore } from '../stores/dashboard'
import MetricCard from '../components/dashboard/MetricCard.vue'
import ChartCard from '../components/dashboard/ChartCard.vue'
import ActivityList from '../components/dashboard/ActivityList.vue'
import SystemHealth from '../components/dashboard/SystemHealth.vue'

export default {
  name: 'Dashboard',
  components: {
    MetricCard,
    ChartCard,
    ActivityList,
    SystemHealth
  },
  setup() {
    const router = useRouter()
    const dashboardStore = useDashboardStore()
    
    const refreshDashboard = async () => {
      await dashboardStore.fetchDashboardData()
    }
    
    const refreshCharts = async () => {
      await dashboardStore.fetchChartsData()
    }
    
    const refreshHealth = async () => {
      await dashboardStore.checkSystemHealth()
    }
    
    const navigateToParts = () => {
      router.push('/parts')
    }
    
    const navigateToVehicles = () => {
      router.push('/vehicles')
    }
    
    const navigateToCategories = () => {
      router.push('/categories')
    }
    
    const navigateToOrders = () => {
      router.push('/orders')
    }
    
    onMounted(async () => {
      await refreshDashboard()
    })
    
    return {
      dashboardStore,
      refreshDashboard,
      refreshCharts,
      refreshHealth,
      navigateToParts,
      navigateToVehicles,
      navigateToCategories,
      navigateToOrders
    }
  }
}
</script>