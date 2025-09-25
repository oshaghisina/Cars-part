<template>
  <div class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50" @click="closeModal">
    <div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white" @click.stop>
      <div class="mt-3">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-medium text-gray-900 font-persian text-rtl">ثبت نام</h3>
          <button @click="closeModal" class="text-gray-400 hover:text-gray-600">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>
        
        <form @submit.prevent="handleRegister" class="space-y-4">
          <div>
            <label for="username" class="block text-sm font-medium text-gray-700 font-persian text-rtl">نام کاربری</label>
            <input
              v-model="formData.username"
              type="text"
              id="username"
              required
              class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 font-persian text-rtl"
              placeholder="نام کاربری خود را وارد کنید"
            />
          </div>
          
          <div>
            <label for="email" class="block text-sm font-medium text-gray-700 font-persian text-rtl">ایمیل</label>
            <input
              v-model="formData.email"
              type="email"
              id="email"
              required
              class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 font-persian text-rtl"
              placeholder="ایمیل خود را وارد کنید"
            />
          </div>
          
          <div>
            <label for="password" class="block text-sm font-medium text-gray-700 font-persian text-rtl">رمز عبور</label>
            <input
              v-model="formData.password"
              type="password"
              id="password"
              required
              class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 font-persian text-rtl"
              placeholder="رمز عبور خود را وارد کنید"
            />
          </div>
          
          <div>
            <label for="confirmPassword" class="block text-sm font-medium text-gray-700 font-persian text-rtl">تکرار رمز عبور</label>
            <input
              v-model="formData.confirmPassword"
              type="password"
              id="confirmPassword"
              required
              class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 font-persian text-rtl"
              placeholder="رمز عبور را مجدداً وارد کنید"
            />
          </div>
          
          <button
            type="submit"
            :disabled="loading"
            class="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors font-persian flex items-center justify-center gap-2"
          >
            <div v-if="loading" class="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
            {{ loading ? 'در حال ثبت نام...' : 'ثبت نام' }}
          </button>
        </form>
        
        <div class="mt-6 text-center">
          <p class="text-sm text-gray-600 font-persian text-rtl">
            قبلاً حساب کاربری دارید؟
            <button @click="showLogin" class="text-blue-600 hover:text-blue-700 font-medium">
              وارد شوید
            </button>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'
import { useAuthStore } from '@/stores/auth.js'

export default {
  name: 'RegisterModal',
  emits: ['close', 'show-login'],
  setup(props, { emit }) {
    const authStore = useAuthStore()
    const loading = ref(false)
    
    const formData = reactive({
      username: '',
      email: '',
      password: '',
      confirmPassword: ''
    })
    
    const closeModal = () => {
      emit('close')
    }
    
    const showLogin = () => {
      emit('show-login')
    }
    
    const handleRegister = async () => {
      if (formData.password !== formData.confirmPassword) {
        alert('رمز عبور و تکرار آن مطابقت ندارند')
        return
      }
      
      loading.value = true
      try {
        const result = await authStore.register(formData)
        if (result.success) {
          closeModal()
        } else {
          alert(result.message || 'خطا در ثبت نام')
        }
      } catch (error) {
        console.error('Registration error:', error)
        alert('خطا در ثبت نام')
      } finally {
        loading.value = false
      }
    }
    
    return {
      loading,
      formData,
      closeModal,
      showLogin,
      handleRegister
    }
  }
}
</script>