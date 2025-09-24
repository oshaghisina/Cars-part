<template>
  <header class="bg-white shadow-sm border-b border-gray-200">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between items-center h-16">
        <!-- Logo -->
        <div class="flex items-center">
          <router-link to="/" class="flex items-center space-x-2">
            <div class="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <span class="text-white font-bold text-lg">C</span>
            </div>
            <span class="text-xl font-bold text-gray-900 font-persian-bold">China Car Parts</span>
          </router-link>
        </div>

        <!-- Search Bar -->
        <div class="flex-1 max-w-lg mx-8 hidden md:block">
          <div class="relative">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="جستجو در قطعات..."
              class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 font-persian text-rtl"
              @keyup.enter="handleSearch"
            />
            <div class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
              <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
          </div>
        </div>

        <!-- Right Side Actions -->
        <div class="flex items-center space-x-4">
          <!-- Search Button (Mobile) -->
          <button
            @click="toggleMobileSearch"
            class="md:hidden p-2 text-gray-400 hover:text-gray-600"
          >
            <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </button>

          <!-- Compare Button -->
          <button
            @click="goToCompare"
            class="relative p-2 text-gray-400 hover:text-gray-600"
            title="مقایسه"
          >
            <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            <span v-if="compareCount > 0" class="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
              {{ compareCount }}
            </span>
          </button>

          <!-- Wishlist Button -->
          <button
            @click="goToWishlist"
            class="relative p-2 text-gray-400 hover:text-gray-600"
            title="علاقه‌مندی‌ها"
          >
            <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
            </svg>
            <span v-if="wishlistCount > 0" class="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
              {{ wishlistCount }}
            </span>
          </button>

          <!-- Cart Button -->
          <button
            @click="goToCart"
            class="relative p-2 text-gray-400 hover:text-gray-600"
            title="سبد خرید"
          >
            <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4m0 0L7 13m0 0l-2.5 5M7 13l2.5 5m6-5v6a2 2 0 11-4 0v-6m4 0V9a2 2 0 00-2-2H9a2 2 0 00-2 2v4.01" />
            </svg>
            <span v-if="cartCount > 0" class="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
              {{ cartCount }}
            </span>
          </button>

          <!-- User Menu or Login Button -->
          <div v-if="isAuthenticated">
            <UserMenu />
          </div>
          <div v-else>
            <button
              @click="showLoginModal"
              class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors font-persian"
            >
              ورود
            </button>
          </div>
        </div>
      </div>

      <!-- Mobile Search Bar -->
      <div v-if="showMobileSearch" class="md:hidden pb-4">
        <div class="relative">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="جستجو در قطعات..."
            class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 font-persian text-rtl"
            @keyup.enter="handleSearch"
          />
          <div class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
            <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
        </div>
      </div>
    </div>

    <!-- Login Modal -->
    <LoginModal
      :is-open="showLogin"
      @close="hideLoginModal"
      @show-register="showRegisterModal"
      @login-success="handleLoginSuccess"
    />
  </header>
</template>

<script>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth.js'
import UserMenu from '@/components/auth/UserMenu.vue'
import LoginModal from '@/components/auth/LoginModal.vue'

export default {
  name: 'Header',
  components: {
    UserMenu,
    LoginModal
  },
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()
    
    const searchQuery = ref('')
    const showMobileSearch = ref(false)
    const showLogin = ref(false)

    const isAuthenticated = computed(() => authStore.isAuthenticated)
    const cartCount = ref(0) // This would come from cart store
    const wishlistCount = ref(0) // This would come from wishlist store
    const compareCount = ref(0) // This would come from compare store

    const toggleMobileSearch = () => {
      showMobileSearch.value = !showMobileSearch.value
    }

    const handleSearch = () => {
      if (searchQuery.value.trim()) {
        router.push({
          name: 'search',
          query: { q: searchQuery.value }
        })
        searchQuery.value = ''
        showMobileSearch.value = false
      }
    }

    const showLoginModal = () => {
      showLogin.value = true
    }

    const hideLoginModal = () => {
      showLogin.value = false
    }

    const showRegisterModal = () => {
      // TODO: Implement register modal
      console.log('Show register modal')
    }

    const handleLoginSuccess = (user) => {
      console.log('Login successful:', user)
      hideLoginModal()
    }

    const goToCart = () => {
      router.push('/cart')
    }

    const goToWishlist = () => {
      router.push('/wishlist')
    }

    const goToCompare = () => {
      router.push('/compare')
    }

    return {
      searchQuery,
      showMobileSearch,
      showLogin,
      isAuthenticated,
      cartCount,
      wishlistCount,
      compareCount,
      toggleMobileSearch,
      handleSearch,
      showLoginModal,
      hideLoginModal,
      showRegisterModal,
      handleLoginSuccess,
      goToCart,
      goToWishlist,
      goToCompare
    }
  }
}
</script>
