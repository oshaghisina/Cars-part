<template>
  <div class="order-detail">
    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div v-if="loading" class="text-center py-12 font-persian font-persian">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <p class="mt-2 text-gray-600 font-persian font-persian" class="font-persian text-rtl">Loading order details...</p>
      </div>
      
      <div v-else-if="order" class="space-y-6">
        <!-- Order Header -->
        <div class="bg-white rounded-lg shadow-md p-6">
          <div class="flex justify-between items-start mb-4">
            <div>
              <h1 class="text-2xl font-bold text-gray-900 font-persian font-persian" class="font-persian-bold text-rtl">Order #{{ order.number }}</h1>
              <p class="text-gray-600 font-persian font-persian" class="font-persian text-rtl">Placed on {{ order.date }}</p>
            </div>
            <span :class="getStatusClass(order.status)" class="px-4 py-2 rounded-full text-sm font-semibold font-persian font-persian">
              {{ order.status }}
            </span>
          </div>
          
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <p class="text-sm text-gray-600 font-persian font-persian" class="font-persian text-rtl">Total Amount</p>
              <p class="text-2xl font-bold text-blue-600 font-persian font-persian" class="font-persian text-rtl">${{ order.total }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-600 font-persian font-persian" class="font-persian text-rtl">Payment Method</p>
              <p class="font-semibold font-persian" class="font-persian text-rtl">{{ order.paymentMethod }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-600 font-persian font-persian" class="font-persian text-rtl">Shipping Address</p>
              <p class="font-semibold font-persian" class="font-persian text-rtl">{{ order.shippingAddress }}</p>
            </div>
          </div>
        </div>

        <!-- Order Items -->
        <div class="bg-white rounded-lg shadow-md p-6">
          <h2 class="text-lg font-semibold text-gray-900 mb-4 font-persian font-persian" class="font-persian-bold text-rtl">اقلام سفارش</h2>
          <div class="space-y-4">
            <div
              v-for="item in order.items"
              :key="item.id"
              class="flex items-center space-x-4 p-4 border border-gray-200 rounded-lg"
            >
              <div class="w-16 h-16 bg-gray-200 rounded-lg flex items-center justify-center">
                <span class="text-2xl font-persian font-persian">🔧</span>
              </div>
              <div class="flex-1">
                <h3 class="font-semibold text-gray-900 font-persian font-persian" class="font-persian-bold text-rtl">{{ item.name }}</h3>
                <p class="text-sm text-gray-600 font-persian font-persian" class="font-persian text-rtl">{{ item.description }}</p>
                <p class="text-sm text-gray-500 font-persian font-persian" class="font-persian text-rtl">SKU: {{ item.sku }}</p>
              </div>
              <div class="text-right font-persian font-persian">
                <p class="font-semibold font-persian" class="font-persian text-rtl">${{ item.price }}</p>
                <p class="text-sm text-gray-600 font-persian font-persian" class="font-persian text-rtl">Qty: {{ item.quantity }}</p>
                <p class="text-sm font-semibold text-blue-600 font-persian font-persian" class="font-persian text-rtl">${{ (item.price * item.quantity).toFixed(2) }}</p>
              </div>
            </div>
          </div>
          
          <div class="mt-6 pt-4 border-t border-gray-200">
            <div class="flex justify-between items-center text-lg font-semibold font-persian font-persian">
              <span>مجموع</span>
              <span class="text-blue-600 font-persian font-persian">${{ order.total }}</span>
            </div>
          </div>
        </div>

        <!-- Tracking Information -->
        <div v-if="order.tracking" class="bg-white rounded-lg shadow-md p-6">
          <h2 class="text-lg font-semibold text-gray-900 mb-4 font-persian font-persian" class="font-persian-bold text-rtl">Tracking Information</h2>
          <div class="space-y-3">
            <div class="flex justify-between items-center">
              <span class="font-semibold font-persian">Tracking Number</span>
              <span class="text-blue-600 font-mono font-persian font-persian">{{ order.tracking.number }}</span>
            </div>
            <div class="flex justify-between items-center">
              <span class="font-semibold font-persian">Carrier</span>
              <span>{{ order.tracking.carrier }}</span>
            </div>
            <div class="flex justify-between items-center">
              <span class="font-semibold font-persian">Estimated Delivery</span>
              <span>{{ order.tracking.estimatedDelivery }}</span>
            </div>
          </div>
        </div>

        <!-- Actions -->
        <div class="flex justify-between items-center">
          <router-link
            to="/track"
            class="btn-secondary"
          >
            Back to Tracking
          </router-link>
          <button
            @click="downloadInvoice"
            class="btn-primary"
          >
            Download Invoice
          </button>
        </div>
      </div>
      
      <div v-else class="text-center py-12 font-persian font-persian">
        <div class="text-6xl mb-4 font-persian font-persian">❌</div>
        <h3 class="text-xl font-semibold text-gray-900 mb-2 font-persian font-persian" class="font-persian-bold text-rtl">Order not found</h3>
        <p class="text-gray-600 mb-4 font-persian font-persian" class="font-persian text-rtl">The requested order could not be found.</p>
        <router-link
          to="/track"
          class="btn-primary"
        >
          Back to Tracking
        </router-link>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'OrderDetail',
  props: {
    id: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      order: null,
      loading: true
    }
  },
  async mounted() {
    await this.loadOrder()
  },
  methods: {
    async loadOrder() {
      this.loading = true
      
      try {
        // Simulate API call - replace with actual API integration
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        // Mock order data
        this.order = {
          number: this.id,
          date: '2024-01-15',
          status: 'ارسال شده',
          total: '125.50',
          paymentMethod: 'Credit Card',
          shippingAddress: '123 Main St, شهر, State 12345',
          items: [
            {
              id: 1,
              name: 'Brake Pads - Front',
              description: 'High-quality ceramic brake pads for front wheels',
              sku: 'BP-F3-2020',
              price: '45.99',
              quantity: 1
            },
            {
              id: 2,
              name: 'Oil Filter',
              description: 'Premium oil filter for optimal engine protection',
              sku: 'OF-EC7-2018',
              price: '12.50',
              quantity: 2
            }
          ],
          tracking: {
            number: 'TRK123456789',
            carrier: 'DHL Express',
            estimatedDelivery: '2024-01-20'
          }
        }
      } catch (error) {
        console.error('Error loading order:', error)
        this.order = null
      } finally {
        this.loading = false
      }
    },
    
    getStatusClass(status) {
      const classes = {
        'در حال پردازش': 'bg-yellow-100 text-yellow-800',
        'ارسال شده': 'bg-blue-100 text-blue-800',
        'تحویل داده شده': 'bg-green-100 text-green-800',
        'لغو شده': 'bg-red-100 text-red-800'
      }
      return classes[status] || 'bg-gray-100 text-gray-800'
    },
    
    downloadInvoice() {
      // Simulate invoice download
      alert('Invoice download started! (This is a demo)')
    }
  }
}
</script>
