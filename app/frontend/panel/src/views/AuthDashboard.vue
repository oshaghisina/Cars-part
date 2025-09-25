<template>
  <div class="auth-dashboard p-6">
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900 font-persian text-rtl">داشبورد احراز هویت</h1>
      <p class="mt-2 text-gray-600 font-persian text-rtl">مدیریت و نظارت بر سیستم احراز هویت</p>
    </div>

    <!-- Health Status Cards -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
      <div class="bg-white rounded-lg shadow-sm p-6">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
              <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
          <div class="mr-4">
            <h3 class="text-lg font-medium text-gray-900 font-persian text-rtl">وضعیت سیستم</h3>
            <p class="text-sm text-gray-500 font-persian text-rtl">{{ health.status || 'نامشخص' }}</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow-sm p-6">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
              <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
            </div>
          </div>
          <div class="mr-4">
            <h3 class="text-lg font-medium text-gray-900 font-persian text-rtl">سرویس JWT</h3>
            <p class="text-sm text-gray-500 font-persian text-rtl">{{ health.jwt_service || 'نامشخص' }}</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow-sm p-6">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
              <svg class="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
          </div>
          <div class="mr-4">
            <h3 class="text-lg font-medium text-gray-900 font-persian text-rtl">ویژگی‌های فعال</h3>
            <p class="text-sm text-gray-500 font-persian text-rtl">{{ activeFeaturesCount }} از {{ totalFeaturesCount }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Tabs -->
    <div class="bg-white rounded-lg shadow-sm">
      <div class="border-b border-gray-200">
        <nav class="-mb-px flex space-x-8" aria-label="Tabs">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            @click="activeTab = tab.id"
            :class="[
              activeTab === tab.id
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
              'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm font-persian text-rtl'
            ]"
          >
            {{ tab.name }}
          </button>
        </nav>
      </div>

      <div class="p-6">
        <!-- Configuration Tab -->
        <div v-if="activeTab === 'config'">
          <PolicyViewer />
        </div>

        <!-- Statistics Tab -->
        <div v-if="activeTab === 'stats'">
          <div class="space-y-6">
            <h3 class="text-lg font-semibold text-gray-900 font-persian text-rtl">آمار احراز هویت</h3>
            
            <div v-if="statsLoading" class="flex items-center justify-center py-8">
              <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              <span class="mr-2 text-gray-600 font-persian text-rtl">در حال بارگذاری آمار...</span>
            </div>

            <div v-else-if="statsError" class="bg-red-50 border border-red-200 rounded-md p-4">
              <div class="flex">
                <svg class="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                </svg>
                <div class="mr-3">
                  <h3 class="text-sm font-medium text-red-800 font-persian text-rtl">خطا در بارگذاری آمار</h3>
                  <p class="mt-1 text-sm text-red-700 font-persian text-rtl">{{ statsError }}</p>
                </div>
              </div>
            </div>

            <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <!-- JWT Tokens Stats -->
              <div class="bg-gray-50 rounded-lg p-4">
                <h4 class="text-sm font-medium text-gray-700 font-persian text-rtl">توکن‌های JWT</h4>
                <div class="mt-2 space-y-1">
                  <div class="flex justify-between text-sm">
                    <span class="text-gray-600 font-persian text-rtl">کل صادر شده:</span>
                    <span class="font-medium">{{ stats.jwt_tokens?.total_issued || 0 }}</span>
                  </div>
                  <div class="flex justify-between text-sm">
                    <span class="text-gray-600 font-persian text-rtl">فعال:</span>
                    <span class="font-medium text-green-600">{{ stats.jwt_tokens?.active_tokens || 0 }}</span>
                  </div>
                  <div class="flex justify-between text-sm">
                    <span class="text-gray-600 font-persian text-rtl">منقضی شده:</span>
                    <span class="font-medium text-red-600">{{ stats.jwt_tokens?.expired_tokens || 0 }}</span>
                  </div>
                </div>
              </div>

              <!-- Authentication Stats -->
              <div class="bg-gray-50 rounded-lg p-4">
                <h4 class="text-sm font-medium text-gray-700 font-persian text-rtl">احراز هویت</h4>
                <div class="mt-2 space-y-1">
                  <div class="flex justify-between text-sm">
                    <span class="text-gray-600 font-persian text-rtl">ورود موفق:</span>
                    <span class="font-medium text-green-600">{{ stats.authentication?.successful_logins || 0 }}</span>
                  </div>
                  <div class="flex justify-between text-sm">
                    <span class="text-gray-600 font-persian text-rtl">ورود ناموفق:</span>
                    <span class="font-medium text-red-600">{{ stats.authentication?.failed_logins || 0 }}</span>
                  </div>
                  <div class="flex justify-between text-sm">
                    <span class="text-gray-600 font-persian text-rtl">نرخ موفقیت:</span>
                    <span class="font-medium">{{ (stats.authentication?.success_rate || 0).toFixed(1) }}%</span>
                  </div>
                </div>
              </div>

              <!-- OTP Stats -->
              <div class="bg-gray-50 rounded-lg p-4">
                <h4 class="text-sm font-medium text-gray-700 font-persian text-rtl">OTP</h4>
                <div class="mt-2 space-y-1">
                  <div class="flex justify-between text-sm">
                    <span class="text-gray-600 font-persian text-rtl">کل درخواست‌ها:</span>
                    <span class="font-medium">{{ stats.otp?.total_requests || 0 }}</span>
                  </div>
                  <div class="flex justify-between text-sm">
                    <span class="text-gray-600 font-persian text-rtl">تایید موفق:</span>
                    <span class="font-medium text-green-600">{{ stats.otp?.successful_verifications || 0 }}</span>
                  </div>
                  <div class="flex justify-between text-sm">
                    <span class="text-gray-600 font-persian text-rtl">نرخ تحویل:</span>
                    <span class="font-medium">{{ (stats.otp?.delivery_success_rate || 0).toFixed(1) }}%</span>
                  </div>
                </div>
              </div>

              <!-- Telegram Stats -->
              <div class="bg-gray-50 rounded-lg p-4">
                <h4 class="text-sm font-medium text-gray-700 font-persian text-rtl">تلگرام</h4>
                <div class="mt-2 space-y-1">
                  <div class="flex justify-between text-sm">
                    <span class="text-gray-600 font-persian text-rtl">کل لینک‌ها:</span>
                    <span class="font-medium">{{ stats.telegram?.total_links || 0 }}</span>
                  </div>
                  <div class="flex justify-between text-sm">
                    <span class="text-gray-600 font-persian text-rtl">لینک موفق:</span>
                    <span class="font-medium text-green-600">{{ stats.telegram?.successful_links || 0 }}</span>
                  </div>
                  <div class="flex justify-between text-sm">
                    <span class="text-gray-600 font-persian text-rtl">کاربران فعال:</span>
                    <span class="font-medium">{{ stats.telegram?.active_telegram_users || 0 }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Logs Tab -->
        <div v-if="activeTab === 'logs'">
          <div class="space-y-6">
            <div class="flex items-center justify-between">
              <h3 class="text-lg font-semibold text-gray-900 font-persian text-rtl">لاگ‌های احراز هویت</h3>
              <button
                @click="loadLogs"
                :disabled="logsLoading"
                class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 transition-colors font-persian"
              >
                <div v-if="logsLoading" class="animate-spin rounded-full h-4 w-4 border-b-2 border-white inline-block mr-2"></div>
                {{ logsLoading ? 'در حال بارگذاری...' : 'بروزرسانی' }}
              </button>
            </div>

            <div v-if="logsLoading" class="flex items-center justify-center py-8">
              <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              <span class="mr-2 text-gray-600 font-persian text-rtl">در حال بارگذاری لاگ‌ها...</span>
            </div>

            <div v-else-if="logsError" class="bg-red-50 border border-red-200 rounded-md p-4">
              <div class="flex">
                <svg class="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                </svg>
                <div class="mr-3">
                  <h3 class="text-sm font-medium text-red-800 font-persian text-rtl">خطا در بارگذاری لاگ‌ها</h3>
                  <p class="mt-1 text-sm text-red-700 font-persian text-rtl">{{ logsError }}</p>
                </div>
              </div>
            </div>

            <div v-else class="bg-white border border-gray-200 rounded-lg overflow-hidden">
              <div class="overflow-x-auto">
                <table class="min-w-full divide-y divide-gray-200">
                  <thead class="bg-gray-50">
                    <tr>
                      <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider font-persian text-rtl">زمان</th>
                      <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider font-persian text-rtl">سطح</th>
                      <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider font-persian text-rtl">رویداد</th>
                      <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider font-persian text-rtl">کاربر</th>
                      <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider font-persian text-rtl">وضعیت</th>
                    </tr>
                  </thead>
                  <tbody class="bg-white divide-y divide-gray-200">
                    <tr v-for="log in logs" :key="log.timestamp" class="hover:bg-gray-50">
                      <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 font-persian text-rtl">
                        {{ formatDate(log.timestamp) }}
                      </td>
                      <td class="px-6 py-4 whitespace-nowrap">
                        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                              :class="getLogLevelClass(log.level)">
                          {{ log.level }}
                        </span>
                      </td>
                      <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 font-persian text-rtl">
                        {{ log.event }}
                      </td>
                      <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 font-persian text-rtl">
                        {{ log.username || 'نامشخص' }}
                      </td>
                      <td class="px-6 py-4 whitespace-nowrap">
                        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                              :class="log.success ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'">
                          {{ log.success ? 'موفق' : 'ناموفق' }}
                        </span>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { adminApi } from '@/api/client.js'
import PolicyViewer from '@/components/auth/PolicyViewer.vue'

export default {
  name: 'AuthDashboard',
  components: {
    PolicyViewer
  },
  setup() {
    const activeTab = ref('config')
    const health = ref({})
    const stats = ref({})
    const logs = ref([])
    const statsLoading = ref(false)
    const statsError = ref('')
    const logsLoading = ref(false)
    const logsError = ref('')

    const tabs = [
      { id: 'config', name: 'پیکربندی' },
      { id: 'stats', name: 'آمار' },
      { id: 'logs', name: 'لاگ‌ها' }
    ]

    const activeFeaturesCount = computed(() => {
      if (!health.value.features) return 0
      return Object.values(health.value.features).filter(Boolean).length
    })

    const totalFeaturesCount = computed(() => {
      if (!health.value.features) return 0
      return Object.keys(health.value.features).length
    })

    const loadHealth = async () => {
      try {
        health.value = await adminApi.get('/auth/health')
      } catch (err) {
        console.error('Error loading health:', err)
      }
    }

    const loadStats = async () => {
      statsLoading.value = true
      statsError.value = ''
      try {
        stats.value = await adminApi.getAuthStats()
      } catch (err) {
        statsError.value = err.message || 'خطا در بارگذاری آمار'
        console.error('Error loading stats:', err)
      } finally {
        statsLoading.value = false
      }
    }

    const loadLogs = async () => {
      logsLoading.value = true
      logsError.value = ''
      try {
        const response = await adminApi.getAuthLogs()
        logs.value = response.logs || []
      } catch (err) {
        logsError.value = err.message || 'خطا در بارگذاری لاگ‌ها'
        console.error('Error loading logs:', err)
      } finally {
        logsLoading.value = false
      }
    }

    const getLogLevelClass = (level) => {
      switch (level) {
        case 'ERROR':
          return 'bg-red-100 text-red-800'
        case 'WARNING':
          return 'bg-yellow-100 text-yellow-800'
        case 'INFO':
          return 'bg-blue-100 text-blue-800'
        default:
          return 'bg-gray-100 text-gray-800'
      }
    }

    const formatDate = (dateString) => {
      if (!dateString) return 'نامشخص'
      try {
        return new Date(dateString).toLocaleString('fa-IR')
      } catch {
        return dateString
      }
    }

    onMounted(() => {
      loadHealth()
    })

    return {
      activeTab,
      health,
      stats,
      logs,
      statsLoading,
      statsError,
      logsLoading,
      logsError,
      tabs,
      activeFeaturesCount,
      totalFeaturesCount,
      loadStats,
      loadLogs,
      getLogLevelClass,
      formatDate
    }
  }
}
</script>
