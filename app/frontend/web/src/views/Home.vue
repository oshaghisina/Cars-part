<template>
  <div class="home">
    <!-- Hero Section -->
    <section class="bg-gradient-to-r from-blue-600 to-blue-800 text-white">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
        <div class="text-center">
          <h1 class="text-4xl md:text-6xl font-bold mb-6">
            Quality Chinese Auto Parts
          </h1>
          <p class="text-xl md:text-2xl mb-8 text-blue-100">
            Find the perfect parts for your vehicle with competitive prices and fast delivery
          </p>
          <div class="flex flex-col sm:flex-row gap-4 justify-center">
            <router-link 
              to="/search" 
              class="bg-white text-blue-600 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors"
            >
              Search Parts
            </router-link>
            <button 
              @click="$emit('show-contact')"
              class="border-2 border-white text-white px-8 py-3 rounded-lg font-semibold hover:bg-white hover:text-blue-600 transition-colors"
            >
              Get Quote
            </button>
          </div>
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section class="py-16 bg-white">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-12">
          <h2 class="text-3xl font-bold text-gray-900 mb-4">Why Choose Us?</h2>
          <p class="text-lg text-gray-600">We provide the best service for Chinese auto parts</p>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div class="text-center">
            <div class="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <span class="text-2xl">🔍</span>
            </div>
            <h3 class="text-xl font-semibold mb-2">Easy Search</h3>
            <p class="text-gray-600">Find parts quickly with our advanced search and filtering system</p>
          </div>
          
          <div class="text-center">
            <div class="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <span class="text-2xl">💰</span>
            </div>
            <h3 class="text-xl font-semibold mb-2">Competitive Prices</h3>
            <p class="text-gray-600">Get the best prices with our direct supplier relationships</p>
          </div>
          
          <div class="text-center">
            <div class="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <span class="text-2xl">🚚</span>
            </div>
            <h3 class="text-xl font-semibold mb-2">Fast Delivery</h3>
            <p class="text-gray-600">Quick and reliable shipping to get your parts when you need them</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Persian Font Demo Section -->
    <section class="py-16 bg-white">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-12">
          <h2 class="text-3xl font-bold text-gray-900 mb-4 font-persian-bold">
            پشتیبانی کامل از زبان فارسی
          </h2>
          <p class="text-lg text-gray-600 font-persian text-rtl">
            این سیستم با پشتیبانی کامل از زبان فارسی طراحی شده است
          </p>
        </div>
        <div class="bg-gradient-to-r from-blue-50 to-green-50 rounded-lg p-8">
          <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div class="text-center">
              <div class="text-4xl mb-4">🔍</div>
              <h4 class="text-lg font-persian-bold text-rtl mb-2">جستجوی قطعات</h4>
              <p class="text-sm font-persian text-rtl text-gray-600">جستجوی آسان و سریع قطعات مورد نیاز</p>
            </div>
            <div class="text-center">
              <div class="text-4xl mb-4">💰</div>
              <h4 class="text-lg font-persian-bold text-rtl mb-2">قیمت‌های رقابتی</h4>
              <p class="text-sm font-persian text-rtl text-gray-600">بهترین قیمت‌ها در بازار</p>
            </div>
            <div class="text-center">
              <div class="text-4xl mb-4">🚚</div>
              <h4 class="text-lg font-persian-bold text-rtl mb-2">ارسال سریع</h4>
              <p class="text-sm font-persian text-rtl text-gray-600">ارسال سریع و مطمئن</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Popular Parts Section -->
    <section class="py-16 bg-gray-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-12">
          <h2 class="text-3xl font-bold text-gray-900 mb-4">Popular Parts</h2>
          <p class="text-lg text-gray-600">Browse our most requested parts</p>
        </div>
        
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          <div 
            v-for="part in popularParts" 
            :key="part.id"
            class="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow cursor-pointer"
            @click="$router.push(`/part/${part.id}`)"
          >
            <div class="w-full h-32 bg-gray-200 rounded-lg mb-4 flex items-center justify-center">
              <span class="text-4xl">{{ part.icon }}</span>
            </div>
            <h3 class="font-semibold text-lg mb-2">{{ part.name }}</h3>
            <p class="text-gray-600 text-sm mb-3">{{ part.description }}</p>
            <div class="flex justify-between items-center">
              <span class="text-blue-600 font-semibold">${{ part.price }}</span>
              <span class="text-sm text-gray-500">{{ part.stock }} in stock</span>
            </div>
          </div>
        </div>
        
        <div class="text-center mt-8">
          <router-link 
            to="/search" 
            class="bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
          >
            View All Parts
          </router-link>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
import apiService from '../services/api.js'

export default {
  name: 'Home',
  data() {
    return {
      popularParts: [],
      loading: true,
      error: null
    }
  },
  async mounted() {
    await this.loadPopularParts()
  },
  methods: {
    async loadPopularParts() {
      this.loading = true
      this.error = null
      
      try {
        // Get popular parts from API
        const parts = await apiService.getPopularParts(4)
        
        // Format parts for display with icons
        this.popularParts = parts.map((part, index) => {
          const icons = ['🛑', '🔧', '💨', '⚡', '🔩', '⚙️', '🛠️', '🔌']
          return {
            ...apiService.formatPartForDisplay(part),
            icon: icons[index % icons.length]
          }
        })
        
      } catch (error) {
        console.error('Failed to load popular parts:', error)
        this.error = 'Failed to load popular parts'
        
        // Fallback to mock data
        this.popularParts = [
          {
            id: 1,
            name: 'Brake Pads',
            description: 'High-quality brake pads for Chinese vehicles',
            price: '45.99',
            stock: 12,
            icon: '🛑'
          },
          {
            id: 2,
            name: 'Oil Filter',
            description: 'Premium oil filters for optimal engine performance',
            price: '12.50',
            stock: 25,
            icon: '🔧'
          },
          {
            id: 3,
            name: 'Air Filter',
            description: 'Clean air filters for better engine efficiency',
            price: '18.75',
            stock: 8,
            icon: '💨'
          },
          {
            id: 4,
            name: 'Spark Plugs',
            description: 'High-performance spark plugs for smooth ignition',
            price: '32.00',
            stock: 15,
            icon: '⚡'
          }
        ]
      } finally {
        this.loading = false
      }
    }
  }
}
</script>
