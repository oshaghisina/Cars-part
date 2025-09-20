<template>
  <div class="bg-white shadow rounded-lg">
    <div class="px-6 py-4 border-b border-gray-200">
      <div class="flex justify-between items-center">
        <h3 class="text-lg font-medium text-gray-900">{{ title }}</h3>
        <button
          @click="$emit('viewAll')"
          class="text-sm text-blue-600 hover:text-blue-900"
        >
          View all
        </button>
      </div>
    </div>
    
    <div class="divide-y divide-gray-200">
      <!-- Loading State -->
      <div v-if="loading" class="px-6 py-4">
        <div class="animate-pulse space-y-3">
          <div v-for="i in 3" :key="i" class="flex items-center space-x-3">
            <div class="rounded-full bg-gray-200 h-8 w-8"></div>
            <div class="flex-1 space-y-1">
              <div class="h-4 bg-gray-200 rounded w-3/4"></div>
              <div class="h-3 bg-gray-200 rounded w-1/2"></div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Empty State -->
      <div v-else-if="!hasItems" class="px-6 py-8 text-center">
        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
        </svg>
        <h3 class="mt-2 text-sm font-medium text-gray-900">No recent activity</h3>
        <p class="mt-1 text-sm text-gray-500">{{ emptyMessage }}</p>
      </div>
      
      <!-- Activity Items -->
      <div v-else>
        <div
          v-for="(item, index) in items"
          :key="index"
          class="px-6 py-4 hover:bg-gray-50"
        >
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div :class="[
                'w-8 h-8 rounded-full flex items-center justify-center',
                getItemIconBg(item)
              ]">
                <span class="text-white text-xs font-medium">{{ getItemIcon(item) }}</span>
              </div>
            </div>
            <div class="ml-4 flex-1 min-w-0">
              <div class="flex items-center justify-between">
                <p class="text-sm font-medium text-gray-900 truncate">
                  {{ getItemTitle(item) }}
                </p>
                <div class="ml-2 flex-shrink-0 flex">
                  <p class="text-xs text-gray-500">{{ formatTime(item) }}</p>
                </div>
              </div>
              <p class="text-sm text-gray-500 truncate">
                {{ getItemDescription(item) }}
              </p>
              <div v-if="getItemStatus(item)" class="mt-1">
                <span :class="[
                  'inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium',
                  getStatusClass(getItemStatus(item))
                ]">
                  {{ getItemStatus(item) }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ActivityList',
  props: {
    title: {
      type: String,
      required: true
    },
    items: {
      type: Array,
      default: () => []
    },
    loading: {
      type: Boolean,
      default: false
    },
    type: {
      type: String,
      default: 'general' // 'orders', 'leads', 'parts', 'categories'
    },
    emptyMessage: {
      type: String,
      default: 'No recent activity to show'
    }
  },
  emits: ['viewAll'],
  computed: {
    hasItems() {
      return this.items && this.items.length > 0
    }
  },
  methods: {
    getItemIcon(item) {
      switch (this.type) {
        case 'orders':
          return '📦'
        case 'leads':
          return '👥'
        case 'parts':
          return '🔧'
        case 'categories':
          return '📁'
        default:
          return '📋'
      }
    },
    
    getItemIconBg(item) {
      switch (this.type) {
        case 'orders':
          return 'bg-blue-500'
        case 'leads':
          return 'bg-green-500'
        case 'parts':
          return 'bg-purple-500'
        case 'categories':
          return 'bg-orange-500'
        default:
          return 'bg-gray-500'
      }
    },
    
    getItemTitle(item) {
      switch (this.type) {
        case 'orders':
          return `Order #${item.id}`
        case 'leads':
          return item.name || item.email || 'New Lead'
        case 'parts':
          return item.part_name || 'New Part'
        case 'categories':
          return item.name || 'New Category'
        default:
          return item.title || item.name || 'New Item'
      }
    },
    
    getItemDescription(item) {
      switch (this.type) {
        case 'orders':
          return `Customer: ${item.customer_name || 'Unknown'} - $${item.total || 0}`
        case 'leads':
          return item.message || item.source || 'New lead received'
        case 'parts':
          return `${item.brand_oem || 'Unknown Brand'} - ${item.category || 'Uncategorized'}`
        case 'categories':
          return item.description || 'New category added'
        default:
          return item.description || 'New activity'
      }
    },
    
    getItemStatus(item) {
      switch (this.type) {
        case 'orders':
          return item.status
        case 'leads':
          return item.status
        case 'parts':
          return item.status === 'active' ? 'Active' : 'Inactive'
        case 'categories':
          return null
        default:
          return null
      }
    },
    
    getStatusClass(status) {
      if (!status) return ''
      
      const statusMap = {
        'pending': 'bg-yellow-100 text-yellow-800',
        'active': 'bg-green-100 text-green-800',
        'inactive': 'bg-red-100 text-red-800',
        'completed': 'bg-blue-100 text-blue-800',
        'cancelled': 'bg-gray-100 text-gray-800',
        'new': 'bg-green-100 text-green-800',
        'contacted': 'bg-blue-100 text-blue-800',
        'qualified': 'bg-purple-100 text-purple-800',
        'closed': 'bg-gray-100 text-gray-800'
      }
      
      return statusMap[status.toLowerCase()] || 'bg-gray-100 text-gray-800'
    },
    
    formatTime(item) {
      const date = new Date(item.created_at || item.updated_at || Date.now())
      const now = new Date()
      const diffInHours = (now - date) / (1000 * 60 * 60)
      
      if (diffInHours < 1) {
        return 'Just now'
      } else if (diffInHours < 24) {
        return `${Math.floor(diffInHours)}h ago`
      } else {
        const diffInDays = Math.floor(diffInHours / 24)
        return `${diffInDays}d ago`
      }
    }
  }
}
</script>
