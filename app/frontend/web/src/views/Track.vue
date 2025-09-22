<template>
  <div class="track">
    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 class="text-3xl font-bold text-gray-900 mb-8">Track Your Order</h1>
      
      <!-- Search Form -->
      <div class="bg-white rounded-lg shadow-md p-6 mb-8">
        <form @submit.prevent="trackOrder" class="space-y-4">
          <div class="flex gap-4">
            <div class="flex-1">
              <label class="block text-sm font-medium text-gray-700 mb-2">Order Number</label>
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
                class="bg-blue-600 text-white px-6 py-2 rounded-md font-semibold hover:bg-blue-700 disabled:opacity-50"
              >
                {{ loading ? 'Tracking...' : 'Track Order' }}
              </button>
            </div>
          </div>
        </form>
      </div>

      <!-- Order Details -->
      <div v-if="order" class="space-y-6">
        <!-- Order Summary -->
        <div class="bg-white rounded-lg shadow-md p-6">
          <h2 class="text-xl font-semibold text-gray-900 mb-4">Order Summary</h2>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <p class="text-sm text-gray-600">Order Number</p>
              <p class="font-semibold">{{ order.number }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-600">Order Date</p>
              <p class="font-semibold">{{ order.date }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-600">Status</p>
              <span :class="getStatusClass(order.status)" class="px-3 py-1 rounded-full text-sm font-semibold">
                {{ order.status }}
              </span>
            </div>
            <div>
              <p class="text-sm text-gray-600">Total Amount</p>
              <p class="font-semibold text-lg text-blue-600">${{ order.total }}</p>
            </div>
          </div>
        </div>

        <!-- Tracking Timeline -->
        <div class="bg-white rounded-lg shadow-md p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Tracking Timeline</h3>
          <div class="space-y-4">
            <div
              v-for="(event, index) in order.timeline"
              :key="index"
              class="flex items-start space-x-3"
            >
              <div :class="getTimelineDotClass(event.status)" class="w-3 h-3 rounded-full mt-2"></div>
              <div class="flex-1">
                <p class="font-semibold text-gray-900">{{ event.title }}</p>
                <p class="text-sm text-gray-600">{{ event.description }}</p>
                <p class="text-xs text-gray-500">{{ event.timestamp }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Order Items -->
        <div class="bg-white rounded-lg shadow-md p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Order Items</h3>
          <div class="space-y-3">
            <div
              v-for="item in order.items"
              :key="item.id"
              class="flex justify-between items-center py-2 border-b border-gray-200 last:border-b-0"
            >
              <div>
                <p class="font-semibold">{{ item.name }}</p>
                <p class="text-sm text-gray-600">{{ item.description }}</p>
              </div>
              <div class="text-right">
                <p class="font-semibold">${{ item.price }}</p>
                <p class="text-sm text-gray-600">Qty: {{ item.quantity }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- No Order Found -->
      <div v-else-if="hasSearched && !loading" class="text-center py-12">
        <div class="text-6xl mb-4">📦</div>
        <h3 class="text-xl font-semibold text-gray-900 mb-2">Order not found</h3>
        <p class="text-gray-600 mb-4">Please check your order number and try again.</p>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <p class="mt-2 text-gray-600">Tracking order...</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Track',
  data() {
    return {
      orderNumber: '',
      order: null,
      loading: false,
      hasSearched: false
    }
  },
  methods: {
    async trackOrder() {
      if (!this.orderNumber.trim()) return
      
      this.loading = true
      this.hasSearched = true
      
      try {
        // Simulate API call - replace with actual API integration
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        // Mock order data
        this.order = {
          number: this.orderNumber,
          date: '2024-01-15',
          status: 'Shipped',
          total: '125.50',
          items: [
            {
              id: 1,
              name: 'Brake Pads - Front',
              description: 'High-quality ceramic brake pads',
              price: '45.99',
              quantity: 1
            },
            {
              id: 2,
              name: 'Oil Filter',
              description: 'Premium oil filter',
              price: '12.50',
              quantity: 2
            }
          ],
          timeline: [
            {
              title: 'Order Placed',
              description: 'Your order has been received and is being processed.',
              timestamp: '2024-01-15 10:30 AM',
              status: 'completed'
            },
            {
              title: 'Payment Confirmed',
              description: 'Payment has been processed successfully.',
              timestamp: '2024-01-15 10:35 AM',
              status: 'completed'
            },
            {
              title: 'Order Processed',
              description: 'Your order is being prepared for shipment.',
              timestamp: '2024-01-15 2:15 PM',
              status: 'completed'
            },
            {
              title: 'Shipped',
              description: 'Your order has been shipped and is on its way.',
              timestamp: '2024-01-16 9:00 AM',
              status: 'current'
            },
            {
              title: 'In Transit',
              description: 'Your order is currently in transit.',
              timestamp: 'Expected delivery: 2024-01-20',
              status: 'pending'
            }
          ]
        }
      } catch (error) {
        console.error('Tracking error:', error)
        this.order = null
      } finally {
        this.loading = false
      }
    },
    
    getStatusClass(status) {
      const classes = {
        'Processing': 'bg-yellow-100 text-yellow-800',
        'Shipped': 'bg-blue-100 text-blue-800',
        'Delivered': 'bg-green-100 text-green-800',
        'Cancelled': 'bg-red-100 text-red-800'
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
