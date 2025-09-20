<template>
  <div class="bg-white shadow rounded-lg">
    <div class="px-6 py-4 border-b border-gray-200">
      <div class="flex justify-between items-center">
        <h3 class="text-lg font-medium text-gray-900">System Health</h3>
        <div class="flex items-center space-x-2">
          <div :class="[
            'w-3 h-3 rounded-full',
            overallStatus === 'healthy' ? 'bg-green-400' : 
            overallStatus === 'warning' ? 'bg-yellow-400' : 'bg-red-400'
          ]"></div>
          <span class="text-sm font-medium capitalize">{{ overallStatus }}</span>
        </div>
      </div>
    </div>
    
    <div class="p-6 space-y-4">
      <!-- API Status -->
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-3">
          <div class="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
            <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.367 2.684 3 3 0 00-5.367-2.684z" />
            </svg>
          </div>
          <div>
            <p class="text-sm font-medium text-gray-900">API Server</p>
            <p class="text-xs text-gray-500">REST API endpoints</p>
          </div>
        </div>
        <div class="flex items-center space-x-2">
          <div :class="[
            'w-2 h-2 rounded-full',
            health.apiStatus === 'healthy' ? 'bg-green-400' : 
            health.apiStatus === 'warning' ? 'bg-yellow-400' : 'bg-red-400'
          ]"></div>
          <span class="text-sm font-medium capitalize">{{ health.apiStatus }}</span>
        </div>
      </div>
      
      <!-- Database Status -->
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-3">
          <div class="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
            <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4" />
            </svg>
          </div>
          <div>
            <p class="text-sm font-medium text-gray-900">Database</p>
            <p class="text-xs text-gray-500">SQLite database</p>
          </div>
        </div>
        <div class="flex items-center space-x-2">
          <div :class="[
            'w-2 h-2 rounded-full',
            health.databaseStatus === 'healthy' ? 'bg-green-400' : 
            health.databaseStatus === 'warning' ? 'bg-yellow-400' : 'bg-red-400'
          ]"></div>
          <span class="text-sm font-medium capitalize">{{ health.databaseStatus }}</span>
        </div>
      </div>
      
      <!-- Bot Status -->
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-3">
          <div class="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center">
            <svg class="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
          </div>
          <div>
            <p class="text-sm font-medium text-gray-900">Telegram Bot</p>
            <p class="text-xs text-gray-500">@ChinaCarPartBot</p>
          </div>
        </div>
        <div class="flex items-center space-x-2">
          <div :class="[
            'w-2 h-2 rounded-full',
            health.botStatus === 'healthy' ? 'bg-green-400' : 
            health.botStatus === 'warning' ? 'bg-yellow-400' : 'bg-red-400'
          ]"></div>
          <span class="text-sm font-medium capitalize">{{ health.botStatus }}</span>
        </div>
      </div>
      
      <!-- Last Update -->
      <div v-if="health.lastUpdate" class="pt-4 border-t border-gray-200">
        <div class="flex items-center justify-between text-xs text-gray-500">
          <span>Last updated</span>
          <span>{{ formatLastUpdate(health.lastUpdate) }}</span>
        </div>
      </div>
      
      <!-- Refresh Button -->
      <div class="pt-4 border-t border-gray-200">
        <button
          @click="$emit('refresh')"
          :disabled="loading"
          class="w-full inline-flex justify-center items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
        >
          <svg class="w-4 h-4 mr-2" :class="{ 'animate-spin': loading }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Refresh Status
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SystemHealth',
  props: {
    health: {
      type: Object,
      required: true
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  emits: ['refresh'],
  computed: {
    overallStatus() {
      const statuses = [
        this.health.apiStatus,
        this.health.databaseStatus,
        this.health.botStatus
      ]
      
      if (statuses.includes('error')) return 'error'
      if (statuses.includes('warning')) return 'warning'
      return 'healthy'
    }
  },
  methods: {
    formatLastUpdate(timestamp) {
      const date = new Date(timestamp)
      const now = new Date()
      const diffInMinutes = (now - date) / (1000 * 60)
      
      if (diffInMinutes < 1) {
        return 'Just now'
      } else if (diffInMinutes < 60) {
        return `${Math.floor(diffInMinutes)}m ago`
      } else {
        const diffInHours = Math.floor(diffInMinutes / 60)
        return `${diffInHours}h ago`
      }
    }
  }
}
</script>
