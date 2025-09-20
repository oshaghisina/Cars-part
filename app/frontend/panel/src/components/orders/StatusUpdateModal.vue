<template>
  <div class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
    <div class="relative top-20 mx-auto p-5 border w-full max-w-md shadow-lg rounded-md bg-white">
      <div class="mt-3">
        <!-- Header -->
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-medium text-gray-900">
            Update Order Status
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

        <!-- Order Info -->
        <div class="mb-4 p-3 bg-gray-50 rounded-lg">
          <p class="text-sm text-gray-600">Order #{{ order.id.toString().padStart(5, '0') }}</p>
          <p class="text-sm text-gray-500">Current Status: {{ getStatusText(order.status) }}</p>
        </div>

        <!-- Form -->
        <form @submit.prevent="updateStatus">
          <div class="mb-4">
            <label for="status" class="block text-sm font-medium text-gray-700 mb-2">
              New Status
            </label>
            <select
              id="status"
              v-model="newStatus"
              required
              class="w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
            >
              <option value="new">New</option>
              <option value="in_progress">In Progress</option>
              <option value="quoted">Quoted</option>
              <option value="won">Won</option>
              <option value="completed">Completed</option>
              <option value="lost">Lost</option>
              <option value="cancelled">Cancelled</option>
            </select>
          </div>

          <div class="mb-4">
            <label for="notes" class="block text-sm font-medium text-gray-700 mb-2">
              Notes (Optional)
            </label>
            <textarea
              id="notes"
              v-model="notes"
              rows="3"
              placeholder="Add any additional notes about this status change..."
              class="w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
            ></textarea>
          </div>

          <!-- Error Message -->
          <div v-if="error" class="mb-4 rounded-md bg-red-50 p-3">
            <div class="flex">
              <div class="flex-shrink-0">
                <svg class="h-5 w-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                </svg>
              </div>
              <div class="ml-3">
                <h3 class="text-sm font-medium text-red-800">Error</h3>
                <div class="mt-1 text-sm text-red-700">{{ error }}</div>
              </div>
            </div>
          </div>

          <!-- Form Actions -->
          <div class="flex justify-end space-x-3">
            <button
              type="button"
              @click="$emit('close')"
              class="inline-flex justify-center py-2 px-4 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Cancel
            </button>
            <button
              type="submit"
              :disabled="loading || newStatus === order.status"
              class="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <svg v-if="loading" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              {{ loading ? 'Updating...' : 'Update Status' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useOrdersStore } from '../../stores/orders'

export default {
  name: 'StatusUpdateModal',
  props: {
    order: {
      type: Object,
      required: true
    }
  },
  emits: ['close', 'updated'],
  setup(props, { emit }) {
    const ordersStore = useOrdersStore()
    
    const loading = ref(false)
    const error = ref(null)
    const newStatus = ref(props.order.status)
    const notes = ref('')

    const getStatusText = (status) => {
      return ordersStore.getStatusText(status)
    }

    const updateStatus = async () => {
      if (newStatus.value === props.order.status) {
        return
      }

      loading.value = true
      error.value = null
      
      try {
        await ordersStore.updateOrderStatus(props.order.id, newStatus.value, notes.value)
        emit('updated')
      } catch (err) {
        error.value = err.message || 'Failed to update order status'
      } finally {
        loading.value = false
      }
    }

    return {
      ordersStore,
      loading,
      error,
      newStatus,
      notes,
      getStatusText,
      updateStatus
    }
  }
}
</script>
