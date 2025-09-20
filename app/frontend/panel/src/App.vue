<template>
  <div id="app" class="min-h-screen bg-gray-50">
    <!-- Login Modal -->
    <LoginModal 
      :show="!authStore.isAuthenticated" 
      @close="handleLoginClose" 
    />
    
    <!-- Main App Content (only show when authenticated) -->
    <div v-if="authStore.isAuthenticated">
      <!-- Sidebar -->
      <Sidebar />
      
      <!-- Main Content Area -->
      <div class="lg:pl-64">
        <!-- Top Bar -->
        <TopBar />
        
        <!-- Page Content -->
        <main class="pt-20 py-6">
          <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <router-view />
          </div>
        </main>
      </div>
    </div>
  </div>
</template>

<script>
import { onMounted } from 'vue'
import Sidebar from './components/Sidebar.vue'
import TopBar from './components/TopBar.vue'
import LoginModal from './components/LoginModal.vue'
import { useAuthStore } from './stores/auth'
import { useNavigationStore } from './stores/navigation'

export default {
  name: 'App',
  components: {
    Sidebar,
    TopBar,
    LoginModal
  },
  setup() {
    const authStore = useAuthStore()
    const navigationStore = useNavigationStore()
    
    onMounted(() => {
      // Initialize auth state
      authStore.initializeAuth()
      
      // Initialize navigation state
      navigationStore.initializeNavigation()
    })

    const handleLoginClose = () => {
      // Login modal closed - no action needed as it's controlled by isAuthenticated
    }
    
    return {
      authStore,
      handleLoginClose
    }
  }
}
</script>

<style>
/* Global styles */
body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* Smooth transitions for layout changes */
#app {
  transition: all 0.3s ease-in-out;
}

/* Custom scrollbar for main content */
main {
  scrollbar-width: thin;
  scrollbar-color: #cbd5e1 #f1f5f9;
}

main::-webkit-scrollbar {
  width: 6px;
}

main::-webkit-scrollbar-track {
  background: #f1f5f9;
}

main::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

main::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

/* Focus styles for accessibility */
*:focus {
  outline: 2px solid #3b82f6;
  outline-offset: 2px;
}

/* Remove focus outline for mouse users */
*:focus:not(:focus-visible) {
  outline: none;
}

/* Ensure proper spacing for fixed elements */
.lg\:pl-64 {
  padding-left: 16rem;
}

@media (max-width: 1023px) {
  .lg\:pl-64 {
    padding-left: 0;
  }
}
</style>
