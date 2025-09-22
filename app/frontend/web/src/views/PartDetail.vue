<template>
  <div class="part-detail">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div v-if="loading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <p class="mt-2 text-gray-600">Loading part details...</p>
      </div>
      
      <div v-else-if="part" class="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <!-- Part Image -->
        <div class="bg-white rounded-lg shadow-md p-6">
          <div class="w-full h-64 bg-gray-200 rounded-lg mb-4 flex items-center justify-center">
            <span class="text-6xl">🔧</span>
          </div>
          <h1 class="text-2xl font-bold text-gray-900 mb-2">{{ part.name }}</h1>
          <p class="text-gray-600 mb-4">{{ part.description }}</p>
        </div>
        
        <!-- Part Details & Actions -->
        <div class="bg-white rounded-lg shadow-md p-6">
          <div class="mb-6">
            <div class="flex justify-between items-center mb-4">
              <span class="text-3xl font-bold text-blue-600">${{ part.price }}</span>
              <span class="text-sm text-gray-500">{{ part.stock }} in stock</span>
            </div>
            
            <div class="space-y-2 text-sm text-gray-600">
              <p><strong>Make:</strong> {{ part.make }}</p>
              <p><strong>Model:</strong> {{ part.model }}</p>
              <p><strong>Year:</strong> {{ part.year }}</p>
              <p><strong>OEM Code:</strong> {{ part.oemCode }}</p>
              <p><strong>Category:</strong> {{ part.category }}</p>
            </div>
          </div>
          
          <div class="space-y-4">
            <button
              @click="requestQuote"
              class="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
            >
              Request Quote
            </button>
            
            <button
              @click="addToCart"
              class="w-full border-2 border-blue-600 text-blue-600 py-3 rounded-lg font-semibold hover:bg-blue-50 transition-colors"
            >
              Add to Cart
            </button>
          </div>
          
          <div class="mt-6 pt-6 border-t border-gray-200">
            <h3 class="font-semibold text-gray-900 mb-2">Specifications</h3>
            <div class="space-y-1 text-sm text-gray-600">
              <p><strong>Material:</strong> {{ part.material || 'High-quality steel' }}</p>
              <p><strong>Warranty:</strong> {{ part.warranty || '12 months' }}</p>
              <p><strong>Origin:</strong> {{ part.origin || 'China' }}</p>
            </div>
          </div>
        </div>
      </div>
      
      <div v-else class="text-center py-12">
        <div class="text-6xl mb-4">❌</div>
        <h3 class="text-xl font-semibold text-gray-900 mb-2">Part not found</h3>
        <p class="text-gray-600 mb-4">The requested part could not be found.</p>
        <router-link
          to="/search"
          class="bg-blue-600 text-white px-6 py-2 rounded-lg font-semibold hover:bg-blue-700"
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
