<template>
  <div class="part-detail">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div v-if="loading" class="text-center py-12 font-persian">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <p class="mt-2 text-gray-600 font-persian font-persian text-rtl">Loading part details...</p>
      </div>
      
      <div v-else-if="part" class="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <!-- Part Image -->
        <div class="bg-white rounded-lg shadow-md p-6">
          <div class="w-full h-64 bg-gray-200 rounded-lg mb-4 flex items-center justify-center">
            <span class="text-6xl font-persian">🔧</span>
          </div>
          <h1 class="text-2xl font-bold text-gray-900 mb-2 font-persian font-persian-bold text-rtl">{{ part.name }}</h1>
          <p class="text-gray-600 mb-4 font-persian font-persian text-rtl">{{ part.description }}</p>
        </div>
        
        <!-- Part Details & Actions -->
        <div class="bg-white rounded-lg shadow-md p-6">
          <div class="mb-6">
            <div class="flex justify-between items-center mb-4">
              <span class="text-3xl font-bold text-blue-600 font-persian">${{ part.price }}</span>
              <span class="text-sm text-gray-500 font-persian">{{ part.stock }} in stock</span>
            </div>
            
            <div class="space-y-2 text-sm text-gray-600 font-persian">
              <p class="font-persian text-rtl"><strong>Make:</strong> {{ part.make }}</p>
              <p class="font-persian text-rtl"><strong>Model:</strong> {{ part.model }}</p>
              <p class="font-persian text-rtl"><strong>Year:</strong> {{ part.year }}</p>
              <p class="font-persian text-rtl"><strong>OEM Code:</strong> {{ part.oemCode }}</p>
              <p class="font-persian text-rtl"><strong>Category:</strong> {{ part.category }}</p>
            </div>
          </div>
          
          <div class="space-y-4">
            <button
              @click="requestQuote"
              class="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors font-persian"
            >
              Request Quote
            </button>
            
            <button
              @click="addToCart"
              class="w-full border-2 border-blue-600 text-blue-600 py-3 rounded-lg font-semibold hover:bg-blue-50 transition-colors font-persian"
            >
              Add to Cart
            </button>
          </div>
          
          <div class="mt-6 pt-6 border-t border-gray-200">
            <h3 class="font-semibold text-gray-900 mb-2 font-persian font-persian-bold text-rtl">Specifications</h3>
            <div class="space-y-1 text-sm text-gray-600 font-persian">
              <p class="font-persian text-rtl"><strong>Material:</strong> {{ part.material || 'High-quality steel' }}</p>
              <p class="font-persian text-rtl"><strong>Warranty:</strong> {{ part.warranty || '12 months' }}</p>
              <p class="font-persian text-rtl"><strong>Origin:</strong> {{ part.origin || 'China' }}</p>
            </div>
          </div>
        </div>
      </div>
      
      <div v-else class="text-center py-12 font-persian">
        <div class="text-6xl mb-4 font-persian">❌</div>
        <h3 class="text-xl font-semibold text-gray-900 mb-2 font-persian font-persian-bold text-rtl">Part not found</h3>
        <p class="text-gray-600 mb-4 font-persian font-persian text-rtl">The requested part could not be found.</p>
        <router-link
          to="/search"
          class="bg-blue-600 text-white px-6 py-2 rounded-lg font-semibold hover:bg-blue-700 font-persian"
        >
          Back to Search
        </router-link>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PartDetail',
  props: {
    id: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      part: null,
      loading: true
    }
  },
  async mounted() {
    await this.loadPart()
  },
  methods: {
    async loadPart() {
      this.loading = true
      
      try {
        // Simulate API call - replace with actual API integration
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        // Mock part data
        this.part = {
          id: this.id,
          name: 'Brake Pads - Front',
          description: 'High-quality ceramic brake pads for front wheels. Provides excellent stopping power and durability.',
          price: '45.99',
          stock: 12,
          make: 'BYD',
          model: 'F3',
          year: '2020-2023',
          oemCode: 'BP-F3-2020',
          category: 'Brake System',
          material: 'Ceramic',
          warranty: '12 months',
          origin: 'China'
        }
      } catch (error) {
        console.error('Error loading part:', error)
        this.part = null
      } finally {
        this.loading = false
      }
    },
    
    requestQuote() {
      // Emit event to show contact form
      this.$emit('show-contact')
    },
    
    addToCart() {
      // Simulate adding to cart
      alert('Part added to cart! (This is a demo)')
    }
  }
}
</script>
