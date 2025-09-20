<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="bg-white shadow rounded-lg p-6">
      <div class="flex justify-between items-center">
        <div>
          <h1 class="text-2xl font-bold text-gray-900">Lead Management</h1>
          <p class="text-gray-600 mt-2">Track and manage customer leads with comprehensive profiles</p>
        </div>
        <div class="flex space-x-3">
          <button
            @click="exportLeads"
            class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Export
          </button>
          <button
            @click="refreshData"
            :disabled="leadsStore.loading"
            class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
          >
            <svg class="w-4 h-4 mr-2" :class="{ 'animate-spin': leadsStore.loading }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            {{ leadsStore.loading ? 'Refreshing...' : 'Refresh' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
      <div class="bg-white overflow-hidden shadow rounded-lg">
        <div class="p-5">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div class="w-8 h-8 bg-blue-500 rounded-md flex items-center justify-center">
                <span class="text-white text-sm font-medium">👥</span>
              </div>
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">Total Leads</dt>
                <dd class="text-lg font-medium text-gray-900">{{ leadsStore.stats.totalLeads }}</dd>
              </dl>
            </div>
          </div>
        </div>
      </div>

      <div class="bg-white overflow-hidden shadow rounded-lg">
        <div class="p-5">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div class="w-8 h-8 bg-green-500 rounded-md flex items-center justify-center">
                <span class="text-white text-sm font-medium">🆕</span>
              </div>
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">New Leads</dt>
                <dd class="text-lg font-medium text-gray-900">{{ leadsStore.stats.newLeads }}</dd>
              </dl>
            </div>
          </div>
        </div>
      </div>

      <div class="bg-white overflow-hidden shadow rounded-lg">
        <div class="p-5">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div class="w-8 h-8 bg-purple-500 rounded-md flex items-center justify-center">
                <span class="text-white text-sm font-medium">✅</span>
              </div>
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">Converted</dt>
                <dd class="text-lg font-medium text-gray-900">{{ leadsStore.stats.convertedLeads }}</dd>
              </dl>
            </div>
          </div>
        </div>
      </div>

      <div class="bg-white overflow-hidden shadow rounded-lg">
        <div class="p-5">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div class="w-8 h-8 bg-orange-500 rounded-md flex items-center justify-center">
                <span class="text-white text-sm font-medium">📊</span>
              </div>
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">Conversion Rate</dt>
                <dd class="text-lg font-medium text-gray-900">{{ formatPercentage(leadsStore.stats.conversionRate) }}</dd>
              </dl>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white shadow rounded-lg p-6">
      <h3 class="text-lg font-medium text-gray-900 mb-4">Filters</h3>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <!-- Search -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Search</label>
          <input
            v-model="leadsStore.filters.search"
            type="text"
            placeholder="Search leads..."
            class="w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
          />
        </div>

        <!-- City -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">City</label>
          <select
            v-model="leadsStore.filters.city"
            class="w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
          >
            <option value="">All Cities</option>
            <option v-for="city in leadsStore.uniqueCities" :key="city" :value="city">
              {{ city }}
            </option>
          </select>
        </div>

        <!-- Date From -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Date From</label>
          <input
            v-model="leadsStore.filters.dateFrom"
            type="date"
            class="w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
          />
        </div>

        <!-- Date To -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Date To</label>
          <input
            v-model="leadsStore.filters.dateTo"
            type="date"
            class="w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
          />
        </div>

        <!-- Clear Filters -->
        <div class="flex items-end">
          <button
            @click="clearFilters"
            class="w-full inline-flex justify-center items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            Clear Filters
          </button>
        </div>
      </div>
    </div>

    <!-- Leads Table -->
    <div class="bg-white shadow rounded-lg">
      <div class="px-6 py-4 border-b border-gray-200">
        <div class="flex justify-between items-center">
          <h3 class="text-lg font-medium text-gray-900">Leads</h3>
          <div class="flex items-center space-x-4">
            <span class="text-sm text-gray-500">
              Showing {{ leadsStore.leads.length }} of {{ leadsStore.pagination.total }} leads
            </span>
            <select
              v-model="pageSize"
              @change="onPageSizeChange"
              class="border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
            >
              <option value="20">20 per page</option>
              <option value="50">50 per page</option>
              <option value="100">100 per page</option>
            </select>
          </div>
        </div>
      </div>

      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Customer
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Contact
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Orders
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Value
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Created
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-if="leadsStore.loading">
              <td colspan="7" class="px-6 py-8 text-center">
                <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                <p class="mt-2 text-sm text-gray-500">Loading leads...</p>
              </td>
            </tr>
            
            <tr v-else-if="leadsStore.leads.length === 0">
              <td colspan="7" class="px-6 py-8 text-center">
                <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
                <h3 class="mt-2 text-sm font-medium text-gray-900">No leads found</h3>
                <p class="mt-1 text-sm text-gray-500">Get started by creating a new lead.</p>
              </td>
            </tr>

            <tr v-else v-for="lead in leadsStore.leads" :key="lead.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div class="flex-shrink-0 h-10 w-10">
                    <div class="h-10 w-10 rounded-full bg-gray-300 flex items-center justify-center">
                      <span class="text-sm font-medium text-gray-700">
                        {{ getInitials(leadsStore.getFullName(lead)) }}
                      </span>
                    </div>
                  </div>
                  <div class="ml-4">
                    <div class="text-sm font-medium text-gray-900">
                      {{ leadsStore.getFullName(lead) }}
                    </div>
                    <div class="text-sm text-gray-500">ID: {{ lead.id }}</div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900">{{ leadsStore.getDisplayPhone(lead.phone_e164) }}</div>
                <div class="text-sm text-gray-500">{{ leadsStore.getDisplayCity(lead.city) }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span
                  :class="[
                    getStatusBadgeClass(leadsStore.getLeadStatus(lead)),
                    'inline-flex px-2 py-1 text-xs font-semibold rounded-full'
                  ]"
                >
                  {{ leadsStore.getStatusText(leadsStore.getLeadStatus(lead)) }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900">{{ lead.orders?.length || 0 }} orders</div>
                <div class="text-xs text-gray-500">
                  {{ lead.orders?.length > 0 ? formatDate(lead.orders[lead.orders.length - 1].created_at) : 'No orders' }}
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">
                  ${{ formatCurrency(getLeadTotalValue(lead)) }}
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900">{{ formatDate(lead.created_at) }}</div>
                <div class="text-xs text-gray-500">{{ formatTime(lead.created_at) }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <div class="flex space-x-2">
                  <button
                    @click="viewLead(lead)"
                    class="text-blue-600 hover:text-blue-900"
                  >
                    View
                  </button>
                  <button
                    @click="editLead(lead)"
                    class="text-indigo-600 hover:text-indigo-900"
                  >
                    Edit
                  </button>
                  <button
                    @click="viewOrders(lead)"
                    class="text-green-600 hover:text-green-900"
                  >
                    Orders
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div v-if="leadsStore.pagination.totalPages > 1" class="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6">
        <div class="flex-1 flex justify-between sm:hidden">
          <button
            @click="goToPreviousPage"
            :disabled="leadsStore.pagination.page === 1"
            class="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Previous
          </button>
          <button
            @click="goToNextPage"
            :disabled="leadsStore.pagination.page === leadsStore.pagination.totalPages"
            class="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Next
          </button>
        </div>
        <div class="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
          <div>
            <p class="text-sm text-gray-700">
              Showing
              <span class="font-medium">{{ (leadsStore.pagination.page - 1) * leadsStore.pagination.limit + 1 }}</span>
              to
              <span class="font-medium">{{ Math.min(leadsStore.pagination.page * leadsStore.pagination.limit, leadsStore.pagination.total) }}</span>
              of
              <span class="font-medium">{{ leadsStore.pagination.total }}</span>
              results
            </p>
          </div>
          <div>
            <nav class="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
              <button
                @click="goToPreviousPage"
                :disabled="leadsStore.pagination.page === 1"
                class="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <span class="sr-only">Previous</span>
                <svg class="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clip-rule="evenodd" />
                </svg>
              </button>
              
              <button
                v-for="page in visiblePages"
                :key="page"
                @click="goToPage(page)"
                :class="[
                  page === leadsStore.pagination.page
                    ? 'z-10 bg-blue-50 border-blue-500 text-blue-600'
                    : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50',
                  'relative inline-flex items-center px-4 py-2 border text-sm font-medium'
                ]"
              >
                {{ page }}
              </button>
              
              <button
                @click="goToNextPage"
                :disabled="leadsStore.pagination.page === leadsStore.pagination.totalPages"
                class="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <span class="sr-only">Next</span>
                <svg class="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
                </svg>
              </button>
            </nav>
          </div>
        </div>
      </div>
    </div>

    <!-- Lead Detail Modal will be added here -->
    <LeadDetailModal v-if="showLeadModal" :lead="selectedLead" @close="showLeadModal = false" @updated="onLeadUpdated" />
    
    <!-- Lead Form Modal will be added here -->
    <LeadFormModal v-if="showFormModal" :lead="selectedLead" @close="showFormModal = false" @saved="onLeadSaved" />
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useLeadsStore } from '../../stores/leads'
import LeadDetailModal from '../../components/leads/LeadDetailModal.vue'
import LeadFormModal from '../../components/leads/LeadFormModal.vue'

export default {
  name: 'Leads',
  components: {
    LeadDetailModal,
    LeadFormModal
  },
  setup() {
    const router = useRouter()
    const leadsStore = useLeadsStore()
    
    const showLeadModal = ref(false)
    const showFormModal = ref(false)
    const selectedLead = ref(null)
    const pageSize = ref(20)

    const visiblePages = computed(() => {
      const current = leadsStore.pagination.page
      const total = leadsStore.pagination.totalPages
      const pages = []
      
      if (total <= 7) {
        for (let i = 1; i <= total; i++) {
          pages.push(i)
        }
      } else {
        if (current <= 4) {
          for (let i = 1; i <= 5; i++) {
            pages.push(i)
          }
          pages.push('...')
          pages.push(total)
        } else if (current >= total - 3) {
          pages.push(1)
          pages.push('...')
          for (let i = total - 4; i <= total; i++) {
            pages.push(i)
          }
        } else {
          pages.push(1)
          pages.push('...')
          for (let i = current - 1; i <= current + 1; i++) {
            pages.push(i)
          }
          pages.push('...')
          pages.push(total)
        }
      }
      
      return pages
    })

    const getInitials = (name) => {
      return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
    }

    const getLeadTotalValue = (lead) => {
      if (!lead.orders) return 0
      return lead.orders.reduce((total, order) => {
        return total + leadsStore.calculateOrderValue(order)
      }, 0)
    }

    const getStatusBadgeClass = (status) => {
      const color = leadsStore.getStatusColor(status)
      const classes = {
        green: 'bg-green-100 text-green-800',
        blue: 'bg-blue-100 text-blue-800',
        purple: 'bg-purple-100 text-purple-800',
        gray: 'bg-gray-100 text-gray-800'
      }
      return classes[color] || classes.gray
    }

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString()
    }

    const formatTime = (dateString) => {
      return new Date(dateString).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }

    const formatCurrency = (amount) => {
      return parseFloat(amount || 0).toFixed(2)
    }

    const formatPercentage = (value) => {
      return parseFloat(value || 0).toFixed(1) + '%'
    }

    const refreshData = async () => {
      await leadsStore.fetchLeads()
    }

    const onPageSizeChange = () => {
      leadsStore.setLimit(parseInt(pageSize.value))
      fetchLeadsWithFilters()
    }

    const clearFilters = () => {
      leadsStore.clearFilters()
      fetchLeadsWithFilters()
    }

    const fetchLeadsWithFilters = () => {
      const params = {
        page: leadsStore.pagination.page,
        limit: leadsStore.pagination.limit,
        ...leadsStore.filters
      }
      leadsStore.fetchLeads(params)
    }

    const goToPage = (page) => {
      if (page !== '...') {
        leadsStore.setPage(page)
        fetchLeadsWithFilters()
      }
    }

    const goToPreviousPage = () => {
      if (leadsStore.pagination.page > 1) {
        leadsStore.setPage(leadsStore.pagination.page - 1)
        fetchLeadsWithFilters()
      }
    }

    const goToNextPage = () => {
      if (leadsStore.pagination.page < leadsStore.pagination.totalPages) {
        leadsStore.setPage(leadsStore.pagination.page + 1)
        fetchLeadsWithFilters()
      }
    }

    const viewLead = (lead) => {
      selectedLead.value = lead
      showLeadModal.value = true
    }

    const editLead = (lead) => {
      selectedLead.value = lead
      showFormModal.value = true
    }

    const viewOrders = (lead) => {
      router.push(`/orders?lead_id=${lead.id}`)
    }

    const exportLeads = () => {
      leadsStore.exportLeads('csv')
    }

    const onLeadUpdated = () => {
      showLeadModal.value = false
      selectedLead.value = null
      fetchLeadsWithFilters()
    }

    const onLeadSaved = () => {
      showFormModal.value = false
      selectedLead.value = null
      fetchLeadsWithFilters()
    }

    // Watch for filter changes
    watch(() => leadsStore.filters, () => {
      fetchLeadsWithFilters()
    }, { deep: true })

    onMounted(async () => {
      await refreshData()
    })

    return {
      leadsStore,
      showLeadModal,
      showFormModal,
      selectedLead,
      pageSize,
      visiblePages,
      getInitials,
      getLeadTotalValue,
      getStatusBadgeClass,
      formatDate,
      formatTime,
      formatCurrency,
      formatPercentage,
      refreshData,
      onPageSizeChange,
      clearFilters,
      goToPage,
      goToPreviousPage,
      goToNextPage,
      viewLead,
      editLead,
      viewOrders,
      exportLeads,
      onLeadUpdated,
      onLeadSaved
    }
  }
}
</script>
