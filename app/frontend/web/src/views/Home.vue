<template>
  <div class="home">
    <!-- Hero Section -->
    <section class="bg-gradient-to-r from-blue-600 to-blue-800 text-white font-persian">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
        <div class="text-center font-persian">
          <h1 class="text-4xl md:text-6xl font-bold mb-6 font-persian-bold text-rtl">
            قطعات خودرو با کیفیت
          </h1>
          <p class="text-xl md:text-2xl mb-8 text-blue-100 font-persian text-rtl">
            قطعات مناسب خودرو خود را با قیمت‌های رقابتی و ارسال سریع پیدا کنید
          </p>
          <div class="flex flex-col sm:flex-row gap-4 justify-center">
            <router-link 
              to="/products" 
              class="bg-white text-blue-600 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors font-persian"
            >
              مشاهده همه محصولات
            </router-link>
            <router-link 
              to="/search" 
              class="border-2 border-white text-white px-8 py-3 rounded-lg font-semibold hover:bg-white hover:text-blue-600 transition-colors font-persian"
            >
              جستجوی قطعات
            </router-link>
            <button 
              @click="showContactForm = true"
              class="border-2 border-white text-white px-8 py-3 rounded-lg font-semibold hover:bg-white hover:text-blue-600 transition-colors font-persian"
            >
              دریافت پیشنهاد
            </button>
          </div>
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section class="py-16 bg-white">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-12">
          <h2 class="text-3xl font-bold text-gray-900 mb-4 font-persian-bold text-rtl">چرا ما را انتخاب کنید؟</h2>
          <p class="text-lg text-gray-600 font-persian text-rtl">بهترین خدمات را برای قطعات خودرو ارائه می‌دهیم</p>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div class="text-center">
            <div class="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <span class="text-2xl">🔍</span>
            </div>
            <h3 class="text-xl font-semibold mb-2 font-persian-bold text-rtl">جستجوی آسان</h3>
            <p class="text-gray-600 font-persian text-rtl">با سیستم جستجو و فیلتر پیشرفته ما، قطعات را سریع پیدا کنید</p>
          </div>
          
          <div class="text-center">
            <div class="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <span class="text-2xl">💰</span>
            </div>
            <h3 class="text-xl font-semibold mb-2 font-persian-bold text-rtl">قیمت‌های رقابتی</h3>
            <p class="text-gray-600 font-persian text-rtl">با روابط مستقیم ما با تامین‌کنندگان، بهترین قیمت‌ها را دریافت کنید</p>
          </div>
          
          <div class="text-center">
            <div class="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <span class="text-2xl">🚚</span>
            </div>
            <h3 class="text-xl font-semibold mb-2 font-persian-bold text-rtl">ارسال سریع</h3>
            <p class="text-gray-600 font-persian text-rtl">ارسال سریع و قابل اعتماد برای دریافت قطعات در زمان نیاز</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Categories Section -->
    <section class="py-16 bg-gray-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <CategoryManagement />
      </div>
    </section>

    <!-- Test PDP Section -->
    <section class="py-16 bg-white">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-12">
          <h2 class="text-3xl font-bold text-gray-900 mb-4 font-persian-bold text-rtl">تست PDP</h2>
          <p class="text-lg text-gray-600 font-persian text-rtl">برای تست صفحه جزئیات محصول، روی لینک زیر کلیک کنید</p>
        </div>
        
        <div class="text-center">
          <router-link 
            to="/part/14" 
            class="inline-flex items-center bg-gradient-to-r from-green-600 to-green-700 text-white px-8 py-4 rounded-xl font-semibold hover:from-green-700 hover:to-green-800 transition-all duration-300 transform hover:scale-105 font-persian"
          >
            <span>تست PDP - لنت ترمز جلو</span>
            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
            </svg>
          </router-link>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
import CategoryManagement from '@/components/CategoryManagement.vue'

export default {
  name: 'خانه',
  components: {
    CategoryManagement
  },
  data() {
    return {
      showContactForm: false
    }
  }
}
</script>