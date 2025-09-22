<template>
  <div class="ai-dashboard">
    <div class="dashboard-header mb-8">
      <h1 class="text-3xl font-bold text-gray-800 mb-2">
        🤖 AI Dashboard
      </h1>
      <p class="text-gray-600 text-lg">
        Advanced AI-powered features for car parts management
      </p>
    </div>

    <!-- AI Status Card -->
    <div class="ai-status-card mb-8 p-6 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-200">
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-xl font-semibold text-blue-800 mb-2">AI Gateway Status</h2>
          <div class="flex items-center gap-4 text-sm">
            <div class="flex items-center gap-2">
              <div class="w-3 h-3 bg-green-500 rounded-full"></div>
              <span class="text-gray-700">AI Gateway: {{ aiStatus.enabled ? 'Enabled' : 'Disabled' }}</span>
            </div>
            <div class="flex items-center gap-2">
              <div class="w-3 h-3 bg-blue-500 rounded-full"></div>
              <span class="text-gray-700">Providers: {{ aiStatus.providers ? Object.keys(aiStatus.providers).length : 0 }}</span>
            </div>
            <div class="flex items-center gap-2">
              <div class="w-3 h-3 bg-purple-500 rounded-full"></div>
              <span class="text-gray-700">Epic E3: Active</span>
            </div>
          </div>
        </div>
        <button
          @click="refreshAIStatus"
          :disabled="isLoadingStatus"
          class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {{ isLoadingStatus ? 'Refreshing...' : 'Refresh Status' }}
        </button>
      </div>
    </div>

    <!-- Feature Tabs -->
    <div class="feature-tabs mb-8">
      <div class="border-b border-gray-200">
        <nav class="-mb-px flex space-x-8">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            @click="activeTab = tab.id"
            :class="[
              'py-2 px-1 border-b-2 font-medium text-sm transition-colors',
              activeTab === tab.id
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            <span class="mr-2">{{ tab.icon }}</span>
            {{ tab.name }}
          </button>
        </nav>
      </div>
    </div>

    <!-- Tab Content -->
    <div class="tab-content">
      <!-- AI Search Interface -->
      <div v-if="activeTab === 'search'" class="tab-panel">
        <AISearchInterface />
      </div>

      <!-- AI Recommendations -->
      <div v-if="activeTab === 'recommendations'" class="tab-panel">
        <AIRecommendations />
      </div>

      <!-- Language Analysis -->
      <div v-if="activeTab === 'language'" class="tab-panel">
        <AILanguageAnalysis />
      </div>

      <!-- AI Analytics -->
      <div v-if="activeTab === 'analytics'" class="tab-panel">
        <AIAnalytics />
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="quick-actions mt-8 p-6 bg-gray-50 rounded-lg">
      <h3 class="text-lg font-semibold text-gray-800 mb-4">Quick Actions</h3>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <button
          @click="activeTab = 'search'"
          class="p-4 bg-white border border-gray-200 rounded-lg hover:shadow-md transition-shadow text-left"
        >
          <div class="text-2xl mb-2">🔍</div>
          <div class="font-medium text-gray-800">AI Search</div>
          <div class="text-sm text-gray-600">Search parts with natural language</div>
        </button>
        
        <button
          @click="activeTab = 'recommendations'"
          class="p-4 bg-white border border-gray-200 rounded-lg hover:shadow-md transition-shadow text-left"
        >
          <div class="text-2xl mb-2">🎯</div>
          <div class="font-medium text-gray-800">Smart Recommendations</div>
          <div class="text-sm text-gray-600">Get AI-powered part suggestions</div>
        </button>
        
        <button
          @click="activeTab = 'language'"
          class="p-4 bg-white border border-gray-200 rounded-lg hover:shadow-md transition-shadow text-left"
        >
          <div class="text-2xl mb-2">🌐</div>
          <div class="font-medium text-gray-800">Language Analysis</div>
          <div class="text-sm text-gray-600">Analyze text and extract entities</div>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import AISearchInterface from '@/components/AISearchInterface.vue'
import AIRecommendations from '@/components/AIRecommendations.vue'
import AILanguageAnalysis from '@/components/AILanguageAnalysis.vue'
import AIAnalytics from '@/components/AIAnalytics.vue'

const authStore = useAuthStore()

// Reactive data
const activeTab = ref('search')
const aiStatus = ref({})
const isLoadingStatus = ref(false)

const tabs = [
  { id: 'search', name: 'AI Search', icon: '🔍' },
  { id: 'recommendations', name: 'Recommendations', icon: '🎯' },
  { id: 'language', name: 'Language Analysis', icon: '🌐' },
  { id: 'analytics', name: 'AI Analytics', icon: '📊' }
]

// Methods
const refreshAIStatus = async () => {
  isLoadingStatus.value = true
  
  try {
    const response = await fetch('/api/v1/ai/ai-status', {
      headers: {
        'Authorization': `Bearer ${authStore.token}`
      }
    })
    
    if (response.ok) {
      const data = await response.json()
      aiStatus.value = data
    }
  } catch (err) {
    console.error('Error fetching AI status:', err)
  } finally {
    isLoadingStatus.value = false
  }
}

onMounted(() => {
  refreshAIStatus()
})
</script>

<style scoped>
.ai-dashboard {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.tab-panel {
  animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.quick-actions button {
  transition: all 0.2s ease;
}

.quick-actions button:hover {
  transform: translateY(-2px);
}
</style>
