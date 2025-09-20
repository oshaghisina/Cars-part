<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <div class="bg-white shadow">
      <div class="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center">
          <div>
            <h1 class="text-3xl font-bold text-gray-900">User Management</h1>
            <p class="mt-2 text-sm text-gray-600">Manage system users and their permissions</p>
          </div>
          <div class="flex space-x-3">
            <button
              @click="refreshData"
              class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              Refresh
            </button>
            <button
              @click="showCreateUser = true"
              class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
              </svg>
              Add User
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Statistics Cards -->
    <div class="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div class="bg-white overflow-hidden shadow rounded-lg">
          <div class="p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <svg class="h-6 w-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
                </svg>
              </div>
              <div class="ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-sm font-medium text-gray-500 truncate">Total Users</dt>
                  <dd class="text-lg font-medium text-gray-900">{{ usersStore.statistics.totalUsers }}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div class="bg-white overflow-hidden shadow rounded-lg">
          <div class="p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <svg class="h-6 w-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div class="ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-sm font-medium text-gray-500 truncate">Active Users</dt>
                  <dd class="text-lg font-medium text-gray-900">{{ usersStore.statistics.activeUsers }}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div class="bg-white overflow-hidden shadow rounded-lg">
          <div class="p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <svg class="h-6 w-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
              </div>
              <div class="ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-sm font-medium text-gray-500 truncate">Verified Users</dt>
                  <dd class="text-lg font-medium text-gray-900">{{ usersStore.statistics.verifiedUsers }}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div class="bg-white overflow-hidden shadow rounded-lg">
          <div class="p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <svg class="h-6 w-6 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div class="ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-sm font-medium text-gray-500 truncate">Recent Logins</dt>
                  <dd class="text-lg font-medium text-gray-900">{{ usersStore.statistics.recentLogins }}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Filters and Search -->
      <div class="bg-white shadow rounded-lg p-6 mb-6">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Search</label>
            <input
              v-model="usersStore.filters.search"
              @input="debouncedSearch"
              type="text"
              placeholder="Search users..."
              class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Role</label>
            <select
              v-model="usersStore.filters.role"
              @change="usersStore.setFilter('role', usersStore.filters.role)"
              class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">All Roles</option>
              <option value="super_admin">Super Admin</option>
              <option value="admin">Admin</option>
              <option value="manager">Manager</option>
              <option value="user">User</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Status</label>
            <select
              v-model="usersStore.filters.isActive"
              @change="usersStore.setFilter('isActive', usersStore.filters.isActive)"
              class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            >
              <option :value="null">All Status</option>
              <option :value="true">Active</option>
              <option :value="false">Inactive</option>
            </select>
          </div>
          <div class="flex items-end">
            <button
              @click="usersStore.clearFilters"
              class="w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Clear Filters
            </button>
          </div>
        </div>
      </div>

      <!-- Users Table -->
      <div class="bg-white shadow overflow-hidden sm:rounded-md">
        <div v-if="usersStore.loading" class="flex justify-center items-center py-12">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
        
        <div v-else-if="usersStore.error" class="bg-red-50 border border-red-200 rounded-md p-4">
          <div class="flex">
            <svg class="h-5 w-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
            </svg>
            <div class="ml-3">
              <p class="text-sm text-red-800">{{ usersStore.error }}</p>
            </div>
          </div>
        </div>

        <ul v-else class="divide-y divide-gray-200">
          <li v-for="user in usersStore.getPaginatedUsers" :key="user.id" class="px-6 py-4">
            <div class="flex items-center justify-between">
              <div class="flex items-center">
                <div class="flex-shrink-0 h-10 w-10">
                  <div class="h-10 w-10 rounded-full bg-gray-300 flex items-center justify-center">
                    <span class="text-sm font-medium text-gray-700">
                      {{ user.first_name.charAt(0) }}{{ user.last_name.charAt(0) }}
                    </span>
                  </div>
                </div>
                <div class="ml-4">
                  <div class="flex items-center">
                    <p class="text-sm font-medium text-gray-900">
                      {{ user.first_name }} {{ user.last_name }}
                    </p>
                    <span
                      :class="[
                        'ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
                        usersStore.getRoleColor(user.role) === 'red' ? 'bg-red-100 text-red-800' :
                        usersStore.getRoleColor(user.role) === 'blue' ? 'bg-blue-100 text-blue-800' :
                        usersStore.getRoleColor(user.role) === 'green' ? 'bg-green-100 text-green-800' :
                        'bg-gray-100 text-gray-800'
                      ]"
                    >
                      {{ usersStore.getRoleDisplayName(user.role) }}
                    </span>
                  </div>
                  <p class="text-sm text-gray-500">{{ user.email }}</p>
                  <p class="text-xs text-gray-400">@{{ user.username }}</p>
                </div>
              </div>
              <div class="flex items-center space-x-4">
                <div class="text-right">
                  <div class="flex items-center">
                    <span
                      :class="[
                        'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
                        user.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                      ]"
                    >
                      {{ user.is_active ? 'Active' : 'Inactive' }}
                    </span>
                    <span
                      v-if="user.is_verified"
                      class="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
                    >
                      Verified
                    </span>
                  </div>
                  <p class="text-xs text-gray-400 mt-1">
                    Last login: {{ usersStore.formatLastLogin(user.last_login) }}
                  </p>
                </div>
                <div class="flex space-x-2">
                  <button
                    @click="viewUser(user)"
                    class="text-blue-600 hover:text-blue-900 text-sm font-medium"
                  >
                    View
                  </button>
                  <button
                    @click="editUser(user)"
                    class="text-green-600 hover:text-green-900 text-sm font-medium"
                  >
                    Edit
                  </button>
                  <button
                    @click="deleteUser(user)"
                    class="text-red-600 hover:text-red-900 text-sm font-medium"
                  >
                    Delete
                  </button>
                </div>
              </div>
            </div>
          </li>
        </ul>

        <!-- Pagination -->
        <div v-if="usersStore.pagination.totalPages > 1" class="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6">
          <div class="flex-1 flex justify-between sm:hidden">
            <button
              @click="goToPreviousPage"
              :disabled="usersStore.pagination.currentPage === 1"
              class="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
            >
              Previous
            </button>
            <button
              @click="goToNextPage"
              :disabled="usersStore.pagination.currentPage === usersStore.pagination.totalPages"
              class="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
            >
              Next
            </button>
          </div>
          <div class="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
            <div>
              <p class="text-sm text-gray-700">
                Showing
                <span class="font-medium">{{ (usersStore.pagination.currentPage - 1) * usersStore.pagination.pageSize + 1 }}</span>
                to
                <span class="font-medium">{{ Math.min(usersStore.pagination.currentPage * usersStore.pagination.pageSize, usersStore.pagination.totalItems) }}</span>
                of
                <span class="font-medium">{{ usersStore.pagination.totalItems }}</span>
                results
              </p>
            </div>
            <div>
              <nav class="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
                <button
                  @click="goToPreviousPage"
                  :disabled="usersStore.pagination.currentPage === 1"
                  class="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50"
                >
                  Previous
                </button>
                <button
                  v-for="page in visiblePages"
                  :key="page"
                  @click="goToPage(page)"
                  :class="[
                    'relative inline-flex items-center px-4 py-2 border text-sm font-medium',
                    page === usersStore.pagination.currentPage
                      ? 'z-10 bg-blue-50 border-blue-500 text-blue-600'
                      : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'
                  ]"
                >
                  {{ page }}
                </button>
                <button
                  @click="goToNextPage"
                  :disabled="usersStore.pagination.currentPage === usersStore.pagination.totalPages"
                  class="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50"
                >
                  Next
                </button>
              </nav>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- User Form Modal -->
    <UserFormModal
      :show="showCreateUser || showEditUser"
      :user="selectedUser"
      :is-edit="showEditUser"
      @close="closeUserForm"
      @save="onUserSaved"
    />

    <!-- User Detail Modal -->
    <UserDetailModal
      :show="showUserDetail"
      :user="selectedUser"
      @close="showUserDetail = false"
      @edit="editUser"
    />
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { useUsersStore } from '@/stores/users'
import UserFormModal from '@/components/users/UserFormModal.vue'
import UserDetailModal from '@/components/users/UserDetailModal.vue'
import { debounce } from 'lodash-es'

export default {
  name: 'Users',
  components: {
    UserFormModal,
    UserDetailModal,
  },
  setup() {
    const usersStore = useUsersStore()
    
    const showCreateUser = ref(false)
    const showEditUser = ref(false)
    const showUserDetail = ref(false)
    const selectedUser = ref(null)

    const debouncedSearch = debounce(() => {
      usersStore.setFilter('search', usersStore.filters.search)
    }, 300)

    const visiblePages = computed(() => {
      const current = usersStore.pagination.currentPage
      const total = usersStore.pagination.totalPages
      const delta = 2
      
      let start = Math.max(1, current - delta)
      let end = Math.min(total, current + delta)
      
      if (end - start < 2 * delta) {
        if (start === 1) {
          end = Math.min(total, start + 2 * delta)
        } else {
          start = Math.max(1, end - 2 * delta)
        }
      }
      
      const pages = []
      for (let i = start; i <= end; i++) {
        pages.push(i)
      }
      return pages
    })

    const refreshData = async () => {
      await Promise.all([
        usersStore.fetchUsers(),
        usersStore.fetchUserStatistics()
      ])
    }

    const viewUser = (user) => {
      selectedUser.value = user
      showUserDetail.value = true
    }

    const editUser = (user) => {
      selectedUser.value = user
      showEditUser.value = true
      showUserDetail.value = false
    }

    const deleteUser = async (user) => {
      if (confirm(`Are you sure you want to delete user "${user.first_name} ${user.last_name}"?`)) {
        try {
          await usersStore.deleteUser(user.id)
        } catch (error) {
          console.error('Error deleting user:', error)
        }
      }
    }

    const closeUserForm = () => {
      showCreateUser.value = false
      showEditUser.value = false
      selectedUser.value = null
    }

    const onUserSaved = () => {
      closeUserForm()
      refreshData()
    }

    const goToPage = (page) => {
      usersStore.setCurrentPage(page)
    }

    const goToPreviousPage = () => {
      if (usersStore.pagination.currentPage > 1) {
        usersStore.setCurrentPage(usersStore.pagination.currentPage - 1)
      }
    }

    const goToNextPage = () => {
      if (usersStore.pagination.currentPage < usersStore.pagination.totalPages) {
        usersStore.setCurrentPage(usersStore.pagination.currentPage + 1)
      }
    }

    onMounted(() => {
      refreshData()
    })

    return {
      usersStore,
      showCreateUser,
      showEditUser,
      showUserDetail,
      selectedUser,
      debouncedSearch,
      visiblePages,
      refreshData,
      viewUser,
      editUser,
      deleteUser,
      closeUserForm,
      onUserSaved,
      goToPage,
      goToPreviousPage,
      goToNextPage,
    }
  },
}
</script>
