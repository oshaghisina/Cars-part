<template>
  <div class="min-h-screen bg-gray-50 flex items-center justify-center px-4">
    <div class="max-w-md w-full bg-white rounded-lg shadow-lg p-8 text-center">
      <!-- Loading State -->
      <div v-if="loading" class="space-y-4">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
        <h2 class="text-xl font-bold text-gray-900 font-persian-bold text-rtl">
          در حال تأیید ورود...
        </h2>
        <p class="text-gray-600 font-persian text-rtl">
          لطفاً صبر کنید تا ورود شما تأیید شود
        </p>
      </div>

      <!-- Success State -->
      <div v-else-if="success" class="space-y-4">
        <div class="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto">
          <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <h2 class="text-xl font-bold text-gray-900 font-persian-bold text-rtl">
          ورود موفقیت‌آمیز!
        </h2>
        <p class="text-gray-600 font-persian text-rtl">
          خوش آمدید {{ user?.first_name || user?.username || 'کاربر' }}
        </p>
        <button
          @click="redirectToHome"
          class="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors font-persian"
        >
          ادامه به صفحه اصلی
        </button>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="space-y-4">
        <div class="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mx-auto">
          <svg class="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </div>
        <h2 class="text-xl font-bold text-gray-900 font-persian-bold text-rtl">
          خطا در ورود
        </h2>
        <p class="text-gray-600 font-persian text-rtl">
          {{ error }}
        </p>
        <div class="space-y-2">
          <button
            @click="retryVerification"
            class="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors font-persian"
          >
            تلاش مجدد
          </button>
          <button
            @click="redirectToLogin"
            class="w-full bg-gray-600 text-white py-2 px-4 rounded-md hover:bg-gray-700 transition-colors font-persian"
          >
            بازگشت به ورود
          </button>
        </div>
      </div>

      <!-- Instructions State -->
      <div v-else class="space-y-4">
        <div class="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto">
          <svg class="w-6 h-6 text-blue-600" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm5.568 8.16l-1.61 7.59c-.12.54-.44.68-.89.42l-2.46-1.81-1.19 1.15c-.13.13-.24.24-.49.24l.18-2.55 4.57-4.13c.2-.18-.04-.28-.31-.1l-5.64 3.55-2.43-.76c-.53-.16-.54-.53.11-.79l9.57-3.69c.44-.16.83.1.69.79z"/>
          </svg>
        </div>
        <h2 class="text-xl font-bold text-gray-900 font-persian-bold text-rtl">
          تأیید ورود در تلگرام
        </h2>
        <p class="text-gray-600 font-persian text-rtl">
          لطفاً در تلگرام روی دکمه تأیید کلیک کنید تا ورود شما کامل شود
        </p>
        <div class="space-y-2">
          <button
            @click="checkVerification"
            class="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors font-persian"
          >
            بررسی وضعیت
          </button>
          <button
            @click="redirectToLogin"
            class="w-full bg-gray-600 text-white py-2 px-4 rounded-md hover:bg-gray-700 transition-colors font-persian"
          >
            بازگشت به ورود
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth.js'

export default {
  name: 'TelegramCallback',
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()
    
    const loading = ref(false)
    const success = ref(false)
    const error = ref('')
    const user = ref(null)

    const checkVerification = async () => {
      loading.value = true
      error.value = ''
      
      try {
        // Get the stored link token
        const linkToken = localStorage.getItem('telegram_link_token')
        
        if (!linkToken) {
          error.value = 'لینک تأیید یافت نشد. لطفاً مجدداً وارد شوید.'
          return
        }

        // Verify the token
        const result = await authStore.verifyTelegramLogin(linkToken)
        
        if (result.success) {
          success.value = true
          user.value = result.user
          
          // Redirect to home after 2 seconds
          setTimeout(() => {
            router.push('/')
          }, 2000)
        } else {
          error.value = result.message || 'خطا در تأیید ورود'
        }
      } catch (err) {
        console.error('Verification error:', err)
        error.value = 'خطا در تأیید ورود'
      } finally {
        loading.value = false
      }
    }

    const retryVerification = () => {
      error.value = ''
      checkVerification()
    }

    const redirectToHome = () => {
      router.push('/')
    }

    const redirectToLogin = () => {
      router.push('/')
    }

    // Auto-check verification on mount
    onMounted(() => {
      checkVerification()
    })

    return {
      loading,
      success,
      error,
      user,
      checkVerification,
      retryVerification,
      redirectToHome,
      redirectToLogin
    }
  }
}
</script>
