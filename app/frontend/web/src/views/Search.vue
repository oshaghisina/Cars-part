<template>
  <div class="product-list-page">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Enhanced Breadcrumbs -->
      <nav class="flex mb-6" aria-label="Breadcrumb">
        <ol class="inline-flex items-center space-x-1 md:space-x-3">
          <li class="inline-flex items-center">
            <router-link to="/" class="inline-flex items-center text-sm font-medium text-gray-700 hover:text-blue-600 transition-colors">
              <svg class="w-3 h-3 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path d="m19.707 9.293-2-2-7-7a1 1 0 0 0-1.414 0l-7 7-2 2a1 1 0 0 0 1.414 1.414L2 10.414V18a2 2 0 0 0 2 2h3a1 1 0 0 0 1-1v-4a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1v4a1 1 0 0 0 1 1h3a2 2 0 0 0 2-2v-7.586l.293.293a1 1 0 0 0 1.414-1.414Z"/>
              </svg>
              <span class="font-persian">خانه</span>
            </router-link>
          </li>
          <li>
            <div class="flex items-center">
              <svg class="w-3 h-3 text-gray-400 mx-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
              </svg>
              <span class="ml-1 text-sm font-medium text-gray-500 font-persian">
                {{ categoryName ? categoryName : 'محصولات' }}
              </span>
            </div>
          </li>
          <!-- Show search query if present -->
          <li v-if="searchQuery && !categoryName">
            <div class="flex items-center">
              <svg class="w-3 h-3 text-gray-400 mx-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
              </svg>
              <span class="ml-1 text-sm font-medium text-gray-500 font-persian">
                نتایج جستجو برای: "{{ searchQuery }}"
              </span>
            </div>
          </li>
        </ol>
      </nav>

      <!-- Page Header -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900 mb-4 font-persian-bold text-rtl">
          {{ categoryName ? `قطعات ${categoryName}` : 'جستجوی قطعات خودرو' }}
        </h1>
        <p v-if="categoryName" class="text-lg text-gray-600 font-persian text-rtl mb-4">
          مشاهده تمام محصولات در دسته‌بندی {{ categoryName }}
        </p>
        
        <!-- Search and Filters -->
        <div class="bg-white rounded-lg shadow-md p-6">
          <!-- Search Bar -->
          <div class="mb-6">
            <div class="relative">
              <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
                </svg>
              </div>
              <input
                v-model="searchQuery"
                type="text"
                placeholder="جستجوی قطعات، برند، مدل..."
                class="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500 font-persian text-rtl"
                @input="debouncedSearch"
              />
            </div>
          </div>

          <!-- Filters -->
          <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <!-- Category Filter -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2 font-persian text-rtl">دسته‌بندی</label>
              <select
                v-model="filters.category"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 font-persian text-rtl"
                @change="applyFilters"
              >
                <option value="">همه دسته‌ها</option>
                <option v-for="category in categories" :key="category.id" :value="category.name">
                  {{ category.name_fa || category.name }}
                </option>
              </select>
            </div>
            
            <!-- Vehicle Make Filter -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2 font-persian text-rtl">برند خودرو</label>
              <select
                v-model="filters.vehicleMake"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 font-persian text-rtl"
                @change="applyFilters"
              >
                <option value="">همه برندها</option>
                <option v-for="make in vehicleMakes" :key="make" :value="make">{{ make }}</option>
              </select>
            </div>
            
            <!-- Vehicle Model Filter -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2 font-persian text-rtl">مدل خودرو</label>
              <input
                v-model="filters.vehicleModel"
                type="text"
                placeholder="مثال: Tiggo 8, F3"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 font-persian text-rtl"
                @input="debouncedSearch"
              />
            </div>

            <!-- Sort Filter -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2 font-persian text-rtl">مرتب‌سازی</label>
              <select
                v-model="sortBy"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 font-persian text-rtl"
                @change="applyFilters"
              >
                <option value="name">نام قطعه</option>
                <option value="make">برند خودرو</option>
                <option value="model">مدل خودرو</option>
                <option value="category">دسته‌بندی</option>
              </select>
            </div>
          </div>
          
          <!-- Filter Actions -->
          <div class="flex justify-between items-center">
            <div class="flex items-center space-x-4 space-x-reverse">
              <button
                @click="toggleAdvancedFilters"
                class="text-blue-600 hover:text-blue-800 font-persian text-sm"
              >
                {{ showAdvancedFilters ? 'مخفی کردن فیلترهای پیشرفته' : 'فیلترهای پیشرفته' }}
              </button>
              
              <span v-if="totalResults > 0" class="text-sm text-gray-600 font-persian">
                {{ totalResults }} نتیجه پیدا شد
              </span>
            </div>
            
            <button
              @click="clearAllFilters"
              class="text-gray-600 hover:text-gray-800 font-persian text-sm"
            >
              پاک کردن همه فیلترها
            </button>
          </div>

          <!-- Advanced Filters -->
          <div v-if="showAdvancedFilters" class="mt-6 pt-6 border-t border-gray-200">
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2 font-persian text-rtl">کد OEM</label>
                <input
                  v-model="filters.oemCode"
                  type="text"
                  placeholder="کد OEM"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 font-persian text-rtl"
                  @input="debouncedSearch"
                />
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2 font-persian text-rtl">وضعیت</label>
                <select
                  v-model="filters.status"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 font-persian text-rtl"
                  @change="applyFilters"
                >
                  <option value="">همه وضعیت‌ها</option>
                  <option value="active">فعال</option>
                  <option value="inactive">غیرفعال</option>
                </select>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2 font-persian text-rtl">تعداد نمایش</label>
                <select
                  v-model="itemsPerPage"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 font-persian text-rtl"
                  @change="applyFilters"
                >
                  <option value="12">12 محصول</option>
                  <option value="24">24 محصول</option>
                  <option value="48">48 محصول</option>
                </select>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Product Grid -->
      <div v-if="products.length > 0" class="mb-8">
        <!-- Results Header -->
        <div class="flex justify-between items-center mb-6">
          <div>
            <h2 class="text-xl font-semibold text-gray-900 font-persian-bold text-rtl">
              نتایج جستجو
            </h2>
            <p class="text-gray-600 font-persian text-rtl">
              {{ totalResults }} محصول از {{ totalResults }} نتیجه
            </p>
          </div>
          
          <!-- View Toggle -->
          <div class="flex items-center space-x-2 space-x-reverse">
            <button
              @click="viewMode = 'grid'"
              :class="[
                'p-2 rounded-md',
                viewMode === 'grid' ? 'bg-blue-100 text-blue-600' : 'text-gray-400 hover:text-gray-600'
              ]"
            >
              <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path d="M5 3a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2V5a2 2 0 00-2-2H5zM5 11a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2v-2a2 2 0 00-2-2H5zM11 5a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V5zM11 13a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"/>
              </svg>
            </button>
            <button
              @click="viewMode = 'list'"
              :class="[
                'p-2 rounded-md',
                viewMode === 'list' ? 'bg-blue-100 text-blue-600' : 'text-gray-400 hover:text-gray-600'
              ]"
            >
              <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clip-rule="evenodd"/>
              </svg>
            </button>
          </div>
        </div>
        
        <!-- Products Grid/List -->
        <div 
          :class="[
            'grid gap-6',
            viewMode === 'grid' 
              ? 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4' 
              : 'grid-cols-1'
          ]"
        >
          <div
            v-for="product in products"
            :key="product.id"
            :class="[
              'bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow cursor-pointer overflow-hidden',
              viewMode === 'list' ? 'flex' : ''
            ]"
            @click="$router.push(`/part/${product.id}`)"
          >
            <!-- Product Image -->
            <div 
              :class="[
                'bg-gray-200 flex items-center justify-center',
                viewMode === 'grid' ? 'w-full h-48' : 'w-32 h-32 flex-shrink-0'
              ]"
            >
              <span class="text-4xl">🔧</span>
            </div>
            
            <!-- Product Info -->
            <div :class="['p-4', viewMode === 'list' ? 'flex-1' : '']">
              <div class="flex justify-between items-start mb-2">
                <h3 class="font-semibold text-lg font-persian-bold text-rtl">{{ product.part_name }}</h3>
                <span 
                  :class="[
                    'px-2 py-1 text-xs rounded-full',
                    product.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                  ]"
                >
                  {{ product.status === 'active' ? 'فعال' : 'غیرفعال' }}
                </span>
              </div>
              
              <p class="text-gray-600 text-sm mb-3 font-persian text-rtl">
                {{ product.brand_oem }} - {{ product.oem_code }}
              </p>
              
              <!-- Vehicle Info -->
              <div class="text-sm text-gray-500 mb-3 font-persian">
                <p class="font-persian text-rtl">
                  <span class="font-semibold">خودرو:</span> {{ product.vehicle_make }} {{ product.vehicle_model }}
                  <span v-if="product.vehicle_trim">- {{ product.vehicle_trim }}</span>
                </p>
                <p class="font-persian text-rtl">
                  <span class="font-semibold">دسته:</span> {{ product.category }}
                </p>
                <p class="font-persian text-rtl" v-if="product.subcategory">
                  <span class="font-semibold">زیردسته:</span> {{ product.subcategory }}
                </p>
              </div>
              
              <!-- Price and Stock (Real Data) -->
              <div class="flex justify-between items-center">
                <div>
                  <span v-if="product.price" class="text-blue-600 font-semibold text-lg font-persian">
                    {{ formatPrice(product.price.effective_price) }} {{ getCurrencySymbol(product.price.currency) }}
                  </span>
                  <span v-else class="text-gray-500 font-medium text-lg font-persian">
                    قیمت در دسترس نیست
                  </span>
                  <span v-if="product.stock" class="text-sm text-gray-500 font-persian block">
                    موجودی: {{ product.stock.in_stock ? (product.stock.current_stock - product.stock.reserved_quantity) : 0 }} عدد
                  </span>
                  <span v-else class="text-sm text-gray-500 font-persian block">
                    موجودی: نامشخص
                  </span>
                </div>
                <button class="bg-blue-600 text-white px-4 py-2 rounded-md text-sm hover:bg-blue-700 font-persian">
                  مشاهده جزئیات
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Pagination -->
        <div v-if="totalPages > 1" class="mt-8 flex justify-center">
          <nav class="flex items-center space-x-2 space-x-reverse">
            <button
              @click="goToPage(currentPage - 1)"
              :disabled="currentPage === 1"
              class="px-3 py-2 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              قبلی
            </button>
            
            <template v-for="page in visiblePages" :key="page">
              <button
                v-if="page !== '...'"
                @click="goToPage(page)"
                :class="[
                  'px-3 py-2 text-sm font-medium rounded-md',
                  page === currentPage
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-700 bg-white border border-gray-300 hover:bg-gray-50'
                ]"
              >
                {{ page }}
              </button>
              <span v-else class="px-3 py-2 text-sm text-gray-500">...</span>
            </template>
            
            <button
              @click="goToPage(currentPage + 1)"
              :disabled="currentPage === totalPages"
              class="px-3 py-2 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              بعدی
            </button>
          </nav>
        </div>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="text-center py-12 font-persian">
        <div class="text-6xl mb-4 font-persian">❌</div>
        <h3 class="text-xl font-semibold text-gray-900 mb-2 font-persian-bold text-rtl">Search Error</h3>
        <p class="text-gray-600 mb-4 font-persian text-rtl">{{ error }}</p>
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
        <h3 class="text-xl font-semibold text-gray-900 mb-2 font-persian-bold text-rtl">No parts found</h3>
        <p class="text-gray-600 mb-4 font-persian text-rtl">Try adjusting your search criteria</p>
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
        <p class="mt-2 text-gray-600 font-persian text-rtl">Searching for parts...</p>
      </div>
    </div>
  </div>
</template>

<script>
import apiService from '../services/api.js'

export default {
  name: 'ProductListPage',
  data() {
    return {
      // Search and filters
      searchQuery: '',
      filters: {
        category: '',
        vehicleMake: '',
        vehicleModel: '',
        oemCode: '',
        status: ''
      },
      sortBy: 'name',
      itemsPerPage: 12,
      showAdvancedFilters: false,
      
      // Data
      products: [],
      categories: [],
      vehicleMakes: [],
      
      // Pagination
      currentPage: 1,
      totalResults: 0,
      totalPages: 0,
      
      // UI state
      loading: false,
      error: null,
      viewMode: 'grid', // 'grid' or 'list'
      
      // Category info from URL
      categoryName: null,
      categorySlug: null,
      
      // Debounce timer
      searchTimeout: null
    }
  },
  computed: {
    visiblePages() {
      const delta = 2
      const range = []
      const rangeWithDots = []
      
      for (let i = Math.max(2, this.currentPage - delta); i <= Math.min(this.totalPages - 1, this.currentPage + delta); i++) {
        range.push(i)
      }
      
      if (this.currentPage - delta > 2) {
        rangeWithDots.push(1, '...')
      } else {
        rangeWithDots.push(1)
      }
      
      rangeWithDots.push(...range)
      
      if (this.currentPage + delta < this.totalPages - 1) {
        rangeWithDots.push('...', this.totalPages)
      } else if (this.totalPages > 1) {
        rangeWithDots.push(this.totalPages)
      }
      
      return rangeWithDots
    }
  },
  async mounted() {
    await this.initializeData()
    this.checkCategoryFilter()
    this.searchProducts()
  },
  watch: {
    '$route.query'() {
      this.checkCategoryFilter()
    }
  },
  methods: {
    async initializeData() {
      try {
        // Load categories
        await this.loadCategories()
        
        // Load vehicle makes
        await this.loadVehicleMakes()
      } catch (error) {
        console.error('Error initializing data:', error)
      }
    },
    
    async loadCategories() {
      try {
        const response = await fetch('/api/v1/categories/')
        if (response.ok) {
          this.categories = await response.json()
        }
      } catch (error) {
        console.error('Error loading categories:', error)
        // Fallback to mock categories
        this.categories = [
          { id: 1, name: 'Engine', name_fa: 'موتور' },
          { id: 2, name: 'Transmission', name_fa: 'گیربکس' },
          { id: 3, name: 'Suspension', name_fa: 'تعلیق' },
          { id: 4, name: 'Brakes', name_fa: 'ترمز' },
          { id: 5, name: 'Electrical', name_fa: 'برق' },
          { id: 6, name: 'Body Parts', name_fa: 'بدنه' },
          { id: 7, name: 'Interior', name_fa: 'داخلی' },
          { id: 8, name: 'Filters', name_fa: 'فیلتر' }
        ]
      }
    },
    
    async loadVehicleMakes() {
      try {
        // Extract unique vehicle makes from parts data
        const response = await fetch('/api/v1/parts/?limit=100')
        if (response.ok) {
          const parts = await response.json()
          const makes = [...new Set(parts.map(part => part.vehicle_make).filter(Boolean))]
          this.vehicleMakes = makes.sort()
        }
      } catch (error) {
        console.error('Error loading vehicle makes:', error)
        // Fallback to common makes
        this.vehicleMakes = ['BYD', 'Chery', 'Geely', 'Great Wall', 'JAC', 'Brilliance']
      }
    },
    
    checkCategoryFilter() {
      const category = this.$route.query.category
      const categoryName = this.$route.query.categoryName
      
      if (category && categoryName) {
        this.categorySlug = category
        this.categoryName = categoryName
        this.filters.category = categoryName
      } else {
        this.categorySlug = null
        this.categoryName = null
      }
    },
    
    debouncedSearch() {
      clearTimeout(this.searchTimeout)
      this.searchTimeout = setTimeout(() => {
        this.searchProducts()
      }, 500)
    },
    
    async searchProducts() {
      this.loading = true
      this.error = null
      
      try {
        // Build search parameters
        const searchParams = {
          limit: this.itemsPerPage,
          skip: (this.currentPage - 1) * this.itemsPerPage
        }
        
        // Add search query
        if (this.searchQuery) {
          searchParams.search = this.searchQuery
        }
        
        // Add filters
        if (this.filters.category) {
          searchParams.category = this.filters.category
        }
        
        if (this.filters.vehicleMake) {
          searchParams.vehicle_make = this.filters.vehicleMake
        }
        
        if (this.filters.vehicleModel) {
          if (searchParams.search) {
            searchParams.search += ` ${this.filters.vehicleModel}`
          } else {
            searchParams.search = this.filters.vehicleModel
          }
        }
        
        if (this.filters.oemCode) {
          if (searchParams.search) {
            searchParams.search += ` ${this.filters.oemCode}`
          } else {
            searchParams.search = this.filters.oemCode
          }
        }
        
        if (this.filters.status) {
          searchParams.status = this.filters.status
        }
        
        // Call API
        const response = await apiService.searchParts(searchParams)
        
        // For now, we'll use the response directly since it's already formatted
        this.products = response
        this.totalResults = response.length // This should come from API pagination info
        this.totalPages = Math.ceil(this.totalResults / this.itemsPerPage)
        
      } catch (error) {
        console.error('Search error:', error)
        this.error = error.message || 'جستجو با خطا مواجه شد. لطفاً دوباره تلاش کنید.'
        this.products = []
        this.totalResults = 0
        this.totalPages = 0
      } finally {
        this.loading = false
      }
    },
    
    applyFilters() {
      this.currentPage = 1 // Reset to first page when filters change
      this.searchProducts()
    },
    
    toggleAdvancedFilters() {
      this.showAdvancedFilters = !this.showAdvancedFilters
    },
    
    clearAllFilters() {
      this.searchQuery = ''
      this.filters = {
        category: '',
        vehicleMake: '',
        vehicleModel: '',
        oemCode: '',
        status: ''
      }
      this.sortBy = 'name'
      this.currentPage = 1
      this.searchProducts()
    },
    
    goToPage(page) {
      if (page >= 1 && page <= this.totalPages && page !== this.currentPage) {
        this.currentPage = page
        this.searchProducts()
      }
    },
    
    // Format price for display
    formatPrice(priceString) {
      if (!priceString) return '0'
      const price = parseFloat(priceString)
      return price.toLocaleString('fa-IR')
    },
    
    // Get currency symbol
    getCurrencySymbol(currency) {
      const symbols = {
        'IRR': 'تومان',
        'USD': '$',
        'EUR': '€'
      }
      return symbols[currency] || currency
    }
  }
}
</script>
