<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="bg-white shadow rounded-lg p-6">
      <div class="flex justify-between items-center">
        <div>
          <div class="flex items-center space-x-3">
            <router-link
              to="/orders"
              class="text-blue-600 hover:text-blue-900"
            >
              ← Back to Orders
            </router-link>
            <h1 class="text-2xl font-bold text-gray-900">
              Order #{{ orderId?.toString().padStart(5, '0') }}
            </h1>
          </div>
          <p class="text-gray-600 mt-2">Order details and management</p>
        </div>
        <div class="flex space-x-3">
          <select
            v-if="ordersStore.currentOrder"
            :value="ordersStore.currentOrder.status"
            @change="updateStatus($event.target.value)"
            class="px-3 py-2 border border-gray-300 rounded-md text-sm"
          >
            <option value="new">New</option>
            <option value="in_progress">In Progress</option>
            <option value="quoted">Quoted</option>
            <option value="won">Completed</option>
            <option value="lost">Lost</option>
          </select>
        </div>
      </div>
    </div>

    <div v-if="ordersStore.loading" class="text-center py-8">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      <p class="mt-2 text-sm text-gray-500">Loading order...</p>
    </div>
    
    <div v-else-if="ordersStore.error" class="text-center py-8">
      <p class="text-red-500">{{ ordersStore.error }}</p>
      <button
        @click="loadOrder"
        class="mt-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
      >
        Retry
      </button>
    </div>
    
    <div v-else-if="ordersStore.currentOrder" class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Order Information -->
      <div class="lg:col-span-2 space-y-6">
        <!-- Order Items -->
        <div class="bg-white shadow rounded-lg p-6">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Order Items</h3>
          
          <div v-if="ordersStore.currentOrder.items.length === 0" class="text-center py-4">
            <p class="text-gray-500">No items in this order</p>
          </div>
          
          <div v-else class="space-y-4">
            <div
              v-for="item in ordersStore.currentOrder.items"
              :key="item.line_no"
              class="border border-gray-200 rounded-lg p-4"
            >
              <div class="flex justify-between items-start">
                <div class="flex-1">
                  <h4 class="font-medium text-gray-900">
                    Item #{{ item.line_no }}
                  </h4>
                  <p class="text-sm text-gray-600 mt-1">
                    Query: "{{ item.query_text }}"
                  </p>
                  <div class="mt-2 flex items-center space-x-4 text-sm">
                    <span class="text-gray-500">
                      Qty: {{ item.qty }} {{ item.unit }}
                    </span>
                    <span
                      v-if="item.matched_part_id"
                      class="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800"
                    >
                      Matched to Part #{{ item.matched_part_id }}
                    </span>
                    <span
                      v-else
                      class="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800"
                    >
                      No Match Found
                    </span>
                  </div>
                  <p v-if="item.notes" class="text-sm text-gray-500 mt-2">
                    Notes: {{ item.notes }}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Order Notes -->
        <div class="bg-white shadow rounded-lg p-6">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Order Notes</h3>
          <textarea
            v-model="notes"
            @blur="updateNotes"
            rows="4"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Add order notes..."
          ></textarea>
        </div>
      </div>

      <!-- Order Summary -->
      <div class="space-y-6">
        <!-- Order Status -->
        <div class="bg-white shadow rounded-lg p-6">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Order Status</h3>
          
          <div class="space-y-3">
            <div class="flex justify-between">
              <span class="text-sm text-gray-500">Status:</span>
              <span :class="getStatusBadgeClass(ordersStore.currentOrder.status)" class="inline-flex px-2 py-1 text-xs font-semibold rounded-full">
                {{ getStatusText(ordersStore.currentOrder.status) }}
              </span>
            </div>
            
            <div class="flex justify-between">
              <span class="text-sm text-gray-500">Created:</span>
              <span class="text-sm text-gray-900">{{ formatDate(ordersStore.currentOrder.created_at) }}</span>
            </div>
            
            <div class="flex justify-between">
              <span class="text-sm text-gray-500">Updated:</span>
              <span class="text-sm text-gray-900">{{ formatDate(ordersStore.currentOrder.updated_at) }}</span>
            </div>
            
            <div class="flex justify-between">
              <span class="text-sm text-gray-500">Items:</span>
              <span class="text-sm text-gray-900">{{ ordersStore.currentOrder.items.length }}</span>
            </div>
            
            <div class="flex justify-between">
              <span class="text-sm text-gray-500">Matched:</span>
              <span class="text-sm text-gray-900">
                {{ ordersStore.currentOrder.items.filter(item => item.matched_part_id).length }} / {{ ordersStore.currentOrder.items.length }}
              </span>
            </div>
          </div>
        </div>

        <!-- Customer Information -->
        <div class="bg-white shadow rounded-lg p-6">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Customer</h3>
          <p class="text-sm text-gray-500">Lead ID: {{ ordersStore.currentOrder.lead_id }}</p>
          <router-link
            :to="`/leads/${ordersStore.currentOrder.lead_id}`"
            class="text-blue-600 hover:text-blue-900 text-sm"
          >
            View Customer Details →
          </router-link>
        </div>

        <!-- Quick Actions -->
        <div class="bg-white shadow rounded-lg p-6">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Quick Actions</h3>
          <div class="space-y-2">
            <button
              v-if="ordersStore.currentOrder.status === 'new'"
              @click="updateStatus('in_progress')"
              class="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 text-sm"
            >
              Start Processing
            </button>
            <button
              v-if="ordersStore.currentOrder.status === 'in_progress'"
              @click="updateStatus('quoted')"
              class="w-full px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 text-sm"
            >
              Mark as Quoted
            </button>
            <button
              v-if="ordersStore.currentOrder.status === 'quoted'"
              @click="updateStatus('won')"
              class="w-full px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 text-sm"
            >
              Mark as Completed
            </button>
            <button
              @click="updateStatus('lost')"
              class="w-full px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 text-sm"
            >
              Mark as Lost
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useOrdersStore } from '../stores/orders'

export default {
  name: 'OrderDetail',
  setup() {
    const route = useRoute()
    const ordersStore = useOrdersStore()
    const orderId = ref(null)
    const notes = ref('')
    
    const loadOrder = async () => {
      if (orderId.value) {
        await ordersStore.fetchOrder(orderId.value)
        if (ordersStore.currentOrder) {
          notes.value = ordersStore.currentOrder.notes || ''
        }
      }
    }
    
    onMounted(() => {
      orderId.value = parseInt(route.params.id)
      loadOrder()
    })
    
    watch(() => route.params.id, (newId) => {
      orderId.value = parseInt(newId)
      loadOrder()
    })
    
    const updateStatus = async (newStatus) => {
      if (orderId.value) {
        await ordersStore.updateOrderStatus(orderId.value, newStatus, notes.value)
      }
    }
    
    const updateNotes = async () => {
      if (orderId.value && notes.value !== ordersStore.currentOrder?.notes) {
        await ordersStore.updateOrderStatus(orderId.value, ordersStore.currentOrder.status, notes.value)
      }
    }
    
    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleString()
    }
    
    const getStatusBadgeClass = (status) => {
      const classes = {
        'new': 'bg-yellow-100 text-yellow-800',
        'in_progress': 'bg-blue-100 text-blue-800',
        'quoted': 'bg-purple-100 text-purple-800',
        'won': 'bg-green-100 text-green-800',
        'lost': 'bg-red-100 text-red-800'
      }
      return classes[status] || 'bg-gray-100 text-gray-800'
    }
    
    const getStatusText = (status) => {
      const texts = {
        'new': 'New',
        'in_progress': 'In Progress',
        'quoted': 'Quoted',
        'won': 'Completed',
        'lost': 'Lost'
      }
      return texts[status] || status
    }
    
    return {
      ordersStore,
      orderId,
      notes,
      loadOrder,
      updateStatus,
      updateNotes,
      formatDate,
      getStatusBadgeClass,
      getStatusText
    }
  }
}
</script>
