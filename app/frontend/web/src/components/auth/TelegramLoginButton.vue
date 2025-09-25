<template>
  <button
    @click="handleTelegramLogin"
    :disabled="loading"
    class="w-full bg-[#0088cc] text-white py-2 px-4 rounded-md hover:bg-[#006699] disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors font-persian flex items-center justify-center gap-3"
  >
    <div v-if="loading" class="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
    <svg v-else class="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
      <path d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm5.568 8.16l-1.61 7.59c-.12.54-.44.68-.89.42l-2.46-1.81-1.19 1.15c-.13.13-.24.24-.49.24l.18-2.55 4.57-4.13c.2-.18-.04-.28-.31-.1l-5.64 3.55-2.43-.76c-.53-.16-.54-.53.11-.79l9.57-3.69c.44-.16.83.1.69.79z"/>
    </svg>
    {{ loading ? 'در حال اتصال...' : 'ورود با تلگرام' }}
  </button>
</template>

<script>
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth.js'

export default {
  name: 'TelegramLoginButton',
  emits: ['login-success', 'error'],
  setup(props, { emit }) {
    const authStore = useAuthStore()
    const loading = ref(false)

    const handleTelegramLogin = async () => {
      loading.value = true
      
      try {
        // For demo purposes, we'll use a mock Telegram ID
        // In a real implementation, this would come from Telegram Web App or user input
        const mockTelegramId = 176007160 // This should be replaced with actual Telegram user ID
        
        const result = await authStore.loginWithTelegram(mockTelegramId)
        
        if (result.success) {
          // Show success message and instructions
          emit('login-success', {
            message: 'لینک ورود به تلگرام ارسال شد. لطفاً در تلگرام روی دکمه تأیید کلیک کنید.',
            telegramUrl: result.telegramUrl
          })
        } else {
          emit('error', result.message || 'خطا در ورود با تلگرام')
        }
      } catch (error) {
        console.error('Telegram login error:', error)
        emit('error', 'خطا در ورود با تلگرام')
      } finally {
        loading.value = false
      }
    }

    return {
      loading,
      handleTelegramLogin
    }
  }
}
</script>

<style scoped>
/* Telegram brand colors */
.bg-\[#0088cc\]:hover {
  background-color: #006699;
}
</style>
