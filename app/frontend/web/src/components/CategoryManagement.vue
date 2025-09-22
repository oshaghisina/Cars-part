<template>
  <div class="category-management">
    <!-- Header Section -->
    <div class="text-center mb-12">
      <h2 class="text-4xl font-bold text-gray-900 mb-4 font-persian-bold text-rtl">
        دسته‌بندی قطعات خودرو
      </h2>
      <p class="text-lg text-gray-600 font-persian text-rtl max-w-3xl mx-auto">
        قطعات خودرو را بر اساس دسته‌بندی مورد نظر خود جستجو کنید
      </p>
    </div>

    <!-- Categories Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8">
      <div 
        v-for="category in categories" 
        :key="category.id"
        class="group relative bg-white rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-2 overflow-hidden cursor-pointer"
        @click="navigateToCategory(category)"
      >
        <!-- Image Container -->
        <div class="relative h-48 bg-gradient-to-br from-blue-50 to-gray-100 overflow-hidden">
          <img 
            :src="category.image" 
            :alt="category.name"
            class="w-full h-full object-contain p-4 group-hover:scale-110 transition-transform duration-300"
            loading="lazy"
          />
          <!-- Overlay -->
          <div class="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
          
          <!-- Category Icon -->
          <div class="absolute top-4 right-4 w-12 h-12 bg-white/90 rounded-full flex items-center justify-center shadow-lg">
            <span class="text-2xl">{{ category.icon }}</span>
          </div>
        </div>

        <!-- Content -->
        <div class="p-6">
          <h3 class="text-xl font-semibold text-gray-900 mb-2 font-persian-bold text-rtl">
            {{ category.name }}
          </h3>
          <p class="text-gray-600 text-sm mb-4 font-persian text-rtl">
            {{ category.description }}
          </p>
          
          <!-- Product Count -->
          <div class="flex justify-between items-center mb-4">
            <span class="text-sm text-gray-500 font-persian text-rtl">
              {{ formatPersianNumber(category.productCount, 'محصول') }}
            </span>
            <span class="text-blue-600 text-sm font-semibold font-persian">
              مشاهده همه →
            </span>
          </div>

          <!-- Popular Items Preview -->
          <div class="text-xs text-gray-500 font-persian text-rtl">
            <p class="mb-1">محصولات محبوب:</p>
            <p class="text-gray-400">{{ category.popularItems }}</p>
          </div>
        </div>

        <!-- Hover Arrow -->
        <div class="absolute bottom-4 left-4 w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-300">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
          </svg>
        </div>
      </div>
    </div>

    <!-- View All Categories Button -->
    <div class="text-center mt-12">
      <router-link 
        to="/categories" 
        class="inline-flex items-center bg-gradient-to-r from-blue-600 to-blue-700 text-white px-8 py-4 rounded-xl font-semibold hover:from-blue-700 hover:to-blue-800 transition-all duration-300 transform hover:scale-105 font-persian"
      >
        <span>مشاهده تمام دسته‌بندی‌ها</span>
        <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
        </svg>
      </router-link>
    </div>
  </div>
</template>

<script>
// Import images for proper Vite bundling
import img10101 from '@/assets/images/parts/10101.png'
import img10102 from '@/assets/images/parts/10102.png'
import img10104 from '@/assets/images/parts/10104.png'
import img10105 from '@/assets/images/parts/10105.png'
import img10106 from '@/assets/images/parts/10106.png'
import img10110 from '@/assets/images/parts/10110.png'
import img10111 from '@/assets/images/parts/10111.png'
import img10113 from '@/assets/images/parts/10113.png'

// Import Persian number utilities
import { formatPersianNumber } from '@/utils/persianNumbers'

export default {
  name: 'CategoryManagement',
  data() {
    return {
      categories: [
        {
          id: 1,
          name: 'موتور و قطعات موتور',
          description: 'قطعات اصلی موتور و سیستم احتراق',
          image: img10101,
          icon: '🔧',
          productCount: 45,
          popularItems: 'لنت ترمز، فیلتر روغن، شمع احتراق',
          slug: 'engine-parts'
        },
        {
          id: 2,
          name: 'سیستم ترمز',
          description: 'لنت ترمز، دیسک ترمز و سیستم ترمز',
          image: img10102,
          icon: '🛑',
          productCount: 28,
          popularItems: 'لنت ترمز جلو، دیسک ترمز، کالیپر',
          slug: 'brake-system'
        },
        {
          id: 3,
          name: 'سیستم خنک‌کننده',
          description: 'رادیاتور، پمپ آب و ترموستات',
          image: img10104,
          icon: '🌡️',
          productCount: 32,
          popularItems: 'رادیاتور، پمپ آب، ترموستات',
          slug: 'cooling-system'
        },
        {
          id: 4,
          name: 'سیستم سوخت',
          description: 'پمپ بنزین، فیلتر سوخت و انژکتور',
          image: img10105,
          icon: '⛽',
          productCount: 18,
          popularItems: 'پمپ بنزین، فیلتر سوخت، انژکتور',
          slug: 'fuel-system'
        },
        {
          id: 5,
          name: 'سیستم برق',
          description: 'باتری، آلترناتور و سیستم برق',
          image: img10106,
          icon: '⚡',
          productCount: 52,
          popularItems: 'باتری، آلترناتور، استارت',
          slug: 'electrical-system'
        },
        {
          id: 6,
          name: 'سیستم تعلیق',
          description: 'فنر، کمک‌فنر و سیستم تعلیق',
          image: img10110,
          icon: '🚗',
          productCount: 38,
          popularItems: 'فنر، کمک‌فنر، بوش',
          slug: 'suspension-system'
        },
        {
          id: 7,
          name: 'سیستم اگزوز',
          description: 'منیفولد، کاتالیست و سیستم اگزوز',
          image: img10111,
          icon: '💨',
          productCount: 24,
          popularItems: 'منیفولد، کاتالیست، لوله اگزوز',
          slug: 'exhaust-system'
        },
        {
          id: 8,
          name: 'قطعات داخلی',
          description: 'دکمه‌ها، دستگیره‌ها و قطعات داخلی',
          image: img10113,
          icon: '🚪',
          productCount: 67,
          popularItems: 'دکمه‌ها، دستگیره‌ها، آینه',
          slug: 'interior-parts'
        }
      ]
    }
  },
  methods: {
    navigateToCategory(category) {
      // Navigate to Product List Page with category filter
      this.$router.push({
        name: 'Search',
        query: {
          category: category.slug,
          categoryName: category.name
        }
      })
    },
    
    formatPersianNumber(number, suffix = '') {
      return formatPersianNumber(number, suffix)
    }
  }
}
</script>

<style scoped>
.category-management {
  @apply py-16 bg-gray-50;
}

/* Custom hover effects */
.group:hover .group-hover\:scale-110 {
  transform: scale(1.1);
}

/* Persian text styling */
.font-persian {
  font-family: 'Peyda', sans-serif;
}

.font-persian-bold {
  font-family: 'Peyda', sans-serif;
  font-weight: 700;
}

/* RTL support */
.text-rtl {
  direction: rtl;
  text-align: right;
}
</style>
