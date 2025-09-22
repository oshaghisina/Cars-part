import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'

export const useNavigationStore = defineStore('navigation', () => {
  // State
  const sidebarCollapsed = ref(false)
  const mobileMenuOpen = ref(false)
  const activeGroup = ref(null)
  const searchQuery = ref('')
  
  // Navigation structure
  const navigationGroups = ref([
    {
      id: 'dashboard',
      label: 'Dashboard',
      icon: 'M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2-2z M8 5v4h8V5',
      route: '/',
      type: 'single'
    },
    {
      id: 'inventory',
      label: 'Inventory',
      icon: 'M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4',
      type: 'group',
      expanded: false,
      items: [
        {
          id: 'vehicles',
          label: 'Vehicles',
          icon: 'M9 17a2 2 0 11-4 0 2 2 0 014 0zM19 17a2 2 0 11-4 0 2 2 0 014 0z',
          route: '/vehicles'
        },
        {
          id: 'categories',
          label: 'Categories',
          icon: 'M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10',
          route: '/categories'
        },
        {
          id: 'parts',
          label: 'Parts',
          icon: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z',
          route: '/parts'
        }
      ]
    },
    {
      id: 'sales',
      label: 'Sales & Orders',
      icon: 'M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z',
      type: 'group',
      expanded: false,
      items: [
        {
          id: 'orders',
          label: 'Orders',
          icon: 'M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2',
          route: '/orders'
        },
        {
          id: 'leads',
          label: 'Leads',
          icon: 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z',
          route: '/leads'
        }
      ]
    },
    {
      id: 'analytics',
      label: 'Analytics',
      icon: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z',
      route: '/analytics',
      type: 'single'
    },
    {
      id: 'admin',
      label: 'Administration',
      icon: 'M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z M15 12a3 3 0 11-6 0 3 3 0 016 0z',
      type: 'group',
      expanded: false,
      items: [
        {
          id: 'users',
          label: 'Users',
          icon: 'M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z',
          route: '/users'
        },
        {
          id: 'ai-dashboard',
          label: 'AI Dashboard',
          icon: 'M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z',
          route: '/ai-dashboard'
        },
        {
          id: 'ai-chat',
          label: 'AI Chat',
          icon: 'M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z',
          route: '/ai-chat'
        },
        {
          id: 'settings',
          label: 'Settings',
          icon: 'M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z M15 12a3 3 0 11-6 0 3 3 0 016 0z',
          route: '/settings'
        }
      ]
    }
  ])

  // Getters
  const isActiveRoute = computed(() => {
    const route = useRoute()
    return (routePath) => route.path === routePath
  })

  const getActiveGroup = computed(() => {
    const route = useRoute()
    for (const group of navigationGroups.value) {
      if (group.type === 'single' && group.route === route.path) {
        return group.id
      }
      if (group.type === 'group') {
        for (const item of group.items) {
          if (item.route === route.path) {
            return group.id
          }
        }
      }
    }
    return null
  })

  // Actions
  const toggleSidebar = () => {
    sidebarCollapsed.value = !sidebarCollapsed.value
    // Save to localStorage
    localStorage.setItem('sidebarCollapsed', sidebarCollapsed.value.toString())
  }

  const toggleMobileMenu = () => {
    mobileMenuOpen.value = !mobileMenuOpen.value
  }

  const toggleGroup = (groupId) => {
    const group = navigationGroups.value.find(g => g.id === groupId)
    if (group) {
      group.expanded = !group.expanded
    }
  }

  const setSearchQuery = (query) => {
    searchQuery.value = query
  }

  const performSearch = () => {
    const router = useRouter()
    if (searchQuery.value.trim()) {
      // Implement search functionality
      router.push({ path: '/search', query: { q: searchQuery.value } })
    }
  }

  const clearSearch = () => {
    searchQuery.value = ''
  }

  // Initialize from localStorage
  const initializeNavigation = () => {
    const saved = localStorage.getItem('sidebarCollapsed')
    if (saved !== null) {
      sidebarCollapsed.value = saved === 'true'
    }
  }

  return {
    // State
    sidebarCollapsed,
    mobileMenuOpen,
    activeGroup,
    searchQuery,
    navigationGroups,
    
    // Getters
    isActiveRoute,
    getActiveGroup,
    
    // Actions
    toggleSidebar,
    toggleMobileMenu,
    toggleGroup,
    setSearchQuery,
    performSearch,
    clearSearch,
    initializeNavigation
  }
})
