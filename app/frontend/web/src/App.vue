<template>
  <div id="app" class="min-h-screen bg-gray-50">
    <!-- Navigation Header -->
    <nav class="bg-white shadow-sm border-b">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex items-center">
            <router-link to="/" class="flex items-center space-x-2">
              <div class="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                <span class="text-white font-bold text-lg font-persian font-persian">🚗</span>
              </div>
              <span class="text-xl font-bold text-gray-900 font-persian-bold font-persian font-persian">قطعات خودرو چین</span>
            </router-link>
          </div>
          
          <div class="flex items-center space-x-4">
            <router-link 
              to="/search" 
              class="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium font-persian font-persian font-persian"
            >
              جستجوی قطعات
            </router-link>
            <router-link 
              to="/track" 
              class="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium font-persian font-persian font-persian"
            >
              پیگیری سفارش
            </router-link>
            <button 
              @click="showContactForm = true"
              class="bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-700 font-persian font-persian font-persian"
            >
              دریافت پیشنهاد
            </button>
          </div>
        </div>
      </div>
    </nav>

    <!-- Main Content -->
    <main class="flex-1">
      <router-view />
    </main>

    <!-- Footer -->
    <footer class="bg-gray-800 text-white font-persian font-persian">
      <div class="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div>
            <h3 class="text-lg font-semibold mb-4 font-persian-bold text-rtl font-persian font-persian" class="font-persian-bold text-rtl">درباره ما</h3>
            <p class="text-gray-300 font-persian text-rtl font-persian font-persian" class="font-persian text-rtl">
              شریک قابل اعتماد شما برای قطعات خودرو چین. قطعات با کیفیت، قیمت‌های رقابتی، ارسال سریع.
            </p>
          </div>
          <div>
            <h3 class="text-lg font-semibold mb-4 font-persian-bold text-rtl font-persian font-persian" class="font-persian-bold text-rtl">لینک‌های سریع</h3>
            <ul class="space-y-2">
              <li><router-link to="/search" class="text-gray-300 hover:text-white font-persian text-rtl font-persian font-persian">جستجوی قطعات</router-link></li>
              <li><router-link to="/track" class="text-gray-300 hover:text-white font-persian text-rtl font-persian font-persian">پیگیری سفارش</router-link></li>
              <li><a href="/panel/" class="text-gray-300 hover:text-white font-persian text-rtl font-persian font-persian">پنل مدیریت</a></li>
            </ul>
          </div>
          <div>
            <h3 class="text-lg font-semibold mb-4 font-persian-bold text-rtl font-persian font-persian" class="font-persian-bold text-rtl">تماس با ما</h3>
            <p class="text-gray-300 font-persian text-rtl font-persian font-persian" class="font-persian text-rtl">
              ایمیل: info@chinaautoparts.com<br>
              تلفن: +86 123 456 7890
            </p>
          </div>
        </div>
        <div class="mt-8 pt-8 border-t border-gray-700 text-center text-gray-300 font-persian font-persian">
          <p class="font-persian text-rtl font-persian font-persian" class="font-persian text-rtl">&copy; 2024 قطعات خودرو چین. تمامی حقوق محفوظ است.</p>
        </div>
      </div>
    </footer>

    <!-- Contact Form Modal -->
    <ContactForm v-if="showContactForm" @close="showContactForm = false" />
  </div>
</template>

<script>
import ContactForm from './components/ContactForm.vue'

export default {
  name: 'App',
  components: {
    ContactForm
  },
  data() {
    return {
      showContactForm: false
    }
  }
}
</script>
