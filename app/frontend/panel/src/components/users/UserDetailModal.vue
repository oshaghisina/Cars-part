<template>
  <div
    v-if="show"
    class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50"
    @click.self="$emit('close')"
  >
    <div class="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white">
      <div class="mt-3">
        <!-- Header -->
        <div class="flex items-center justify-between pb-4 border-b">
          <h3 class="text-lg font-medium text-gray-900">
            User Details
          </h3>
          <button
            @click="$emit('close')"
            class="text-gray-400 hover:text-gray-600"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div v-if="user" class="mt-6 space-y-6">
          <!-- User Avatar and Basic Info -->
          <div class="flex items-start space-x-4">
            <div class="flex-shrink-0">
              <div class="w-16 h-16 bg-gray-300 rounded-full flex items-center justify-center">
                <svg class="w-8 h-8 text-gray-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd" />
                </svg>
              </div>
            </div>
            <div class="flex-1 min-w-0">
              <h4 class="text-lg font-medium text-gray-900">
                {{ user.first_name }} {{ user.last_name }}
              </h4>
              <p class="text-sm text-gray-500">{{ user.email }}</p>
              <div class="flex items-center mt-2 space-x-4">
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                      :class="getRoleBadgeClass(user.role)">
                  {{ user.role }}
                </span>
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                      :class="user.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'">
                  {{ user.is_active ? 'Active' : 'Inactive' }}
                </span>
                <span v-if="user.is_verified" class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                  Verified
                </span>
              </div>
            </div>
          </div>

          <!-- User Information Grid -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- Username -->
            <div>
              <dt class="text-sm font-medium text-gray-500">Username</dt>
              <dd class="mt-1 text-sm text-gray-900">{{ user.username }}</dd>
            </div>

            <!-- Phone -->
            <div>
              <dt class="text-sm font-medium text-gray-500">Phone</dt>
              <dd class="mt-1 text-sm text-gray-900">{{ user.phone || 'Not provided' }}</dd>
            </div>

            <!-- Timezone -->
            <div>
              <dt class="text-sm font-medium text-gray-500">Timezone</dt>
              <dd class="mt-1 text-sm text-gray-900">{{ user.timezone || 'UTC' }}</dd>
            </div>

            <!-- Language -->
            <div>
              <dt class="text-sm font-medium text-gray-500">Language</dt>
              <dd class="mt-1 text-sm text-gray-900">{{ user.language || 'en' }}</dd>
            </div>

            <!-- Created At -->
            <div>
              <dt class="text-sm font-medium text-gray-500">Member Since</dt>
              <dd class="mt-1 text-sm text-gray-900">
                {{ formatDate(user.created_at) }}
              </dd>
            </div>

            <!-- Last Login -->
            <div>
              <dt class="text-sm font-medium text-gray-500">Last Login</dt>
              <dd class="mt-1 text-sm text-gray-900">
                {{ user.last_login ? formatDate(user.last_login) : 'Never' }}
              </dd>
            </div>

            <!-- Login Attempts -->
            <div v-if="user.login_attempts > 0">
              <dt class="text-sm font-medium text-gray-500">Failed Login Attempts</dt>
              <dd class="mt-1 text-sm text-gray-900">{{ user.login_attempts }}</dd>
            </div>

            <!-- Account Locked -->
            <div v-if="user.locked_until">
              <dt class="text-sm font-medium text-gray-500">Account Locked Until</dt>
              <dd class="mt-1 text-sm text-red-600">
                {{ formatDate(user.locked_until) }}
              </dd>
            </div>
          </div>

          <!-- Activity Statistics -->
          <div class="border-t pt-6">
            <h5 class="text-sm font-medium text-gray-900 mb-4">Activity Statistics</h5>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div class="bg-gray-50 rounded-lg p-4">
                <dt class="text-sm font-medium text-gray-500">Total Sessions</dt>
                <dd class="mt-1 text-2xl font-semibold text-gray-900">{{ userStats.totalSessions }}</dd>
              </div>
              <div class="bg-gray-50 rounded-lg p-4">
                <dt class="text-sm font-medium text-gray-500">Active Sessions</dt>
                <dd class="mt-1 text-2xl font-semibold text-gray-900">{{ userStats.activeSessions }}</dd>
              </div>
              <div class="bg-gray-50 rounded-lg p-4">
                <dt class="text-sm font-medium text-gray-500">Total Activities</dt>
                <dd class="mt-1 text-2xl font-semibold text-gray-900">{{ userStats.totalActivities }}</dd>
              </div>
            </div>
          </div>

          <!-- Recent Activity -->
          <div class="border-t pt-6">
            <h5 class="text-sm font-medium text-gray-900 mb-4">Recent Activity</h5>
            <div v-if="recentActivities.length > 0" class="space-y-3">
              <div
                v-for="activity in recentActivities"
                :key="activity.id"
                class="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg"
              >
                <div class="flex-shrink-0">
                  <div class="w-2 h-2 bg-blue-400 rounded-full mt-2"></div>
                </div>
                <div class="flex-1 min-w-0">
                  <p class="text-sm text-gray-900">{{ activity.activity_type }}</p>
                  <p class="text-xs text-gray-500">
                    {{ formatDate(activity.created_at) }}
                    <span v-if="activity.ip_address" class="ml-2">
                      from {{ activity.ip_address }}
                    </span>
                  </p>
                </div>
              </div>
            </div>
            <div v-else class="text-center py-8 text-gray-500">
              <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
              <p class="mt-2">No recent activity</p>
            </div>
          </div>

          <!-- Action Buttons -->
          <div class="flex justify-end space-x-3 pt-6 border-t">
            <button
              @click="$emit('close')"
              class="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Close
            </button>
            <button
              @click="$emit('edit', user)"
              class="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Edit User
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, watch, onMounted } from 'vue'
import { useUsersStore } from '@/stores/users'

export default {
  name: 'UserDetailModal',
  props: {
    show: {
      type: Boolean,
      default: false,
    },
    user: {
      type: Object,
      default: null,
    },
  },
  emits: ['close', 'edit'],
  setup(props) {
    const usersStore = useUsersStore()
    
    const userStats = ref({
      totalSessions: 0,
      activeSessions: 0,
      totalActivities: 0,
    })
    
    const recentActivities = ref([])

    const formatDate = (dateString) => {
      if (!dateString) return 'N/A'
      return new Date(dateString).toLocaleString()
    }

    const getRoleBadgeClass = (role) => {
      const roleClasses = {
        super_admin: 'bg-red-100 text-red-800',
        admin: 'bg-purple-100 text-purple-800',
        manager: 'bg-blue-100 text-blue-800',
        user: 'bg-gray-100 text-gray-800',
      }
      return roleClasses[role] || 'bg-gray-100 text-gray-800'
    }

    const fetchUserStats = async () => {
      if (!props.user) return
      
      try {
        // In a real implementation, you would fetch these from the API
        // For now, we'll use mock data
        userStats.value = {
          totalSessions: Math.floor(Math.random() * 50) + 10,
          activeSessions: Math.floor(Math.random() * 5) + 1,
          totalActivities: Math.floor(Math.random() * 200) + 50,
        }
        
        // Mock recent activities
        recentActivities.value = [
          {
            id: 1,
            activity_type: 'Logged in',
            created_at: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
            ip_address: '192.168.1.1',
          },
          {
            id: 2,
            activity_type: 'Updated profile',
            created_at: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(),
            ip_address: '192.168.1.1',
          },
          {
            id: 3,
            activity_type: 'Changed password',
            created_at: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(),
            ip_address: '192.168.1.1',
          },
        ]
      } catch (error) {
        console.error('Error fetching user stats:', error)
      }
    }

    watch(() => props.show, (newValue) => {
      if (newValue && props.user) {
        fetchUserStats()
      }
    })

    watch(() => props.user, () => {
      if (props.show && props.user) {
        fetchUserStats()
      }
    })

    onMounted(() => {
      if (props.show && props.user) {
        fetchUserStats()
      }
    })

    return {
      userStats,
      recentActivities,
      formatDate,
      getRoleBadgeClass,
    }
  },
}
</script>
