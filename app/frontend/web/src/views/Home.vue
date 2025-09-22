<template>
  <div class="home">
    <!-- Hero Section -->
    <section class="bg-gradient-to-r from-blue-600 to-blue-800 text-white font-persian">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
        <div class="text-center font-persian">
          <h1 class="text-4xl md:text-6xl font-bold mb-6 font-persian-bold text-rtl">
            قطعات خودرو چین با کیفیت
          </h1>
          <p class="text-xl md:text-2xl mb-8 text-blue-100 font-persian text-rtl font-persian text-rtl">
            قطعات مناسب خودرو خود را با قیمت‌های رقابتی و ارسال سریع پیدا کنید
          </p>
          <div class="flex flex-col sm:flex-row gap-4 justify-center">
            <router-link 
              to="/search" 
              class="bg-white text-blue-600 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors font-persian"
            >
              جستجوی قطعات
            </router-link>
            <button 
              @click="$emit('show-contact')"
              class="border-2 border-white text-white px-8 py-3 rounded-lg font-semibold hover:bg-white hover:text-blue-600 transition-colors font-persian"
            >
              دریافت پیشنهاد
            </button>
          </div>
        </div>
      </div>
    </section>

    <!-- Category Management Section -->
    <section class="py-16 bg-gray-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <CategoryManagement />
      </div>
    </section>

    <!-- Features Section -->
    <section class="py-16 bg-white">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-12">
          <h2 class="text-3xl font-bold text-gray-900 mb-4 font-persian-bold text-rtl">چرا ما را انتخاب کنید؟</h2>
          <p class="text-lg text-gray-600 font-persian text-rtl">بهترین خدمات را برای قطعات خودرو چین ارائه می‌دهیم</p>
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
  </div>
</template>

<script>
import CategoryManagement from '../components/CategoryManagement.vue'

export default {
  name: 'خانه',
  components: {
    CategoryManagement
  },
  data() {
    return {
      // Component data if needed
    }
  }
}
</script>
