<template>
  <div class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
    <div class="relative top-4 mx-auto p-5 border w-full max-w-4xl shadow-lg rounded-md bg-white">
      <div class="mt-3">
        <!-- Header -->
        <div class="flex justify-between items-center mb-6">
          <div>
            <h3 class="text-lg font-medium text-gray-900">
              Lead Profile - {{ leadsStore.getFullName(lead) }}
            </h3>
            <p class="text-sm text-gray-500">Lead ID: {{ lead.id }} | Created: {{ formatDate(lead.created_at) }}</p>
          </div>
          <button
            @click="$emit('close')"
            class="text-gray-400 hover:text-gray-600"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Lead Status and Actions -->
        <div class="mb-6 p-4 bg-gray-50 rounded-lg">
          <div class="flex justify-between items-center">
            <div class="flex items-center space-x-4">
              <span class="text-sm font-medium text-gray-700">Status:</span>
              <span
                :class="[
                  getStatusBadgeClass(leadsStore.getLeadStatus(lead)),
                  'inline-flex px-3 py-1 text-sm font-semibold rounded-full'
                ]"
              >
                {{ leadsStore.getStatusText(leadsStore.getLeadStatus(lead)) }}
              </span>
            </div>
            <div class="flex space-x-2">
              <button
                @click="editLead"
                class="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                Edit Lead
              </button>
              <button
                @click="viewOrders"
                class="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                View Orders
              </button>
            </div>
          </div>
        </div>

        <!-- Customer Information -->
        <div class="mb-6">
          <h4 class="text-md font-medium text-gray-900 mb-3">Customer Information</h4>
          <div class="bg-white border border-gray-200 rounded-lg p-4">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700">Full Name</label>
                <p class="mt-1 text-sm text-gray-900">{{ leadsStore.getFullName(lead) }}</p>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700">Phone Number</label>
                <p class="mt-1 text-sm text-gray-900">{{ leadsStore.getDisplayPhone(lead.phone_e164) }}</p>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700">Telegram ID</label>
                <p class="mt-1 text-sm text-gray-900">{{ lead.telegram_user_id || 'Not provided' }}</p>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700">City</label>
                <p class="mt-1 text-sm text-gray-900">{{ leadsStore.getDisplayCity(lead.city) }}</p>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700">Consent</label>
                <p class="mt-1 text-sm text-gray-900">
                  <span :class="[
                    'inline-flex px-2 py-1 text-xs font-semibold rounded-full',
                    lead.consent ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                  ]">
                    {{ lead.consent ? 'Given' : 'Not Given' }}
                  </span>
                </p>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700">Created</label>
                <p class="mt-1 text-sm text-gray-900">{{ formatDate(lead.created_at) }} at {{ formatTime(lead.created_at) }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Lead Notes -->
        <div v-if="lead.notes" class="mb-6">
          <h4 class="text-md font-medium text-gray-900 mb-3">Notes</h4>
          <div class="bg-white border border-gray-200 rounded-lg p-4">
            <p class="text-sm text-gray-900">{{ lead.notes }}</p>
          </div>
        </div>

        <!-- Lead Statistics -->
        <div class="mb-6">
          <h4 class="text-md font-medium text-gray-900 mb-3">Lead Statistics</h4>
          <div class="bg-white border border-gray-200 rounded-lg p-4">
            <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700">Total Orders</label>
                <p class="mt-1 text-2xl font-semibold text-gray-900">{{ lead.orders?.length || 0 }}</p>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700">Total Value</label>
                <p class="mt-1 text-2xl font-semibold text-gray-900">${{ formatCurrency(getLeadTotalValue()) }}</p>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700">Last Order</label>
                <p class="mt-1 text-sm text-gray-900">
                  {{ getLastOrderDate() || 'No orders' }}
                </p>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700">Average Order Value</label>
                <p class="mt-1 text-sm text-gray-900">
                  {{ lead.orders?.length > 0 ? '$' + formatCurrency(getLeadTotalValue() / lead.orders.length) : 'N/A' }}
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Recent Orders -->
        <div class="mb-6">
          <h4 class="text-md font-medium text-gray-900 mb-3">Recent Orders</h4>
          <div class="bg-white border border-gray-200 rounded-lg overflow-hidden">
            <div v-if="!lead.orders || lead.orders.length === 0" class="p-6 text-center">
              <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
              </svg>
              <h3 class="mt-2 text-sm font-medium text-gray-900">No orders yet</h3>
              <p class="mt-1 text-sm text-gray-500">This lead hasn't placed any orders.</p>
            </div>
            <table v-else class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Order ID
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Items
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Value
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Date
                  </th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="order in lead.orders.slice(0, 5)" :key="order.id">
                  <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    #{{ order.id.toString().padStart(5, '0') }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <span
                      :class="[
                        getOrderStatusBadgeClass(order.status),
                        'inline-flex px-2 py-1 text-xs font-semibold rounded-full'
                      ]"
                    >
                      {{ getOrderStatusText(order.status) }}
                    </span>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {{ order.items.length }} items
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    ${{ formatCurrency(leadsStore.calculateOrderValue(order)) }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {{ formatDate(order.created_at) }}
                  </td>
                </tr>
              </tbody>
            </table>
            <div v-if="lead.orders.length > 5" class="px-6 py-3 bg-gray-50 border-t border-gray-200">
              <p class="text-sm text-gray-500">
                Showing 5 of {{ lead.orders.length }} orders. 
                <button @click="viewAllOrders" class="text-blue-600 hover:text-blue-900 font-medium">
                  View all orders →
                </button>
              </p>
            </div>
          </div>
        </div>

        <!-- Error Message -->
        <div v-if="error" class="mb-4 rounded-md bg-red-50 p-4">
          <div class="flex">
            <div class="flex-shrink-0">
              <svg class="h-5 w-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
              </svg>
            </div>
            <div class="ml-3">
              <h3 class="text-sm font-medium text-red-800">Error</h3>
              <div class="mt-2 text-sm text-red-700">{{ error }}</div>
            </div>
          </div>
        </div>

        <!-- Form Actions -->
        <div class="flex justify-end space-x-3 pt-4 border-t border-gray-200">
          <button
            type="button"
            @click="$emit('close')"
            class="inline-flex justify-center py-2 px-4 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useLeadsStore } from '../../stores/leads'

export default {
  name: 'LeadDetailModal',
  props: {
    lead: {
      type: Object,
      required: true
    }
  },
  emits: ['close', 'updated'],
  setup(props, { emit }) {
    const router = useRouter()
    const leadsStore = useLeadsStore()
    
    const error = ref(null)

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

    const getOrderStatusBadgeClass = (status) => {
      const classes = {
        'new': 'bg-yellow-100 text-yellow-800',
        'in_progress': 'bg-blue-100 text-blue-800',
        'quoted': 'bg-purple-100 text-purple-800',
        'won': 'bg-green-100 text-green-800',
        'completed': 'bg-green-100 text-green-800',
        'lost': 'bg-red-100 text-red-800',
        'cancelled': 'bg-gray-100 text-gray-800'
      }
      return classes[status] || classes.gray
    }

    const getOrderStatusText = (status) => {
      const texts = {
        'new': 'New',
        'in_progress': 'In Progress',
        'quoted': 'Quoted',
        'won': 'Won',
        'completed': 'Completed',
        'lost': 'Lost',
        'cancelled': 'Cancelled'
      }
      return texts[status] || status
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

    const getLeadTotalValue = () => {
      if (!props.lead.orders) return 0
      return props.lead.orders.reduce((total, order) => {
        return total + leadsStore.calculateOrderValue(order)
      }, 0)
    }

    const getLastOrderDate = () => {
      if (!props.lead.orders || props.lead.orders.length === 0) return null
      const lastOrder = props.lead.orders[props.lead.orders.length - 1]
      return formatDate(lastOrder.created_at)
    }

    const editLead = () => {
      emit('editLead', props.lead)
    }

    const viewOrders = () => {
      router.push(`/orders?lead_id=${props.lead.id}`)
    }

    const viewAllOrders = () => {
      router.push(`/orders?lead_id=${props.lead.id}`)
    }

    return {
      leadsStore,
      error,
      getStatusBadgeClass,
      getOrderStatusBadgeClass,
      getOrderStatusText,
      formatDate,
      formatTime,
      formatCurrency,
      getLeadTotalValue,
      getLastOrderDate,
      editLead,
      viewOrders,
      viewAllOrders
    }
  }
}
</script>
