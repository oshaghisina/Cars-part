<template>
  <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
    <h3 class="text-lg font-semibold text-gray-900 mb-4 font-persian-bold text-rtl">تست PDP</h3>
    
    <div class="space-y-4">
      <!-- API Status -->
      <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
        <span class="font-medium text-gray-700 font-persian text-rtl">وضعیت API:</span>
        <div class="flex items-center gap-2">
          <div :class="apiStatusClasses" class="w-3 h-3 rounded-full"></div>
          <span :class="apiStatusTextClasses" class="text-sm font-persian">{{ apiStatusMessage }}</span>
        </div>
      </div>

      <!-- Authentication Status -->
      <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
        <span class="font-medium text-gray-700 font-persian text-rtl">وضعیت احراز هویت:</span>
        <div class="flex items-center gap-2">
          <div :class="authStatusClasses" class="w-3 h-3 rounded-full"></div>
          <span :class="authStatusTextClasses" class="text-sm font-persian">{{ authStatusMessage }}</span>
        </div>
      </div>

      <!-- User Info -->
      <div v-if="isAuthenticated" class="p-3 bg-blue-50 rounded-lg">
        <h4 class="font-medium text-blue-900 mb-2 font-persian-bold text-rtl">اطلاعات کاربر:</h4>
        <div class="text-sm text-blue-800 space-y-1 font-persian text-rtl">
          <p><strong>نام:</strong> {{ userDisplayName }}</p>
          <p><strong>ایمیل:</strong> {{ user?.email }}</p>
          <p><strong>نقش:</strong> {{ user?.role }}</p>
          <p v-if="isProUser" class="text-green-600"><strong>نوع:</strong> کاربر حرفه‌ای</p>
        </div>
      </div>

      <!-- Test Actions -->
      <div class="space-y-2">
        <button
          @click="testAPI"
          :disabled="testing"
          class="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors font-persian"
        >
          {{ testing ? 'در حال تست...' : 'تست اتصال API' }}
        </button>

        <button
          @click="testAuth"
          :disabled="testing"
          class="w-full bg-green-600 text-white py-2 px-4 rounded-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors font-persian"
        >
          {{ testing ? 'در حال تست...' : 'تست احراز هویت' }}
        </button>

        <button
          @click="testPDP"
          :disabled="testing"
          class="w-full bg-purple-600 text-white py-2 px-4 rounded-lg hover:bg-purple-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors font-persian"
        >
          {{ testing ? 'در حال تست...' : 'تست PDP' }}
        </button>
      </div>

      <!-- Test Results -->
      <div v-if="testResults.length > 0" class="mt-4">
        <h4 class="font-medium text-gray-900 mb-2 font-persian-bold text-rtl">نتایج تست:</h4>
        <div class="space-y-2">
          <div
            v-for="(result, index) in testResults"
            :key="index"
            class="p-3 rounded-lg"
            :class="result.success ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'"
          >
            <div class="flex items-center gap-2">
              <div :class="result.success ? 'text-green-600' : 'text-red-600'">
                {{ result.success ? '✅' : '❌' }}
              </div>
              <span class="font-medium font-persian text-rtl">{{ result.test }}</span>
            </div>
            <p class="text-sm mt-1 font-persian text-rtl" :class="result.success ? 'text-green-700' : 'text-red-700'">
              {{ result.message }}
            </p>
            <p v-if="result.details" class="text-xs mt-1 text-gray-600 font-mono">
              {{ result.details }}
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth.js'
import { pdpApi } from '@/api/pdp.js'

export default {
  name: 'PDPTest',
  setup() {
    const authStore = useAuthStore()
    
    const apiStatus = ref('unknown')
    const testing = ref(false)
    const testResults = ref([])

    const isAuthenticated = computed(() => authStore.isAuthenticated)
    const user = computed(() => authStore.user)
    const userDisplayName = computed(() => authStore.userDisplayName)
    const isProUser = computed(() => authStore.isProUser)

    const apiStatusMessage = computed(() => {
      switch (apiStatus.value) {
        case 'connected': return 'متصل'
        case 'error': return 'خطا'
        case 'unknown': return 'نامشخص'
        default: return 'نامشخص'
      }
    })

    const apiStatusClasses = computed(() => {
      switch (apiStatus.value) {
        case 'connected': return 'bg-green-500'
        case 'error': return 'bg-red-500'
        case 'unknown': return 'bg-gray-500'
        default: return 'bg-gray-500'
      }
    })

    const apiStatusTextClasses = computed(() => {
      switch (apiStatus.value) {
        case 'connected': return 'text-green-700'
        case 'error': return 'text-red-700'
        case 'unknown': return 'text-gray-700'
        default: return 'text-gray-700'
      }
    })

    const authStatusMessage = computed(() => {
      if (isAuthenticated.value) return 'احراز هویت شده'
      return 'احراز هویت نشده'
    })

    const authStatusClasses = computed(() => {
      return isAuthenticated.value ? 'bg-green-500' : 'bg-gray-500'
    })

    const authStatusTextClasses = computed(() => {
      return isAuthenticated.value ? 'text-green-700' : 'text-gray-700'
    })

    const addTestResult = (test, success, message, details = null) => {
      testResults.value.unshift({
        test,
        success,
        message,
        details,
        timestamp: new Date().toISOString()
      })
    }

    const testAPI = async () => {
      testing.value = true
      try {
        const response = await pdpApi.healthCheck()
        apiStatus.value = 'connected'
        addTestResult('API Health Check', true, 'API در دسترس است', JSON.stringify(response))
      } catch (error) {
        apiStatus.value = 'error'
        addTestResult('API Health Check', false, 'API در دسترس نیست', error.message)
      } finally {
        testing.value = false
      }
    }

    const testAuth = async () => {
      testing.value = true
      try {
        if (isAuthenticated.value) {
          const user = await pdpApi.getCurrentUser()
          addTestResult('Authentication Test', true, 'احراز هویت موفق', `User: ${user.username}`)
        } else {
          addTestResult('Authentication Test', false, 'کاربر احراز هویت نشده', 'لطفاً ابتدا وارد شوید')
        }
      } catch (error) {
        addTestResult('Authentication Test', false, 'خطا در احراز هویت', error.message)
      } finally {
        testing.value = false
      }
    }

    const testPDP = async () => {
      testing.value = true
      try {
        // Test getting a part (using mock data for now)
        const parts = await pdpApi.getParts({ limit: 1 })
        if (parts.data && parts.data.length > 0) {
          const part = parts.data[0]
          addTestResult('PDP Data Test', true, 'دریافت اطلاعات قطعه موفق', `Part: ${part.part_name}`)
        } else {
          addTestResult('PDP Data Test', false, 'هیچ قطعه‌ای یافت نشد', 'دیتابیس خالی است')
        }
      } catch (error) {
        addTestResult('PDP Data Test', false, 'خطا در دریافت اطلاعات قطعه', error.message)
      } finally {
        testing.value = false
      }
    }

    onMounted(() => {
      testAPI()
    })

    return {
      apiStatus,
      testing,
      testResults,
      isAuthenticated,
      user,
      userDisplayName,
      isProUser,
      apiStatusMessage,
      apiStatusClasses,
      apiStatusTextClasses,
      authStatusMessage,
      authStatusClasses,
      authStatusTextClasses,
      testAPI,
      testAuth,
      testPDP
    }
  }
}
</script>
