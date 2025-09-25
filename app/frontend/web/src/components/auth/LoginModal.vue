<template>
  <div
    v-if="isOpen"
    class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    @click="closeModal"
  >
    <div class="bg-white rounded-lg p-8 max-w-md w-full mx-4" @click.stop>
      <div class="flex justify-between items-center mb-6">
        <h2 class="text-2xl font-bold text-gray-900 font-persian-bold text-rtl">ورود به حساب کاربری</h2>
        <button
          @click="closeModal"
          class="text-gray-400 hover:text-gray-600 transition-colors"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <form @submit.prevent="handleLogin" class="space-y-4">
        <div>
          <label for="username" class="block text-sm font-medium text-gray-700 mb-2 font-persian text-rtl">
            نام کاربری یا ایمیل
          </label>
          <input
            id="username"
            v-model="form.username_or_email"
            type="text"
            required
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 font-persian text-rtl"
            :class="{ 'border-red-500': errors.username_or_email }"
            placeholder="نام کاربری یا ایمیل خود را وارد کنید"
          />
          <p v-if="errors.username_or_email" class="mt-1 text-sm text-red-600 font-persian text-rtl">
            {{ errors.username_or_email }}
          </p>
        </div>

        <div>
          <label for="password" class="block text-sm font-medium text-gray-700 mb-2 font-persian text-rtl">
            رمز عبور
          </label>
          <input
            id="password"
            v-model="form.password"
            type="password"
            required
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 font-persian text-rtl"
            :class="{ 'border-red-500': errors.password }"
            placeholder="رمز عبور خود را وارد کنید"
          />
          <p v-if="errors.password" class="mt-1 text-sm text-red-600 font-persian text-rtl">
            {{ errors.password }}
          </p>
        </div>

        <div v-if="error" class="bg-red-50 border border-red-200 rounded-md p-3">
          <p class="text-sm text-red-600 font-persian text-rtl">{{ error }}</p>
        </div>

        <button
          type="submit"
          :disabled="loading"
          class="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors font-persian flex items-center justify-center gap-2"
        >
          <div v-if="loading" class="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
          {{ loading ? 'در حال ورود...' : 'ورود' }}
        </button>
      </form>

      <!-- Divider -->
      <div class="mt-6 mb-6">
        <div class="relative">
          <div class="absolute inset-0 flex items-center">
            <div class="w-full border-t border-gray-300" />
          </div>
          <div class="relative flex justify-center text-sm">
            <span class="px-2 bg-white text-gray-500 font-persian text-rtl">یا</span>
          </div>
        </div>
      </div>

      <!-- Phone Login -->
      <PhoneLoginButton 
        @login-success="handlePhoneSuccess"
        @error="handlePhoneError"
      />

      <!-- Divider -->
      <div class="mt-6 mb-6">
        <div class="relative">
          <div class="absolute inset-0 flex items-center">
            <div class="w-full border-t border-gray-300" />
          </div>
          <div class="relative flex justify-center text-sm">
            <span class="px-2 bg-white text-gray-500 font-persian text-rtl">یا</span>
          </div>
        </div>
      </div>

      <!-- Telegram Login -->
      <TelegramLoginButton 
        @login-success="handleTelegramSuccess"
        @error="handleTelegramError"
      />

      <div class="mt-6 text-center">
        <p class="text-sm text-gray-600 font-persian text-rtl">
          حساب کاربری ندارید؟
          <button
            @click="showRegister"
            class="text-blue-600 hover:text-blue-700 font-medium"
          >
            ثبت نام کنید
          </button>
        </p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed } from 'vue'
import { useAuthStore } from '@/stores/auth.js'
import TelegramLoginButton from './TelegramLoginButton.vue'
import PhoneLoginButton from './PhoneLoginButton.vue'

export default {
  name: 'LoginModal',
  components: {
    TelegramLoginButton,
    PhoneLoginButton
  },
  props: {
    isOpen: {
      type: Boolean,
      default: false
    }
  },
  emits: ['close', 'show-register', 'login-success'],
  setup(props, { emit }) {
    const authStore = useAuthStore()
    
    const form = reactive({
      username_or_email: '',
      password: ''
    })
    
    const errors = reactive({
      username_or_email: '',
      password: ''
    })

    const loading = computed(() => authStore.loading)
    const error = computed(() => authStore.error)

    const validateForm = () => {
      let isValid = true
      
      // Clear previous errors
      errors.username_or_email = ''
      errors.password = ''

      if (!form.username_or_email.trim()) {
        errors.username_or_email = 'نام کاربری یا ایمیل الزامی است'
        isValid = false
      }

      if (!form.password) {
        errors.password = 'رمز عبور الزامی است'
        isValid = false
      }

      return isValid
    }

    const handleLogin = async () => {
      if (!validateForm()) return

      const result = await authStore.login(form)
      
      if (result.success) {
        emit('login-success', result.user)
        closeModal()
      }
    }

    const closeModal = () => {
      // Clear form and errors
      form.username_or_email = ''
      form.password = ''
      errors.username_or_email = ''
      errors.password = ''
      authStore.clearError()
      
      emit('close')
    }

    const showRegister = () => {
      emit('show-register')
    }

    const handleTelegramSuccess = (data) => {
      // Show success message and redirect to callback page
      emit('login-success', data)
      // Redirect to callback page to handle verification
      window.location.href = '/auth/telegram/callback'
    }

    const handleTelegramError = (errorMessage) => {
      // Set error message to be displayed
      authStore.error = errorMessage
    }

    const handlePhoneSuccess = (data) => {
      // Show success message and close modal
      emit('login-success', data)
      closeModal()
    }

    const handlePhoneError = (errorMessage) => {
      // Set error message to be displayed
      authStore.error = errorMessage
    }

    return {
      form,
      errors,
      loading,
      error,
      handleLogin,
      closeModal,
      showRegister,
      handleTelegramSuccess,
      handleTelegramError,
      handlePhoneSuccess,
      handlePhoneError
    }
  }
}
</script>
