<template>
  <!-- Sidebar Container -->
  <aside
    :class="[
      'fixed top-16 bottom-0 left-0 z-40 transition-all duration-300 ease-in-out',
      'bg-white border-r border-gray-200 shadow-lg',
      sidebarCollapsed ? 'w-16' : 'w-64',
      mobileMenuOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0',
    ]"
  >
    <!-- Sidebar Header -->
    <div
      class="flex items-center justify-between h-16 px-4 border-b border-gray-200"
    >
      <!-- Logo -->
      <div v-if="!sidebarCollapsed" class="flex items-center">
        <svg
          class="h-8 w-8 text-blue-600"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z"
          />
        </svg>
        <span class="ml-2 text-xl font-bold text-gray-900"
          >China Car Parts</span
        >
      </div>

      <!-- Collapsed Logo -->
      <div v-else class="flex items-center justify-center w-full">
        <svg
          class="h-8 w-8 text-blue-600"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z"
          />
        </svg>
      </div>

      <!-- Toggle Button (Desktop) -->
      <button
        class="hidden lg:flex items-center justify-center w-8 h-8 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-md transition-colors"
        :title="sidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'"
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
            d="M11 19l-7-7 7-7m8 14l-7-7 7-7"
          />
        </svg>
      </button>
    </div>

    <!-- Search Bar -->
    <div v-if="!sidebarCollapsed" class="p-4 border-b border-gray-200">
      <div class="relative">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search..."
          class="w-full px-4 py-2 pl-10 text-sm text-gray-900 bg-gray-50 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
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

    <!-- Navigation Menu -->
    <nav class="flex-1 px-2 py-4 space-y-1 overflow-y-auto">
      <template v-for="group in navigationGroups" :key="group.id">
        <!-- Single Item -->
        <div v-if="group.type === 'single'">
          <router-link
            :to="group.route"
            :class="[
              'group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors',
              isActiveRoute(group.route)
                ? 'bg-blue-50 text-blue-700 border-r-2 border-blue-700'
                : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900',
            ]"
            :title="sidebarCollapsed ? group.label : ''"
          >
            <svg
              class="flex-shrink-0 w-5 h-5 mr-3"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                :d="group.icon"
              />
            </svg>
            <span v-if="!sidebarCollapsed" class="truncate">{{
              group.label
            }}</span>
          </router-link>
        </div>

        <!-- Group with Items -->
        <div v-else-if="group.type === 'group'">
          <button
            :class="[
              'group w-full flex items-center justify-between px-3 py-2 text-sm font-medium rounded-md transition-colors',
              getActiveGroup === group.id
                ? 'bg-blue-50 text-blue-700'
                : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900',
            ]"
            :title="sidebarCollapsed ? group.label : ''"
            @click="toggleGroup(group.id)"
          >
            <div class="flex items-center">
              <svg
                class="flex-shrink-0 w-5 h-5 mr-3"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  :d="group.icon"
                />
              </svg>
              <span v-if="!sidebarCollapsed" class="truncate">{{
                group.label
              }}</span>
            </div>
            <svg
              v-if="!sidebarCollapsed"
              :class="[
                'w-4 h-4 transition-transform duration-200',
                group.expanded ? 'rotate-180' : '',
              ]"
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

          <!-- Group Items -->
          <div
            v-if="group.expanded && !sidebarCollapsed"
            class="mt-1 space-y-1 pl-11"
          >
            <router-link
              v-for="item in group.items"
              :key="item.id"
              :to="item.route"
              :class="[
                'group flex items-center px-3 py-2 text-sm rounded-md transition-colors',
                isActiveRoute(item.route)
                  ? 'bg-blue-50 text-blue-700 border-r-2 border-blue-700'
                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900',
              ]"
            >
              <svg
                class="flex-shrink-0 w-4 h-4 mr-3"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  :d="item.icon"
                />
              </svg>
              <span class="truncate">{{ item.label }}</span>
            </router-link>
          </div>
        </div>
      </template>
    </nav>

    <!-- User Profile Section -->
    <div class="p-4 border-t border-gray-200">
      <div v-if="!sidebarCollapsed" class="flex items-center">
        <div class="flex-shrink-0">
          <div
            class="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center"
          >
            <span class="text-sm font-medium text-white">{{
              userInitials
            }}</span>
          </div>
        </div>
        <div class="ml-3">
          <p class="text-sm font-medium text-gray-900">{{ userName }}</p>
          <p class="text-xs text-gray-500">Administrator</p>
        </div>
      </div>
      <div v-else class="flex justify-center">
        <div
          class="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center"
        >
          <span class="text-sm font-medium text-white">{{ userInitials }}</span>
        </div>
      </div>
    </div>
  </aside>

  <!-- Mobile Overlay -->
  <div
    v-if="mobileMenuOpen"
    class="fixed inset-0 z-40 bg-gray-600 bg-opacity-75 lg:hidden"
    @click="toggleMobileMenu"
  ></div>
</template>

<script>
import { computed, onMounted } from "vue";
import { useNavigationStore } from "@/stores/navigation";
import { useAuthStore } from "@/stores/auth";

export default {
  name: "Sidebar",
  setup() {
    const navigationStore = useNavigationStore();
    const authStore = useAuthStore();

    // Computed properties
    const sidebarCollapsed = computed(() => navigationStore.sidebarCollapsed);
    const mobileMenuOpen = computed(() => navigationStore.mobileMenuOpen);
    const navigationGroups = computed(() => navigationStore.navigationGroups);
    const searchQuery = computed({
      get: () => navigationStore.searchQuery,
      set: (value) => navigationStore.setSearchQuery(value),
    });
    const isActiveRoute = computed(() => navigationStore.isActiveRoute);
    const getActiveGroup = computed(() => navigationStore.getActiveGroup);

    const userName = computed(() => authStore.user?.username || "Admin User");
    const userInitials = computed(() => {
      const name = userName.value;
      return name
        .split(" ")
        .map((n) => n[0])
        .join("")
        .toUpperCase()
        .slice(0, 2);
    });

    // Methods
    const toggleSidebar = () => navigationStore.toggleSidebar();
    const toggleMobileMenu = () => navigationStore.toggleMobileMenu();
    const toggleGroup = (groupId) => navigationStore.toggleGroup(groupId);
    const performSearch = () => navigationStore.performSearch();
    const clearSearch = () => navigationStore.clearSearch();

    // Initialize navigation on mount
    onMounted(() => {
      navigationStore.initializeNavigation();
    });

    return {
      sidebarCollapsed,
      mobileMenuOpen,
      navigationGroups,
      searchQuery,
      isActiveRoute,
      getActiveGroup,
      userName,
      userInitials,
      toggleSidebar,
      toggleMobileMenu,
      toggleGroup,
      performSearch,
      clearSearch,
    };
  },
};
</script>

<style scoped>
/* Custom scrollbar for navigation */
nav::-webkit-scrollbar {
  width: 4px;
}

nav::-webkit-scrollbar-track {
  background: #f1f5f9;
}

nav::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 2px;
}

nav::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

/* Smooth transitions */
.group {
  transition: all 0.2s ease-in-out;
}

/* Focus styles for accessibility */
button:focus,
a:focus {
  outline: 2px solid #3b82f6;
  outline-offset: 2px;
}

/* Hover effects */
.group:hover .group-hover\:opacity-100 {
  opacity: 1;
}

.group:hover .group-hover\:visible {
  visibility: visible;
}
</style>
