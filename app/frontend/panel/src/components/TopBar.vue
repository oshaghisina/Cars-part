<template>
  <!-- Top Bar -->
  <header
    :class="[
      'fixed top-0 left-0 right-0 z-50 border-b border-gray-200 backdrop-blur-sm transition-all duration-300',
      isScrolled ? 'bg-white/95 shadow-lg' : 'bg-white shadow-sm',
    ]"
  >
    <div class="flex items-center justify-between h-16 px-4">
      <!-- Left Side -->
      <div class="flex items-center">
        <!-- Mobile Menu Button -->
        <button
          aria-label="Toggle mobile menu"
          aria-expanded="false"
          class="lg:hidden flex items-center justify-center w-10 h-10 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-md transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
          @click="toggleMobileMenu"
        >
          <svg
            class="w-6 h-6"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M4 6h16M4 12h16M4 18h16"
            />
          </svg>
        </button>

        <!-- Desktop Sidebar Toggle -->
        <button
          aria-label="Toggle sidebar"
          class="hidden lg:flex items-center justify-center w-10 h-10 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-md transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
          @click="toggleSidebar"
        >
          <svg
            class="w-5 h-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M4 6h16M4 12h16M4 18h16"
            />
          </svg>
        </button>

        <!-- Page Title -->
        <div class="ml-4">
          <h1 class="text-xl font-semibold text-gray-900">{{ pageTitle }}</h1>
        </div>
      </div>

      <!-- Right Side -->
      <div class="flex items-center space-x-4">
        <!-- Search (Desktop) -->
        <div class="hidden md:block">
          <div class="relative">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search..."
              aria-label="Search"
              class="w-64 px-4 py-2 pl-10 text-sm text-gray-900 bg-gray-50 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              @keyup.enter="performSearch"
            />
            <div class="absolute inset-y-0 left-0 flex items-center pl-3">
              <svg
                class="w-4 h-4 text-gray-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                />
              </svg>
            </div>
            <button
              v-if="searchQuery"
              class="absolute inset-y-0 right-0 flex items-center pr-3 text-gray-400 hover:text-gray-600"
              @click="clearSearch"
            >
              <svg
                class="w-4 h-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>
        </div>

        <!-- Quick Analytics -->
        <div class="relative">
          <button
            class="relative p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-md transition-colors"
            @click="toggleAnalyticsMenu"
          >
            <svg
              class="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
              />
            </svg>
          </button>

          <!-- Analytics Dropdown -->
          <div
            v-if="analyticsMenuOpen"
            class="absolute right-0 mt-2 w-80 bg-white rounded-lg shadow-lg z-50 border border-gray-200"
          >
            <div class="p-4">
              <div class="flex items-center justify-between mb-3">
                <h3 class="text-lg font-semibold text-gray-900">
                  Quick Analytics
                </h3>
                <button
                  class="p-1 text-gray-400 hover:text-gray-600 rounded"
                  @click="refreshAnalytics"
                >
                  <svg
                    class="w-4 h-4"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                    />
                  </svg>
                </button>
              </div>

              <!-- Key Metrics Grid -->
              <div class="grid grid-cols-2 gap-3 mb-4">
                <div class="bg-blue-50 p-3 rounded-lg">
                  <div class="text-sm text-blue-600 font-medium">
                    Total Parts
                  </div>
                  <div class="text-xl font-bold text-blue-900">
                    {{ analyticsMetrics.totalParts || 0 }}
                  </div>
                </div>
                <div class="bg-green-50 p-3 rounded-lg">
                  <div class="text-sm text-green-600 font-medium">
                    Total Orders
                  </div>
                  <div class="text-xl font-bold text-green-900">
                    {{ analyticsMetrics.totalOrders || 0 }}
                  </div>
                </div>
                <div class="bg-purple-50 p-3 rounded-lg">
                  <div class="text-sm text-purple-600 font-medium">
                    Active Users
                  </div>
                  <div class="text-xl font-bold text-purple-900">
                    {{ analyticsMetrics.activeUsers || 0 }}
                  </div>
                </div>
                <div class="bg-orange-50 p-3 rounded-lg">
                  <div class="text-sm text-orange-600 font-medium">Revenue</div>
                  <div class="text-xl font-bold text-orange-900">
                    {{ formatCurrency(analyticsMetrics.totalRevenue || 0) }}
                  </div>
                </div>
              </div>

              <!-- Quick Actions -->
              <div class="space-y-2">
                <router-link
                  to="/analytics"
                  class="flex items-center w-full px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-md transition-colors"
                  @click="analyticsMenuOpen = false"
                >
                  <svg
                    class="w-4 h-4 mr-3 text-blue-500"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                    />
                  </svg>
                  View Full Analytics
                </router-link>
                <button
                  class="flex items-center w-full px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-md transition-colors"
                  @click="exportQuickReport"
                >
                  <svg
                    class="w-4 h-4 mr-3 text-green-500"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                    />
                  </svg>
                  Export Quick Report
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Notifications -->
        <button
          class="relative p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-md transition-colors"
        >
          <svg
            class="w-5 h-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
            />
          </svg>
          <!-- Notification Badge -->
          <span
            class="absolute top-0 right-0 inline-block w-2 h-2 bg-red-500 rounded-full"
          ></span>
        </button>

        <!-- User Menu -->
        <div class="relative">
          <button
            class="flex items-center space-x-3 p-2 text-gray-700 hover:bg-gray-100 rounded-md transition-colors"
            @click="toggleUserMenu"
          >
            <div
              class="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center"
            >
              <span class="text-sm font-medium text-white">{{
                userInitials
              }}</span>
            </div>
            <div class="hidden md:block text-left">
              <p class="text-sm font-medium text-gray-900">{{ userName }}</p>
              <p class="text-xs text-gray-500">Administrator</p>
            </div>
            <svg
              class="w-4 h-4 text-gray-500"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M19 9l-7 7-7-7"
              />
            </svg>
          </button>

          <!-- User Dropdown Menu -->
          <div
            v-if="userMenuOpen"
            class="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg z-50 border border-gray-200"
          >
            <div class="py-1">
              <!-- User Info Section -->
              <div class="px-4 py-3 border-b border-gray-100">
                <div class="flex items-center">
                  <div
                    class="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center"
                  >
                    <span class="text-sm font-medium text-white">{{
                      userInitials
                    }}</span>
                  </div>
                  <div class="ml-3">
                    <p class="text-sm font-medium text-gray-900">
                      {{ userName }}
                    </p>
                    <p class="text-xs text-gray-500">{{ userEmail }}</p>
                    <p class="text-xs text-blue-600">{{ userRole }}</p>
                  </div>
                </div>
              </div>

              <!-- Profile Actions -->
              <div class="py-1">
                <router-link
                  to="/users"
                  class="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  @click="userMenuOpen = false"
                >
                  <svg
                    class="w-4 h-4 mr-3"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                    />
                  </svg>
                  View Profile
                </router-link>
                <a
                  href="#"
                  class="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                >
                  <svg
                    class="w-4 h-4 mr-3"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                    />
                  </svg>
                  Account Settings
                </a>
                <hr class="my-1" />
                <button
                  class="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  @click="logout"
                >
                  <svg
                    class="w-4 h-4 mr-3"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
                    />
                  </svg>
                  Sign out
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </header>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from "vue";
import { useRoute } from "vue-router";
import { useNavigationStore } from "@/stores/navigation";
import { useAuthStore } from "@/stores/auth";
import { useAnalyticsStore } from "@/stores/analytics";

export default {
  name: "TopBar",
  setup() {
    const route = useRoute();
    const navigationStore = useNavigationStore();
    const authStore = useAuthStore();
    const analyticsStore = useAnalyticsStore();

    // Local state
    const userMenuOpen = ref(false);
    const analyticsMenuOpen = ref(false);
    const isScrolled = ref(false);

    // Ensure authStore is properly initialized
    if (!authStore) {
      console.warn("AuthStore not properly initialized");
    }

    // Scroll detection for header enhancement
    const handleScroll = () => {
      isScrolled.value = window.scrollY > 10;
    };

    // Computed properties
    const searchQuery = computed({
      get: () => navigationStore.searchQuery,
      set: (value) => navigationStore.setSearchQuery(value),
    });

    const userName = computed(() => {
      try {
        return authStore?.user?.username || "Admin User";
      } catch (error) {
        console.warn("AuthStore not available:", error);
        return "Admin User";
      }
    });

    const userInitials = computed(() => {
      try {
        const name = userName.value;
        return name
          .split(" ")
          .map((n) => n[0])
          .join("")
          .toUpperCase()
          .slice(0, 2);
      } catch (error) {
        return "AD";
      }
    });

    const userEmail = computed(() => {
      try {
        return authStore?.user?.email || "admin@example.com";
      } catch (error) {
        console.warn("AuthStore not available for email:", error);
        return "admin@example.com";
      }
    });

    const userRole = computed(() => {
      try {
        return authStore?.user?.role || "Administrator";
      } catch (error) {
        console.warn("AuthStore not available for role:", error);
        return "Administrator";
      }
    });

    const pageTitle = computed(() => {
      const routeName = route.name;
      const titleMap = {
        Dashboard: "Dashboard",
        Parts: "Parts Management",
        Orders: "Order Management",
        Leads: "Lead Management",
        Vehicles: "Vehicle Management",
        Categories: "Category Management",
        Users: "User Management",
        Settings: "Settings",
        Analytics: "Analytics & Reports",
      };
      return titleMap[routeName] || routeName || "Dashboard";
    });

    // Analytics metrics from store
    const analyticsMetrics = computed(() => analyticsStore.dashboardMetrics);

    // Methods
    const toggleSidebar = () => navigationStore.toggleSidebar();
    const toggleMobileMenu = () => navigationStore.toggleMobileMenu();
    const performSearch = () => navigationStore.performSearch();
    const clearSearch = () => navigationStore.clearSearch();

    const toggleUserMenu = () => {
      userMenuOpen.value = !userMenuOpen.value;
    };

    const toggleAnalyticsMenu = () => {
      analyticsMenuOpen.value = !analyticsMenuOpen.value;
      if (analyticsMenuOpen.value) {
        // Fetch fresh analytics data when opening
        refreshAnalytics();
      }
    };

    const refreshAnalytics = async () => {
      try {
        await analyticsStore.fetchDashboardMetrics();
      } catch (error) {
        console.error("Failed to refresh analytics:", error);
      }
    };

    const formatCurrency = (amount) => {
      return new Intl.NumberFormat("en-US", {
        style: "currency",
        currency: "USD",
        minimumFractionDigits: 0,
        maximumFractionDigits: 0,
      }).format(amount);
    };

    const exportQuickReport = async () => {
      try {
        await analyticsStore.exportData({
          format: "csv",
          includeCharts: false,
          dateRange: "30d",
        });
        analyticsMenuOpen.value = false;
      } catch (error) {
        console.error("Failed to export quick report:", error);
      }
    };

    const logout = () => {
      try {
        if (authStore && authStore.logout) {
          authStore.logout();
        } else {
          console.warn("AuthStore logout method not available");
        }
      } catch (error) {
        console.error("Error during logout:", error);
      } finally {
        userMenuOpen.value = false;
      }
    };

    // Close menus when clicking outside
    const handleClickOutside = (event) => {
      if (!event.target.closest(".relative")) {
        userMenuOpen.value = false;
        analyticsMenuOpen.value = false;
      }
    };

    onMounted(() => {
      document.addEventListener("click", handleClickOutside);
      window.addEventListener("scroll", handleScroll);
    });

    onUnmounted(() => {
      document.removeEventListener("click", handleClickOutside);
      window.removeEventListener("scroll", handleScroll);
    });

    return {
      userMenuOpen,
      analyticsMenuOpen,
      isScrolled,
      searchQuery,
      userName,
      userInitials,
      userEmail,
      userRole,
      pageTitle,
      analyticsMetrics,
      toggleSidebar,
      toggleMobileMenu,
      performSearch,
      clearSearch,
      toggleUserMenu,
      toggleAnalyticsMenu,
      refreshAnalytics,
      formatCurrency,
      exportQuickReport,
      logout,
    };
  },
};
</script>

<style scoped>
/* Custom styles for top bar */
header {
  backdrop-filter: blur(12px);
  transition: all 0.3s ease-in-out;
}

/* Enhanced shadow for better visibility */
header {
  box-shadow:
    0 4px 6px -1px rgba(0, 0, 0, 0.1),
    0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

/* Smooth transitions */
button,
a {
  transition: all 0.2s ease-in-out;
}

/* Focus styles for accessibility */
button:focus {
  outline: 2px solid #3b82f6;
  outline-offset: 2px;
}

/* Hover effects */
.hover\:bg-gray-100:hover {
  background-color: #f3f4f6;
}

/* Dropdown animation */
.absolute {
  animation: fadeIn 0.2s ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
