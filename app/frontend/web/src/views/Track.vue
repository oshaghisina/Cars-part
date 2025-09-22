<template>
  <div class="track">
    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 class="text-3xl font-bold text-gray-900 mb-8 font-persian font-persian" class="font-persian-bold text-rtl">Track Your Order</h1>
      
      <!-- Search Form -->
      <div class="bg-white rounded-lg shadow-md p-6 mb-8">
        <form @submit.prevent="trackOrder" class="space-y-4">
          <div class="flex gap-4">
            <div class="flex-1">
              <label class="block text-sm font-medium text-gray-700 mb-2 font-persian font-persian">شماره سفارش</label>
              <input
                v-model="orderNumber"
                type="text"
                placeholder="Enter your order number"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div class="flex items-end">
              <button
                type="submit"
                :disabled="loading"
                class="bg-blue-600 text-white px-6 py-2 rounded-md font-semibold hover:bg-blue-700 disabled:opacity-50 font-persian font-persian"
              >
                {{ loading ? 'Tracking...' : 'پیگیری سفارش' }}
              </button>
            </div>
          </div>
        </form>
      </div>

      <!-- Order Details -->
      <div v-if="order" class="space-y-6">
        <!-- Order Summary -->
        <div class="bg-white rounded-lg shadow-md p-6">
          <h2 class="text-xl font-semibold text-gray-900 mb-4 font-persian font-persian" class="font-persian-bold text-rtl">خلاصه سفارش</h2>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <p class="text-sm text-gray-600 font-persian font-persian" class="font-persian text-rtl">شماره سفارش</p>
              <p class="font-semibold font-persian" class="font-persian text-rtl">{{ order.number }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-600 font-persian font-persian" class="font-persian text-rtl">تاریخ سفارش</p>
              <p class="font-semibold font-persian" class="font-persian text-rtl">{{ order.date }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-600 font-persian font-persian" class="font-persian text-rtl">Status</p>
              <span :class="getStatusClass(order.status)" class="px-3 py-1 rounded-full text-sm font-semibold font-persian font-persian">
                {{ order.status }}
              </span>
            </div>
            <div>
              <p class="text-sm text-gray-600 font-persian font-persian" class="font-persian text-rtl">Total Amount</p>
              <p class="font-semibold text-lg text-blue-600 font-persian font-persian" class="font-persian text-rtl">${{ order.total }}</p>
            </div>
          </div>
        </div>

        <!-- Tracking Timeline -->
        <div class="bg-white rounded-lg shadow-md p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4 font-persian font-persian" class="font-persian-bold text-rtl">Tracking Timeline</h3>
          <div class="space-y-4">
            <div
              v-for="(event, index) in order.timeline"
              :key="index"
              class="flex items-start space-x-3"
            >
              <div :class="getTimelineDotClass(event.status)" class="w-3 h-3 rounded-full mt-2"></div>
              <div class="flex-1">
                <p class="font-semibold text-gray-900 font-persian font-persian" class="font-persian text-rtl">{{ event.title }}</p>
                <p class="text-sm text-gray-600 font-persian font-persian" class="font-persian text-rtl">{{ event.description }}</p>
                <p class="text-xs text-gray-500 font-persian font-persian" class="font-persian text-rtl">{{ event.timestamp }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Order Items -->
        <div class="bg-white rounded-lg shadow-md p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4 font-persian font-persian" class="font-persian-bold text-rtl">اقلام سفارش</h3>
          <div class="space-y-3">
            <div
              v-for="item in order.items"
              :key="item.id"
              class="flex justify-between items-center py-2 border-b border-gray-200 last:border-b-0"
            >
              <div>
                <p class="font-semibold font-persian" class="font-persian text-rtl">{{ item.name }}</p>
                <p class="text-sm text-gray-600 font-persian font-persian" class="font-persian text-rtl">{{ item.description }}</p>
              </div>
              <div class="text-right font-persian font-persian">
                <p class="font-semibold font-persian" class="font-persian text-rtl">${{ item.price }}</p>
                <p class="text-sm text-gray-600 font-persian font-persian" class="font-persian text-rtl">Qty: {{ item.quantity }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="text-center py-12 font-persian font-persian">
        <div class="text-6xl mb-4 font-persian font-persian">❌</div>
        <h3 class="text-xl font-semibold text-gray-900 mb-2 font-persian font-persian" class="font-persian-bold text-rtl">Tracking Error</h3>
        <p class="text-gray-600 mb-4 font-persian font-persian" class="font-persian text-rtl">{{ error }}</p>
        <button
          @click="trackOrder"
          class="bg-blue-600 text-white px-6 py-2 rounded-lg font-semibold hover:bg-blue-700 font-persian font-persian"
        >
          Try Again
        </button>
      </div>

      <!-- No Order Found -->
      <div v-else-if="hasSearched && !loading" class="text-center py-12 font-persian font-persian">
        <div class="text-6xl mb-4 font-persian font-persian">📦</div>
        <h3 class="text-xl font-semibold text-gray-900 mb-2 font-persian font-persian" class="font-persian-bold text-rtl">Order not found</h3>
        <p class="text-gray-600 mb-4 font-persian font-persian" class="font-persian text-rtl">Please check your order number and try again.</p>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="text-center py-12 font-persian font-persian">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <p class="mt-2 text-gray-600 font-persian font-persian" class="font-persian text-rtl">Tracking order...</p>
      </div>
    </div>
  </div>
</template>

<script>
import apiService from '../services/api.js'

export default {
  name: 'پیگیری',
  data() {
    return {
      orderNumber: '',
      order: null,
      loading: false,
      hasSearched: false,
      error: null
    }
  },
  methods: {
    async trackOrder() {
      if (!this.orderNumber.trim()) return
      
      this.loading = true
      this.hasSearched = true
      this.error = null
      
      try {
        // Try to find order by ID
        const orderId = parseInt(this.orderNumber)
        if (isNaN(orderId)) {
          throw new Error('Please enter a valid order number')
        }
        
        // Get order from API
        const order = await apiService.getOrder(orderId)
        
        if (!order) {
          throw new Error('Order not found. Please check your order number.')
        }
        
        // Format order for display
        this.order = {
          ...apiService.formatOrderForDisplay(order),
          timeline: this.generateTimeline(order.status),
          items: this.formatOrderItems(order.items || [])
        }
        
      } catch (error) {
        console.error('Tracking error:', error)
        this.error = error.message || 'Failed to track order. Please try again.'
        this.order = null
      } finally {
        this.loading = false
      }
    },
    
    generateTimeline(status) {
      const baseTimeline = [
        {
          title: 'Order Placed',
          description: 'Your order has been received and is being processed.',
          timestamp: 'Just now',
          status: 'completed'
        }
      ]
      
      const statusTimeline = {
        'pending': [
          {
            title: 'Order Processing',
            description: 'Your order is being prepared.',
            timestamp: 'In progress',
            status: 'current'
          }
        ],
        'processing': [
          {
            title: 'Order Processing',
            description: 'Your order is being prepared.',
            timestamp: 'In progress',
            status: 'current'
          }
        ],
        'shipped': [
          {
            title: 'Order Processed',
            description: 'Your order has been prepared for shipment.',
            timestamp: 'Completed',
            status: 'completed'
          },
          {
            title: 'ارسال شده',
            description: 'Your order has been shipped and is on its way.',
            timestamp: 'In progress',
            status: 'current'
          }
        ],
        'delivered': [
          {
            title: 'Order Processed',
            description: 'Your order has been prepared for shipment.',
            timestamp: 'Completed',
            status: 'completed'
          },
          {
            title: 'ارسال شده',
            description: 'Your order has been shipped and is on its way.',
            timestamp: 'Completed',
            status: 'completed'
          },
          {
            title: 'تحویل داده شده',
            description: 'Your order has been delivered successfully.',
            timestamp: 'Completed',
            status: 'completed'
          }
        ],
        'cancelled': [
          {
            title: 'Order Cancelled',
            description: 'Your order has been cancelled.',
            timestamp: 'Completed',
            status: 'completed'
          }
        ]
      }
      
      return [...baseTimeline, ...(statusTimeline[status] || [])]
    },
    
    formatOrderItems(items) {
      return items.map((item, index) => ({
        id: index + 1,
        name: item.query_text || 'Part',
        description: `OEM Code: ${item.matched_part_id || 'N/A'}`,
        price: '0.00', // Price would need to be fetched separately
        quantity: item.qty || 1,
        notes: item.notes || ''
      }))
    },
    
    getStatusClass(status) {
      const classes = {
        'pending': 'bg-yellow-100 text-yellow-800',
        'processing': 'bg-yellow-100 text-yellow-800',
        'shipped': 'bg-blue-100 text-blue-800',
        'delivered': 'bg-green-100 text-green-800',
        'cancelled': 'bg-red-100 text-red-800'
      }
      return classes[status] || 'bg-gray-100 text-gray-800'
    },
    
    getTimelineDotClass(status) {
      const classes = {
        'completed': 'bg-green-500',
        'current': 'bg-blue-500',
        'pending': 'bg-gray-300'
      }
      return classes[status] || 'bg-gray-300'
    }
  }
}
</script>
