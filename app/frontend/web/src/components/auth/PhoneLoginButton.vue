<template>
  <div class="w-full">
    <!-- Phone Login Button -->
    <button
      v-if="!showPhoneForm"
      @click="showPhoneForm = true"
      class="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 transition-colors font-persian flex items-center justify-center gap-2"
    >
      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
      </svg>
      ورود با شماره تلفن
    </button>

    <!-- Phone Login Form -->
    <div v-if="showPhoneForm" class="space-y-4">
      <!-- Back Button -->
      <button
        @click="resetForm"
        class="text-gray-500 hover:text-gray-700 text-sm font-persian flex items-center gap-1"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
        بازگشت
      </button>

      <!-- Phone Number Input -->
      <div v-if="!otpSent">
        <label for="phone" class="block text-sm font-medium text-gray-700 mb-2 font-persian text-rtl">
          شماره تلفن
        </label>
        <input
          id="phone"
          v-model="phoneNumber"
          type="tel"
          required
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-green-500 focus:border-green-500 font-persian text-rtl"
          :class="{ 'border-red-500': errors.phone }"
          placeholder="+989123456789"
          @input="formatPhoneNumber"
        />
        <p v-if="errors.phone" class="mt-1 text-sm text-red-600 font-persian text-rtl">
          {{ errors.phone }}
        </p>
        <p class="mt-1 text-xs text-gray-500 font-persian text-rtl">
          شماره تلفن خود را با کد کشور وارد کنید (مثال: +989123456789)
        </p>
      </div>

      <!-- OTP Input -->
      <div v-if="otpSent">
        <label for="otp" class="block text-sm font-medium text-gray-700 mb-2 font-persian text-rtl">
          کد تایید
        </label>
        <input
          id="otp"
          v-model="otpCode"
          type="text"
          required
          maxlength="6"
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-green-500 focus:border-green-500 font-persian text-center text-lg tracking-widest"
          :class="{ 'border-red-500': errors.otp }"
          placeholder="123456"
          @input="formatOTPCode"
        />
        <p v-if="errors.otp" class="mt-1 text-sm text-red-600 font-persian text-rtl">
          {{ errors.otp }}
        </p>
        <p class="mt-1 text-xs text-gray-500 font-persian text-rtl">
          کد ۶ رقمی ارسال شده به شماره {{ phoneNumber }} را وارد کنید
        </p>
      </div>

      <!-- Error Message -->
      <div v-if="error" class="bg-red-50 border border-red-200 rounded-md p-3">
        <p class="text-sm text-red-600 font-persian text-rtl">{{ error }}</p>
      </div>

      <!-- Success Message -->
      <div v-if="successMessage" class="bg-green-50 border border-green-200 rounded-md p-3">
        <p class="text-sm text-green-600 font-persian text-rtl">{{ successMessage }}</p>
      </div>

      <!-- Action Buttons -->
      <div class="space-y-2">
        <!-- Send OTP Button -->
        <button
          v-if="!otpSent"
          @click="sendOTP"
          :disabled="loading || !isValidPhone"
          class="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors font-persian flex items-center justify-center gap-2"
        >
          <div v-if="loading" class="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
          {{ loading ? 'در حال ارسال...' : 'ارسال کد تایید' }}
        </button>

        <!-- Verify OTP Button -->
        <button
          v-if="otpSent"
          @click="verifyOTP"
          :disabled="loading || !isValidOTP"
          class="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors font-persian flex items-center justify-center gap-2"
        >
          <div v-if="loading" class="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
          {{ loading ? 'در حال تایید...' : 'تایید و ورود' }}
        </button>

        <!-- Resend OTP Button -->
        <button
          v-if="otpSent && canResend"
          @click="resendOTP"
          :disabled="loading"
          class="w-full text-green-600 hover:text-green-700 text-sm font-persian"
        >
          ارسال مجدد کد
        </button>
      </div>

      <!-- Countdown Timer -->
      <div v-if="otpSent && !canResend" class="text-center">
        <p class="text-sm text-gray-500 font-persian text-rtl">
          ارسال مجدد کد در {{ countdown }} ثانیه
        </p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '@/stores/auth.js'

export default {
  name: 'PhoneLoginButton',
  emits: ['login-success', 'error'],
  setup(props, { emit }) {
    const authStore = useAuthStore()
    
    // Form state
    const showPhoneForm = ref(false)
    const phoneNumber = ref('')
    const otpCode = ref('')
    const otpSent = ref(false)
    const loading = ref(false)
    const error = ref('')
    const successMessage = ref('')
    const canResend = ref(false)
    const countdown = ref(0)
    
    // Form validation
    const errors = reactive({
      phone: '',
      otp: ''
    })
    
    // Computed properties
    const isValidPhone = computed(() => {
      return phoneNumber.value.startsWith('+') && 
             phoneNumber.value.length >= 10 && 
             phoneNumber.value.length <= 16
    })
    
    const isValidOTP = computed(() => {
      return otpCode.value.length === 6 && /^\d+$/.test(otpCode.value)
    })
    
    // Timer for resend countdown
    let countdownTimer = null
    
    // Format phone number input
    const formatPhoneNumber = (event) => {
      let value = event.target.value.replace(/\D/g, '')
      if (value && !value.startsWith('+')) {
        value = '+' + value
      }
      phoneNumber.value = value
      clearErrors()
    }
    
    // Format OTP code input
    const formatOTPCode = (event) => {
      let value = event.target.value.replace(/\D/g, '')
      if (value.length > 6) {
        value = value.substring(0, 6)
      }
      otpCode.value = value
      clearErrors()
    }
    
    // Clear validation errors
    const clearErrors = () => {
      errors.phone = ''
      errors.otp = ''
      error.value = ''
    }
    
    // Validate phone number
    const validatePhone = () => {
      if (!phoneNumber.value.trim()) {
        errors.phone = 'شماره تلفن الزامی است'
        return false
      }
      if (!phoneNumber.value.startsWith('+')) {
        errors.phone = 'شماره تلفن باید با + شروع شود'
        return false
      }
      if (phoneNumber.value.length < 10 || phoneNumber.value.length > 16) {
        errors.phone = 'شماره تلفن باید بین ۱۰ تا ۱۶ رقم باشد'
        return false
      }
      return true
    }
    
    // Validate OTP code
    const validateOTP = () => {
      if (!otpCode.value.trim()) {
        errors.otp = 'کد تایید الزامی است'
        return false
      }
      if (otpCode.value.length !== 6) {
        errors.otp = 'کد تایید باید ۶ رقم باشد'
        return false
      }
      if (!/^\d+$/.test(otpCode.value)) {
        errors.otp = 'کد تایید باید فقط شامل اعداد باشد'
        return false
      }
      return true
    }
    
    // Send OTP code
    const sendOTP = async () => {
      if (!validatePhone()) return
      
      loading.value = true
      clearErrors()
      
      try {
        const response = await fetch('/api/v1/otp/phone/login/request', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            phone_number: phoneNumber.value
          })
        })
        
        const data = await response.json()
        
        if (response.ok && data.success) {
          otpSent.value = true
          successMessage.value = data.message || 'کد تایید ارسال شد'
          startCountdown()
        } else {
          error.value = data.detail || 'خطا در ارسال کد تایید'
        }
      } catch (err) {
        error.value = 'خطا در ارتباط با سرور'
        console.error('Error sending OTP:', err)
      } finally {
        loading.value = false
      }
    }
    
    // Verify OTP code
    const verifyOTP = async () => {
      if (!validateOTP()) return
      
      loading.value = true
      clearErrors()
      
      try {
        const response = await fetch('/api/v1/otp/phone/login/verify', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            phone_number: phoneNumber.value,
            otp_code: otpCode.value
          })
        })
        
        const data = await response.json()
        
        if (response.ok && data.success) {
          // Store the token
          if (data.access_token) {
            localStorage.setItem('access_token', data.access_token)
          }
          
          // Update auth store
          authStore.setUser(data.user)
          authStore.setToken(data.access_token)
          
          successMessage.value = 'ورود موفقیت‌آمیز بود'
          
          // Emit success event
          emit('login-success', data.user)
          
          // Reset form after a short delay
          setTimeout(() => {
            resetForm()
          }, 1000)
        } else {
          error.value = data.detail || 'کد تایید نامعتبر است'
        }
      } catch (err) {
        error.value = 'خطا در ارتباط با سرور'
        console.error('Error verifying OTP:', err)
      } finally {
        loading.value = false
      }
    }
    
    // Resend OTP code
    const resendOTP = async () => {
      await sendOTP()
    }
    
    // Start countdown timer
    const startCountdown = () => {
      canResend.value = false
      countdown.value = 60 // 60 seconds
      
      countdownTimer = setInterval(() => {
        countdown.value--
        if (countdown.value <= 0) {
          canResend.value = true
          clearInterval(countdownTimer)
        }
      }, 1000)
    }
    
    // Reset form
    const resetForm = () => {
      showPhoneForm.value = false
      phoneNumber.value = ''
      otpCode.value = ''
      otpSent.value = false
      error.value = ''
      successMessage.value = ''
      canResend.value = false
      countdown.value = 0
      clearErrors()
      
      if (countdownTimer) {
        clearInterval(countdownTimer)
        countdownTimer = null
      }
    }
    
    // Cleanup on unmount
    onUnmounted(() => {
      if (countdownTimer) {
        clearInterval(countdownTimer)
      }
    })
    
    return {
      showPhoneForm,
      phoneNumber,
      otpCode,
      otpSent,
      loading,
      error,
      successMessage,
      canResend,
      countdown,
      errors,
      isValidPhone,
      isValidOTP,
      formatPhoneNumber,
      formatOTPCode,
      sendOTP,
      verifyOTP,
      resendOTP,
      resetForm
    }
  }
}
</script>
