<template>
  <div class="ai-analytics">
    <div class="analytics-header mb-6">
      <h2 class="text-2xl font-bold text-gray-800 mb-2">
        📊 AI Analytics
      </h2>
      <p class="text-gray-600">
        Monitor AI performance, usage statistics, and system health
      </p>
    </div>

    <!-- Metrics Grid -->
    <div class="metrics-grid grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <div class="metric-card bg-white p-6 rounded-lg border border-gray-200">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Total AI Requests</p>
            <p class="text-2xl font-bold text-gray-900">{{ metrics.totalRequests || 0 }}</p>
          </div>
          <div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
            <span class="text-2xl">🤖</span>
          </div>
        </div>
      </div>

      <div class="metric-card bg-white p-6 rounded-lg border border-gray-200">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Success Rate</p>
            <p class="text-2xl font-bold text-green-600">{{ Math.round(metrics.successRate || 0) }}%</p>
          </div>
          <div class="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
            <span class="text-2xl">✅</span>
          </div>
        </div>
      </div>

      <div class="metric-card bg-white p-6 rounded-lg border border-gray-200">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Average Response Time</p>
            <p class="text-2xl font-bold text-blue-600">{{ Math.round(metrics.avgResponseTime || 0) }}ms</p>
          </div>
          <div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
            <span class="text-2xl">⚡</span>
          </div>
        </div>
      </div>

      <div class="metric-card bg-white p-6 rounded-lg border border-gray-200">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Active Providers</p>
            <p class="text-2xl font-bold text-purple-600">{{ metrics.activeProviders || 0 }}</p>
          </div>
          <div class="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
            <span class="text-2xl">🔗</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Provider Status -->
    <div class="provider-status mb-8">
      <h3 class="text-lg font-semibold text-gray-800 mb-4">AI Provider Status</h3>
      <div class="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Provider</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Health</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Capabilities</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Circuit Breaker</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="(provider, name) in providerStatus" :key="name">
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  {{ name }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span :class="[
                    'inline-flex px-2 py-1 text-xs font-semibold rounded-full',
                    provider.available ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                  ]">
                    {{ provider.available ? 'Available' : 'Unavailable' }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span :class="[
                    'inline-flex px-2 py-1 text-xs font-semibold rounded-full',
                    provider.healthy ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                  ]">
                    {{ provider.status }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ provider.capabilities?.length || 0 }} capabilities
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span :class="[
                    'inline-flex px-2 py-1 text-xs font-semibold rounded-full',
                    provider.circuit_breaker?.state === 'closed' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                  ]">
                    {{ provider.circuit_breaker?.state || 'unknown' }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Feature Usage -->
    <div class="feature-usage mb-8">
      <h3 class="text-lg font-semibold text-gray-800 mb-4">Feature Usage</h3>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div class="bg-white p-6 rounded-lg border border-gray-200">
          <div class="flex items-center justify-between mb-4">
            <h4 class="font-medium text-gray-800">Hybrid Search</h4>
            <span class="text-2xl">🔍</span>
          </div>
          <div class="text-3xl font-bold text-blue-600 mb-2">{{ featureUsage.hybridSearch || 0 }}</div>
          <div class="text-sm text-gray-600">Total searches</div>
        </div>

        <div class="bg-white p-6 rounded-lg border border-gray-200">
          <div class="flex items-center justify-between mb-4">
            <h4 class="font-medium text-gray-800">Recommendations</h4>
            <span class="text-2xl">🎯</span>
          </div>
          <div class="text-3xl font-bold text-green-600 mb-2">{{ featureUsage.recommendations || 0 }}</div>
          <div class="text-sm text-gray-600">Recommendations generated</div>
        </div>

        <div class="bg-white p-6 rounded-lg border border-gray-200">
          <div class="flex items-center justify-between mb-4">
            <h4 class="font-medium text-gray-800">Language Analysis</h4>
            <span class="text-2xl">🌐</span>
          </div>
          <div class="text-3xl font-bold text-purple-600 mb-2">{{ featureUsage.languageAnalysis || 0 }}</div>
          <div class="text-sm text-gray-600">Text analyses</div>
        </div>
      </div>
    </div>

    <!-- System Health -->
    <div class="system-health">
      <h3 class="text-lg font-semibold text-gray-800 mb-4">System Health</h3>
      <div class="bg-white rounded-lg border border-gray-200 p-6">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 class="font-medium text-gray-800 mb-2">AI Gateway</h4>
            <div class="space-y-2">
              <div class="flex justify-between">
                <span class="text-sm text-gray-600">Status:</span>
                <span :class="aiStatus.enabled ? 'text-green-600' : 'text-red-600'" class="text-sm font-medium">
                  {{ aiStatus.enabled ? 'Enabled' : 'Disabled' }}
                </span>
              </div>
              <div class="flex justify-between">
                <span class="text-sm text-gray-600">Experimental Mode:</span>
                <span :class="aiStatus.experimental ? 'text-yellow-600' : 'text-gray-600'" class="text-sm font-medium">
                  {{ aiStatus.experimental ? 'Enabled' : 'Disabled' }}
                </span>
              </div>
            </div>
          </div>
          
          <div>
            <h4 class="font-medium text-gray-800 mb-2">Epic E3 Components</h4>
            <div class="space-y-2">
              <div class="flex justify-between">
                <span class="text-sm text-gray-600">Language Processor:</span>
                <span class="text-green-600 text-sm font-medium">Active</span>
              </div>
              <div class="flex justify-between">
                <span class="text-sm text-gray-600">Hybrid Search:</span>
                <span class="text-green-600 text-sm font-medium">Active</span>
              </div>
              <div class="flex justify-between">
                <span class="text-sm text-gray-600">Recommendations:</span>
                <span class="text-green-600 text-sm font-medium">Active</span>
              </div>
              <div class="flex justify-between">
                <span class="text-sm text-gray-600">Query Processor:</span>
                <span class="text-green-600 text-sm font-medium">Active</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="loading text-center py-8">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      <div class="mt-2 text-gray-600">Loading AI analytics...</div>
    </div>

    <!-- Error State -->
    <div v-if="error" class="error bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
      <div class="text-red-800 font-medium">Analytics Error</div>
      <div class="text-red-600 text-sm mt-1">{{ error }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

// Reactive data
const metrics = ref({})
const providerStatus = ref({})
const featureUsage = ref({})
const aiStatus = ref({})
const isLoading = ref(false)
const error = ref('')

// Methods
const loadAnalytics = async () => {
  isLoading.value = true
  error.value = ''
  
  try {
    // Load AI status
    const statusResponse = await fetch('/api/v1/ai/ai-status', {
      headers: {
        'Authorization': `Bearer ${authStore.token}`
      }
    })
    
    if (statusResponse.ok) {
      const statusData = await statusResponse.json()
      aiStatus.value = statusData
      providerStatus.value = statusData.providers || {}
      
      // Calculate metrics from status data
      metrics.value = {
        totalRequests: statusData.metrics?.total_requests || 0,
        successRate: 95, // Mock data - would be calculated from actual metrics
        avgResponseTime: 250, // Mock data - would be calculated from actual metrics
        activeProviders: Object.keys(providerStatus.value).length
      }
    }
    
    // Mock feature usage data (in production, this would come from analytics API)
    featureUsage.value = {
      hybridSearch: 1250,
      recommendations: 340,
      languageAnalysis: 890
    }
    
  } catch (err) {
    console.error('Error loading analytics:', err)
    error.value = 'Failed to load analytics data'
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  loadAnalytics()
})
</script>

<style scoped>
.ai-analytics {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.metric-card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.metric-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.loading {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
</style>
