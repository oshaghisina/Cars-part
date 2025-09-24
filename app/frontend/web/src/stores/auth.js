// Authentication Store for Web Frontend
// Shared authentication state management for PDP and other web features

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { pdpApi } from '@/api/pdp.js'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref(null)
  const token = ref(localStorage.getItem('auth_token'))
  const isAuthenticated = ref(false)
  const loading = ref(false)
  const error = ref(null)

  // Computed
  const isProUser = computed(() => 
    user.value?.role === 'pro' || user.value?.role === 'fleet'
  )
  
  const isAdmin = computed(() => 
    user.value?.role === 'admin' || user.value?.role === 'operator' || user.value?.role === 'manager'
  )

  const userDisplayName = computed(() => {
    if (!user.value) return ''
    return `${user.value.first_name} ${user.value.last_name}`.trim() || user.value.username
  })

  // Actions
  const login = async (credentials) => {
    loading.value = true
    error.value = null

    try {
      const response = await pdpApi.client.post('/users/login', credentials)
      
      if (response.data && response.data.access_token) {
        user.value = response.data.user
        token.value = response.data.access_token
        isAuthenticated.value = true
        
        // Store token in localStorage
        localStorage.setItem('auth_token', token.value)
        
        // Set default authorization header for future requests
        pdpApi.client.defaults.headers.common['Authorization'] = `Bearer ${token.value}`
        
        return { success: true, user: user.value }
      } else {
        error.value = 'Invalid response from server'
        return { success: false, message: error.value }
      }
    } catch (err) {
      console.error('Login error:', err)
      error.value = err.response?.data?.detail || err.message || 'Login failed'
      return { success: false, message: error.value }
    } finally {
      loading.value = false
    }
  }

  const logout = async () => {
    loading.value = true
    error.value = null

    try {
      if (token.value) {
        await pdpApi.client.post('/users/logout', {}, {
          headers: { Authorization: `Bearer ${token.value}` }
        })
      }
    } catch (err) {
      console.error('Logout error:', err)
      // Continue with logout even if API call fails
    } finally {
      // Clear local state
      user.value = null
      token.value = null
      isAuthenticated.value = false
      
      // Remove token from localStorage
      localStorage.removeItem('auth_token')
      
      // Remove authorization header
      delete pdpApi.client.defaults.headers.common['Authorization']
      
      loading.value = false
    }
  }

  const initializeAuth = async () => {
    if (!token.value) return

    loading.value = true
    error.value = null

    try {
      // Set authorization header
      pdpApi.client.defaults.headers.common['Authorization'] = `Bearer ${token.value}`
      
      // Validate token by fetching user data
      const userData = await pdpApi.getCurrentUser()
      user.value = userData
      isAuthenticated.value = true
    } catch (err) {
      console.error('Token validation failed:', err)
      // Token is invalid, clear auth state
      await logout()
    } finally {
      loading.value = false
    }
  }

  const updateUser = async (userData) => {
    if (!isAuthenticated.value) return

    loading.value = true
    error.value = null

    try {
      const updatedUser = await pdpApi.client.put('/users/me', userData)
      user.value = { ...user.value, ...updatedUser.data }
      return { success: true, user: user.value }
    } catch (err) {
      console.error('Update user error:', err)
      error.value = err.response?.data?.detail || err.message || 'Failed to update user'
      return { success: false, message: error.value }
    } finally {
      loading.value = false
    }
  }

  const updatePreferences = async (preferences) => {
    if (!isAuthenticated.value) return

    loading.value = true
    error.value = null

    try {
      const updatedUser = await pdpApi.updateUserPreferences(preferences)
      user.value = updatedUser
      return { success: true, user: user.value }
    } catch (err) {
      console.error('Update preferences error:', err)
      error.value = err.response?.data?.detail || err.message || 'Failed to update preferences'
      return { success: false, message: error.value }
    } finally {
      loading.value = false
    }
  }

  const refreshToken = async () => {
    if (!token.value) return

    try {
      // Try to refresh the token by making a request to a protected endpoint
      await pdpApi.getCurrentUser()
    } catch (err) {
      console.error('Token refresh failed:', err)
      // Token is invalid, logout user
      await logout()
    }
  }

  const clearError = () => {
    error.value = null
  }

  // Initialize auth on store creation
  initializeAuth()

  return {
    // State
    user,
    token,
    isAuthenticated,
    loading,
    error,
    
    // Computed
    isProUser,
    isAdmin,
    userDisplayName,
    
    // Actions
    login,
    logout,
    initializeAuth,
    updateUser,
    updatePreferences,
    refreshToken,
    clearError
  }
})
