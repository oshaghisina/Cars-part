<template>
  <div class="search">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Search Header -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900 mb-4 font-persian-bold text-rtl font-persian font-persian-bold text-rtl">جستجوی قطعات خودرو</h1>
        
        <!-- Search Form -->
        <div class="bg-white rounded-lg shadow-md p-6">
          <form @submit.prevent="searchParts" class="space-y-4">
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2 font-persian text-rtl font-persian">نام قطعه</label>
                <input
                  v-model="searchForm.partName"
                  type="text"
                  placeholder="مثال: لنت ترمز، فیلتر روغن"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 font-persian text-rtl font-persian"
                />
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2 font-persian text-rtl font-persian">برند خودرو</label>
                <select
                  v-model="searchForm.make"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 font-persian text-rtl font-persian"
                >
                  <option value="">انتخاب برند</option>
                  <option value="BYD">BYD</option>
                  <option value="Geely">Geely</option>
                  <option value="Great Wall">Great Wall</option>
                  <option value="Chery">Chery</option>
                  <option value="JAC">JAC</option>
                </select>
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2 font-persian text-rtl font-persian">مدل خودرو</label>
                <input
                  v-model="searchForm.model"
                  type="text"
                  placeholder="مثال: F3، EC7"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 font-persian text-rtl font-persian"
                />
              </div>
            </div>
            
            <div class="flex justify-between items-center">
              <button
                type="submit"
                :disabled="loading"
                class="bg-blue-600 text-white px-6 py-2 rounded-md font-semibold hover:bg-blue-700 disabled:opacity-50 font-persian font-persian"
              >
                {{ loading ? 'در حال جستجو...' : 'جستجوی قطعات' }}
              </button>
              
              <button
                type="button"
                @click="clearFilters"
                class="text-gray-600 hover:text-gray-800 font-persian font-persian"
              >
                پاک کردن فیلترها
              </button>
            </div>
          </form>
        </div>
      </div>

      <!-- Search Results -->
      <div v-if="searchResults.length > 0" class="mb-8">
        <h2 class="text-xl font-semibold text-gray-900 mb-4 font-persian font-persian-bold text-rtl">
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
              <span class="text-4xl font-persian">🔧</span>
            </div>
            <h3 class="font-semibold text-lg mb-2 font-persian font-persian-bold text-rtl">{{ part.name }}</h3>
            <p class="text-gray-600 text-sm mb-3 font-persian font-persian text-rtl">{{ part.description }}</p>
            <div class="flex justify-between items-center mb-3">
              <span class="text-blue-600 font-semibold text-lg font-persian">${{ part.price }}</span>
              <span class="text-sm text-gray-500 font-persian">{{ part.stock }} in stock</span>
            </div>
            <div class="text-xs text-gray-500 font-persian">
              <p class="font-persian text-rtl">Make: {{ part.make }}</p>
              <p class="font-persian text-rtl">Model: {{ part.model }}</p>
              <p class="font-persian text-rtl">Year: {{ part.year }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="text-center py-12 font-persian">
        <div class="text-6xl mb-4 font-persian">❌</div>
        <h3 class="text-xl font-semibold text-gray-900 mb-2 font-persian font-persian-bold text-rtl">Search Error</h3>
        <p class="text-gray-600 mb-4 font-persian font-persian text-rtl">{{ error }}</p>
        <button
          @click="searchParts"
          class="bg-blue-600 text-white px-6 py-2 rounded-md font-semibold hover:bg-blue-700 font-persian"
        >
          Try Again
        </button>
      </div>

      <!-- No Results -->
      <div v-else-if="hasSearched && !loading" class="text-center py-12 font-persian">
        <div class="text-6xl mb-4 font-persian">🔍</div>
        <h3 class="text-xl font-semibold text-gray-900 mb-2 font-persian font-persian-bold text-rtl">No parts found</h3>
        <p class="text-gray-600 mb-4 font-persian font-persian text-rtl">Try adjusting your search criteria</p>
        <button
          @click="clearFilters"
          class="bg-blue-600 text-white px-6 py-2 rounded-md font-semibold hover:bg-blue-700 font-persian"
        >
          Clear Filters
        </button>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="text-center py-12 font-persian">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <p class="mt-2 text-gray-600 font-persian font-persian text-rtl">Searching for parts...</p>
      </div>
    </div>
  </div>
</template>

<script>
import apiService from '../services/api.js'

export default {
  name: 'جستجو',
  data() {
    return {
      searchForm: {
        partName: '',
        make: '',
        model: ''
      },
      searchResults: [],
      loading: false,
      hasSearched: false,
      error: null
    }
  },
  methods: {
    async searchParts() {
      this.loading = true
      this.hasSearched = true
      this.error = null
      
      try {
        // Build search parameters
        const searchParams = {
          limit: 20
        }
        
        // Add search query
        if (this.searchForm.partName) {
          searchParams.search = this.searchForm.partName
        }
        
        // Add vehicle filters
        if (this.searchForm.make) {
          searchParams.vehicle_make = this.searchForm.make
        }
        
        if (this.searchForm.model) {
          // For model search, we'll use the general search parameter
          if (searchParams.search) {
            searchParams.search += ` ${this.searchForm.model}`
          } else {
            searchParams.search = this.searchForm.model
          }
        }
        
        // Call real API
        const response = await apiService.searchParts(searchParams)
        
        // Format results for display
        this.searchResults = response.map(part => apiService.formatPartForDisplay(part))
        
      } catch (error) {
        console.error('Search error:', error)
        this.error = error.message || 'Search failed. Please try again.'
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
      this.error = null
    }
  }
}
</script>
