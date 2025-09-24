<template>
  <div class="relative">
    <!-- User Menu Button -->
    <button
      @click="toggleMenu"
      class="flex items-center space-x-2 text-gray-700 hover:text-gray-900 transition-colors"
    >
      <div class="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-white text-sm font-medium">
        {{ userInitials }}
      </div>
      <span class="hidden sm:block font-persian text-rtl">{{ userDisplayName }}</span>
      <svg class="w-4 h-4" :class="{ 'rotate-180': isMenuOpen }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
      </svg>
    </button>

    <!-- Dropdown Menu -->
    <div
      v-if="isMenuOpen"
      class="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-50 border border-gray-200"
    >
      <!-- User Info -->
      <div class="px-4 py-2 border-b border-gray-100">
        <p class="text-sm font-medium text-gray-900 font-persian text-rtl">{{ userDisplayName }}</p>
        <p class="text-xs text-gray-500 font-persian text-rtl">{{ user?.email }}</p>
        <div v-if="isProUser" class="mt-1">
          <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800 font-persian">
            کاربر حرفه‌ای
          </span>
        </div>
      </div>

      <!-- Menu Items -->
      <router-link
        to="/profile"
        class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 font-persian text-rtl"
        @click="closeMenu"
      >
        پروفایل من
      </router-link>
      
      <router-link
        to="/orders"
        class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 font-persian text-rtl"
        @click="closeMenu"
      >
        سفارشات من
      </router-link>
      
      <router-link
        to="/wishlist"
        class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 font-persian text-rtl"
        @click="closeMenu"
      >
        علاقه‌مندی‌ها
      </router-link>
      
      <router-link
        to="/compare"
        class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 font-persian text-rtl"
        @click="closeMenu"
      >
        مقایسه
      </router-link>

      <div v-if="isProUser" class="border-t border-gray-100">
        <router-link
          to="/quotes"
          class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 font-persian text-rtl"
          @click="closeMenu"
        >
          پیش‌فاکتورها
        </router-link>
        
        <router-link
          to="/fleet-management"
          class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 font-persian text-rtl"
          @click="closeMenu"
        >
          مدیریت ناوگان
        </router-link>
      </div>

      <div class="border-t border-gray-100">
        <button
          @click="handleLogout"
          class="block w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 font-persian text-rtl"
        >
          خروج
        </button>
      </div>
    </div>

    <!-- Backdrop -->
    <div
      v-if="isMenuOpen"
      class="fixed inset-0 z-40"
      @click="closeMenu"
    ></div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth.js'

export default {
  name: 'UserMenu',
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()
    
    const isMenuOpen = ref(false)

    const user = computed(() => authStore.user)
    const userDisplayName = computed(() => authStore.userDisplayName)
    const isProUser = computed(() => authStore.isProUser)

    const userInitials = computed(() => {
      if (!user.value) return '?'
      const firstName = user.value.first_name || ''
      const lastName = user.value.last_name || ''
      return (firstName.charAt(0) + lastName.charAt(0)).toUpperCase() || user.value.username.charAt(0).toUpperCase()
    })

    const toggleMenu = () => {
      isMenuOpen.value = !isMenuOpen.value
    }

    const closeMenu = () => {
      isMenuOpen.value = false
    }

    const handleLogout = async () => {
      await authStore.logout()
      closeMenu()
      router.push('/')
    }

    return {
      isMenuOpen,
      user,
      userDisplayName,
      isProUser,
      userInitials,
      toggleMenu,
      closeMenu,
      handleLogout
    }
  }
}
</script>
