<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="bg-white shadow rounded-lg p-6">
      <div class="flex justify-between items-center">
        <div>
          <h1 class="text-2xl font-bold text-gray-900">Orders</h1>
          <p class="text-gray-600 mt-2">Manage and track all orders</p>
        </div>
        <div class="flex space-x-3">
          <select
            v-model="selectedStatus"
            @change="filterOrders"
            class="px-3 py-2 border border-gray-300 rounded-md text-sm"
          >
            <option value="">All Status</option>
            <option value="new">New</option>
            <option value="in_progress">In Progress</option>
            <option value="quoted">Quoted</option>
            <option value="won">Completed</option>
            <option value="lost">Lost</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Orders Table -->
    <div class="bg-white shadow rounded-lg">
      <div class="px-4 py-5 sm:p-6">
        <div v-if="ordersStore.loading" class="text-center py-8">
          <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p class="mt-2 text-sm text-gray-500">Loading orders...</p>
        </div>
        
        <div v-else-if="ordersStore.error" class="text-center py-8">
          <p class="text-red-500">{{ ordersStore.error }}</p>
          <button
            @click="ordersStore.fetchOrders(selectedStatus)"
            class="mt-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
        
        <div v-else-if="ordersStore.orders.length === 0" class="text-center py-8">
          <p class="text-gray-500">No orders found</p>
        </div>
        
        <div v-else class="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
          <table class="min-w-full divide-y divide-gray-300">
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
                  Customer
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
              <tr v-for="order in ordersStore.orders" :key="order.id">
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  #{{ order.id.toString().padStart(5, '0') }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <select
                    :value="order.status"
                    @change="updateOrderStatus(order.id, $event.target.value)"
                    :class="getStatusBadgeClass(order.status)"
                    class="text-xs font-semibold rounded-full px-2 py-1 border-0 bg-transparent"
                  >
                    <option value="new">New</option>
                    <option value="in_progress">In Progress</option>
                    <option value="quoted">Quoted</option>
                    <option value="won">Completed</option>
                    <option value="lost">Lost</option>
                  </select>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ order.items.length }} items
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  Lead #{{ order.lead_id }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ formatDate(order.created_at) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                  <router-link
                    :to="`/orders/${order.id}`"
                    class="text-blue-600 hover:text-blue-900"
                  >
                    View
                  </router-link>
                  <button
                    @click="updateOrderStatus(order.id, getNextStatus(order.status))"
                    class="text-green-600 hover:text-green-900"
                  >
                    {{ getNextStatusText(order.status) }}
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <!-- Pagination -->
        <div v-if="ordersStore.orders.length > 0" class="mt-4 flex justify-between items-center">
          <div class="text-sm text-gray-500">
            Showing {{ ordersStore.orders.length }} orders
          </div>
          <div class="flex space-x-2">
            <button
              @click="previousPage"
              :disabled="ordersStore.pagination.page === 1"
              class="px-3 py-1 text-sm border rounded-md disabled:opacity-50"
            >
              Previous
            </button>
            <button
              @click="nextPage"
              class="px-3 py-1 text-sm border rounded-md"
            >
              Next
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useOrdersStore } from '../stores/orders'

export default {
  name: 'Orders',
  setup() {
    const ordersStore = useOrdersStore()
    const selectedStatus = ref('')
    
    onMounted(() => {
      ordersStore.fetchOrders()
    })
    
    const filterOrders = () => {
      ordersStore.fetchOrders(selectedStatus.value || null)
    }
    
    const updateOrderStatus = async (orderId, newStatus) => {
      await ordersStore.updateOrderStatus(orderId, newStatus)
    }
    
    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString()
    }
    
    const getStatusBadgeClass = (status) => {
      const classes = {
        'new': 'text-yellow-800',
        'in_progress': 'text-blue-800',
        'quoted': 'text-purple-800',
        'won': 'text-green-800',
        'lost': 'text-red-800'
      }
      return classes[status] || 'text-gray-800'
    }
    
    const getNextStatus = (currentStatus) => {
      const statusFlow = {
        'new': 'in_progress',
        'in_progress': 'quoted',
        'quoted': 'won',
        'won': 'won',
        'lost': 'lost'
      }
      return statusFlow[currentStatus] || 'in_progress'
    }
    
    const getNextStatusText = (currentStatus) => {
      const nextStatus = getNextStatus(currentStatus)
      const texts = {
        'in_progress': 'Start',
        'quoted': 'Quote',
        'won': 'Complete',
        'lost': 'Lost'
      }
      return texts[nextStatus] || 'Update'
    }
    
    const previousPage = () => {
      if (ordersStore.pagination.page > 1) {
        ordersStore.setPage(ordersStore.pagination.page - 1)
      }
    }
    
    const nextPage = () => {
      ordersStore.setPage(ordersStore.pagination.page + 1)
    }
    
    return {
      ordersStore,
      selectedStatus,
      filterOrders,
      updateOrderStatus,
      formatDate,
      getStatusBadgeClass,
      getNextStatus,
      getNextStatusText,
      previousPage,
      nextPage
    }
  }
}
</script>
