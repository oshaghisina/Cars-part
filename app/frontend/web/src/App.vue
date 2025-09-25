<template>
  <div id="app" class="min-h-screen bg-gray-50" dir="rtl">
    <!-- Navigation Header -->
    <nav class="bg-white shadow-sm border-b">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16" dir="rtl">
          <!-- Logo Section (Right side in RTL) -->
          <div class="flex items-center">
            <router-link to="/" class="flex items-center space-x-2 space-x-reverse">
              <div class="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                <span class="text-white font-bold text-lg">🚗</span>
              </div>
              <span class="text-xl font-bold text-gray-900 font-persian-bold text-rtl">قطعات خودرو</span>
            </router-link>
          </div>
          
          <!-- Navigation Menu (Left side in RTL) -->
          <div class="flex items-center space-x-4 space-x-reverse">
            <router-link 
              to="/search" 
              class="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium font-persian text-rtl"
            >
              جستجوی قطعات
            </router-link>
            <router-link 
              to="/track" 
              class="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium font-persian text-rtl"
            >
              پیگیری سفارش
            </router-link>
            <button 
              @click="showContactForm = true"
              class="bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-700 font-persian text-rtl"
            >
              دریافت پیشنهاد
            </button>
            
            <!-- Authentication Section -->
            <div class="flex items-center space-x-2 space-x-reverse">
              <!-- Authenticated User Menu -->
              <UserMenu v-if="authStore.isAuthenticated" />
              
              <!-- Unauthenticated Login/Register Buttons -->
              <div v-else class="flex items-center space-x-2 space-x-reverse">
                <button 
                  @click="handleLoginClick"
                  class="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium font-persian text-rtl"
                >
                  ورود
                </button>
                <button 
                  @click="showRegisterModal = true"
                  class="bg-green-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-green-700 font-persian text-rtl"
                >
                  ثبت نام
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </nav>

    <!-- Main Content -->
    <main class="flex-1">
      <router-view />
    </main>

    <!-- Footer -->
    <footer class="bg-gray-800 text-white">
      <div class="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div>
              <h3 class="text-lg font-semibold mb-4 font-persian-bold text-rtl">درباره ما</h3>
              <p class="text-gray-300 font-persian text-rtl">
              شریک قابل اعتماد شما برای قطعات خودرو. قطعات با کیفیت، قیمت‌های رقابتی، ارسال سریع.
            </p>
          </div>
          <div>
            <h3 class="text-lg font-semibold mb-4 font-persian-bold text-rtl">لینک‌های سریع</h3>
            <ul class="space-y-2">
              <li><router-link to="/search" class="text-gray-300 hover:text-white font-persian text-rtl">جستجوی قطعات</router-link></li>
              <li><router-link to="/track" class="text-gray-300 hover:text-white font-persian text-rtl">پیگیری سفارش</router-link></li>
              <li><a href="/panel/" class="text-gray-300 hover:text-white font-persian text-rtl">پنل مدیریت</a></li>
            </ul>
          </div>
          <div>
            <h3 class="text-lg font-semibold mb-4 font-persian-bold text-rtl">تماس با ما</h3>
            <p class="text-gray-300 font-persian text-rtl">
              ایمیل: info@chinaautoparts.com<br>
              تلفن: +86 123 456 7890
            </p>
          </div>
        </div>
        <div class="mt-8 pt-8 border-t border-gray-700 text-center text-gray-300">
          <p class="font-persian text-rtl">&copy; 2024 قطعات خودرو. تمامی حقوق محفوظ است.</p>
        </div>
      </div>
    </footer>

    <!-- Contact Form Modal -->
    <ContactForm v-if="showContactForm" @close="showContactForm = false" />
    
    <!-- Login Modal -->
    <LoginModal 
      :is-open="showLoginModal"
      @close="showLoginModal = false"
      @login-success="handleLoginSuccess"
    />
    
    <!-- Register Modal -->
    <RegisterModal 
      v-if="showRegisterModal" 
      @close="showRegisterModal = false"
      @register-success="handleRegisterSuccess"
      @show-login="handleShowLogin"
    />
  </div>
</template>

<script>
import { onMounted } from 'vue'
import ContactForm from './components/ContactForm.vue'
import LoginModal from './components/auth/LoginModal.vue'
import RegisterModal from './components/auth/RegisterModal.vue'
import UserMenu from './components/auth/UserMenu.vue'
import { useAuthStore } from './stores/auth.js'

export default {
  name: 'App',
  components: {
    ContactForm,
    LoginModal,
    RegisterModal,
    UserMenu
  },
  setup() {
    const authStore = useAuthStore()
    
    return {
      authStore
    }
  },
  data() {
    return {
      showContactForm: false,
      showLoginModal: false,
      showRegisterModal: false
    }
  },
  methods: {
    handleLoginClick() {
      console.log('Login button clicked!')
      console.log('Current showLoginModal:', this.showLoginModal)
      console.log('Auth store:', this.authStore)
      this.showLoginModal = true
      console.log('New showLoginModal:', this.showLoginModal)
    },
    handleLoginSuccess(data) {
      this.showLoginModal = false
      // Optionally show success message or redirect
      console.log('Login successful:', data)
    },
    handleRegisterSuccess(data) {
      this.showRegisterModal = false
      // Optionally show success message or redirect
      console.log('Register successful:', data)
    },
    handleShowLogin() {
      this.showRegisterModal = false
      this.showLoginModal = true
    }
  },
  mounted() {
    // Initialize authentication on app mount
    this.authStore.initializeAuth()
  }
}
</script>