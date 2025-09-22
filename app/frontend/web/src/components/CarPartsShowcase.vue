<template>
  <div class="car-parts-showcase">
    <!-- Header Section -->
    <div class="text-center mb-12">
      <h2 class="text-4xl font-bold text-gray-900 mb-4 font-persian-bold text-rtl">
        قطعات خودرو با کیفیت
      </h2>
      <p class="text-lg text-gray-600 font-persian text-rtl max-w-3xl mx-auto">
        مجموعه کاملی از قطعات خودرو چین با بالاترین کیفیت و مناسب‌ترین قیمت
      </p>
    </div>

    <!-- Parts Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8">
      <div 
        v-for="(part, index) in carParts" 
        :key="part.id"
        class="group relative bg-white rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-2 overflow-hidden"
      >
        <!-- Image Container -->
        <div class="relative h-48 bg-gradient-to-br from-blue-50 to-gray-100 overflow-hidden">
          <img 
            :src="part.image" 
            :alt="part.name"
            class="w-full h-full object-contain p-4 group-hover:scale-110 transition-transform duration-300"
            loading="lazy"
          />
          <!-- Overlay -->
          <div class="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
        </div>

        <!-- Content -->
        <div class="p-6">
          <h3 class="text-xl font-semibold text-gray-900 mb-2 font-persian-bold text-rtl">
            {{ part.name }}
          </h3>
          <p class="text-gray-600 text-sm mb-4 font-persian text-rtl">
            {{ part.description }}
          </p>
          
          <!-- Price and Stock -->
          <div class="flex justify-between items-center mb-4">
            <span class="text-2xl font-bold text-blue-600 font-persian">
              {{ part.price }}
            </span>
            <span class="text-sm text-gray-500 font-persian" :class="part.stock > 0 ? 'text-green-600' : 'text-red-600'">
              {{ part.stock > 0 ? 'موجود' : 'ناموجود' }}
            </span>
          </div>

          <!-- Action Buttons -->
          <div class="flex gap-2">
            <button 
              class="flex-1 bg-blue-600 text-white py-2 px-4 rounded-lg font-semibold hover:bg-blue-700 transition-colors font-persian"
              :disabled="part.stock === 0"
            >
              {{ part.stock > 0 ? 'افزودن به سبد' : 'ناموجود' }}
            </button>
            <button 
              class="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
              title="مشاهده جزئیات"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
              </svg>
            </button>
          </div>
        </div>

        <!-- Badge -->
        <div v-if="part.isNew" class="absolute top-4 right-4 bg-green-500 text-white px-3 py-1 rounded-full text-sm font-semibold font-persian">
          جدید
        </div>
        <div v-if="part.isPopular" class="absolute top-4 right-4 bg-red-500 text-white px-3 py-1 rounded-full text-sm font-semibold font-persian">
          پرفروش
        </div>
      </div>
    </div>

    <!-- View All Button -->
    <div class="text-center mt-12">
      <router-link 
        to="/search" 
        class="inline-flex items-center bg-gradient-to-r from-blue-600 to-blue-700 text-white px-8 py-4 rounded-xl font-semibold hover:from-blue-700 hover:to-blue-800 transition-all duration-300 transform hover:scale-105 font-persian"
      >
        <span>مشاهده تمام قطعات</span>
        <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
        </svg>
      </router-link>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CarPartsShowcase',
  data() {
    return {
      carParts: [
        {
          id: 1,
          name: 'لنت ترمز جلو',
          description: 'لنت ترمز با کیفیت بالا برای خودروهای چینی',
          price: '۲۵۰,۰۰۰ تومان',
          stock: 15,
          image: '/src/assets/images/parts/10101.png',
          isNew: true,
          isPopular: false
        },
        {
          id: 2,
          name: 'فیلتر روغن',
          description: 'فیلتر روغن اصلی برای موتورهای چینی',
          price: '۸۵,۰۰۰ تومان',
          stock: 32,
          image: '/src/assets/images/parts/10102.png',
          isNew: false,
          isPopular: true
        },
        {
          id: 3,
          name: 'شمع احتراق',
          description: 'شمع احتراق با کیفیت بالا',
          price: '۱۲۰,۰۰۰ تومان',
          stock: 8,
          image: '/src/assets/images/parts/10104.png',
          isNew: false,
          isPopular: false
        },
        {
          id: 4,
          name: 'کمربند تایم',
          description: 'کمربند تایم اصلی برای موتور',
          price: '۱۸۰,۰۰۰ تومان',
          stock: 12,
          image: '/src/assets/images/parts/10105.png',
          isNew: true,
          isPopular: false
        },
        {
          id: 5,
          name: 'پمپ آب',
          description: 'پمپ آب اصلی برای سیستم خنک‌کننده',
          price: '۳۲۰,۰۰۰ تومان',
          stock: 6,
          image: '/src/assets/images/parts/10106.png',
          isNew: false,
          isPopular: true
        },
        {
          id: 6,
          name: 'ترموستات',
          description: 'ترموستات موتور با کیفیت بالا',
          price: '۹۵,۰۰۰ تومان',
          stock: 20,
          image: '/src/assets/images/parts/10110.png',
          isNew: false,
          isPopular: false
        },
        {
          id: 7,
          name: 'سنسور اکسیژن',
          description: 'سنسور اکسیژن برای سیستم سوخت',
          price: '۲۸۰,۰۰۰ تومان',
          stock: 4,
          image: '/src/assets/images/parts/10111.png',
          isNew: true,
          isPopular: false
        },
        {
          id: 8,
          name: 'کویل احتراق',
          description: 'کویل احتراق با کیفیت بالا',
          price: '۱۵۰,۰۰۰ تومان',
          stock: 18,
          image: '/src/assets/images/parts/10113.png',
          isNew: false,
          isPopular: true
        }
      ]
    }
  }
}
</script>

<style scoped>
.car-parts-showcase {
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
