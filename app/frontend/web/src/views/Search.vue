<template>
  <div class="search">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Search Header -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900 mb-4">Search Auto Parts</h1>
        
        <!-- Search Form -->
        <div class="bg-white rounded-lg shadow-md p-6">
          <form @submit.prevent="searchParts" class="space-y-4">
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Part Name</label>
                <input
                  v-model="searchForm.partName"
                  type="text"
                  placeholder="e.g., brake pads, oil filter"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Vehicle Make</label>
                <select
                  v-model="searchForm.make"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select Make</option>
                  <option value="BYD">BYD</option>
                  <option value="Geely">Geely</option>
                  <option value="Great Wall">Great Wall</option>
                  <option value="Chery">Chery</option>
                  <option value="JAC">JAC</option>
                </select>
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Vehicle Model</label>
                <input
                  v-model="searchForm.model"
                  type="text"
                  placeholder="e.g., F3, EC7"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
            
            <div class="flex justify-between items-center">
              <button
                type="submit"
                :disabled="loading"
                class="bg-blue-600 text-white px-6 py-2 rounded-md font-semibold hover:bg-blue-700 disabled:opacity-50"
              >
                {{ loading ? 'Searching...' : 'Search Parts' }}
              </button>
              
              <button
                type="button"
                @click="clearFilters"
                class="text-gray-600 hover:text-gray-800"
              >
                Clear Filters
              </button>
            </div>
          </form>
        </div>
      </div>

      <!-- Search Results -->
      <div v-if="searchResults.length > 0" class="mb-8">
        <h2 class="text-xl font-semibold text-gray-900 mb-4">
          Found {{ searchResults.length }} parts
        </h2>
        
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div
            v-for="part in searchResults"
            :key="part.id"
            class="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow cursor-pointer"
            @click="$router.push(`/part/${part.id}`)"
          >
            <div class="w-full h-32 bg-gray-200 rounded-lg mb-4 flex items-center justify-center">
              <span class="text-4xl">🔧</span>
            </div>
            <h3 class="font-semibold text-lg mb-2">{{ part.name }}</h3>
            <p class="text-gray-600 text-sm mb-3">{{ part.description }}</p>
            <div class="flex justify-between items-center mb-3">
              <span class="text-blue-600 font-semibold text-lg">${{ part.price }}</span>
              <span class="text-sm text-gray-500">{{ part.stock }} in stock</span>
            </div>
            <div class="text-xs text-gray-500">
              <p>Make: {{ part.make }}</p>
              <p>Model: {{ part.model }}</p>
              <p>Year: {{ part.year }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- No Results -->
      <div v-else-if="hasSearched && !loading" class="text-center py-12">
        <div class="text-6xl mb-4">🔍</div>
        <h3 class="text-xl font-semibold text-gray-900 mb-2">No parts found</h3>
        <p class="text-gray-600 mb-4">Try adjusting your search criteria</p>
        <button
          @click="clearFilters"
          class="bg-blue-600 text-white px-6 py-2 rounded-md font-semibold hover:bg-blue-700"
        >
          Clear Filters
        </button>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <p class="mt-2 text-gray-600">Searching for parts...</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Search',
  data() {
    return {
      searchForm: {
        partName: '',
        make: '',
        model: ''
      },
      searchResults: [],
      loading: false,
      hasSearched: false
    }
  },
  methods: {
    async searchParts() {
      this.loading = true
      this.hasSearched = true
      
      try {
        // Simulate API call - replace with actual API integration
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        // Mock search results
        this.searchResults = [
          {
            id: 1,
            name: 'Brake Pads - Front',
            description: 'High-quality ceramic brake pads for front wheels',
            price: '45.99',
            stock: 12,
            make: this.searchForm.make || 'BYD',
            model: this.searchForm.model || 'F3',
            year: '2020-2023'
          },
          {
            id: 2,
            name: 'Oil Filter',
            description: 'Premium oil filter for optimal engine protection',
            price: '12.50',
            stock: 25,
            make: this.searchForm.make || 'Geely',
            model: this.searchForm.model || 'EC7',
            year: '2018-2023'
          }
        ]
      } catch (error) {
        console.error('Search error:', error)
        this.searchResults = []
      } finally {
        this.loading = false
      }
    },
    
    clearFilters() {
      this.searchForm = {
        partName: '',
        make: '',
        model: ''
      }
      this.searchResults = []
      this.hasSearched = false
    }
  }
}
</script>
