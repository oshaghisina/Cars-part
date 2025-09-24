// PDP Composable
// Provides reactive state management and data fetching for the Product Detail Page

import { ref, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { pdpApi } from '@/api/pdp.js'
import { useAuthStore } from '@/stores/auth.js'

export function usePDP() {
  const route = useRoute()
  const authStore = useAuthStore()
  
  // State
  const part = ref(null)
  const loading = ref(false)
  const error = ref(null)
  const compatibilityStatus = ref(null)
  const cart = ref([])
  const wishlist = ref([])
  const compareList = ref([])
  const savedVehicles = ref([])

  // Computed
  const user = computed(() => authStore.user)
  const isProUser = computed(() => authStore.isProUser)
  const isAuthenticated = computed(() => authStore.isAuthenticated)

  // Methods
  const loadPart = async (id, options = {}) => {
    const partId = id || route.params.id
    if (!partId) return

    loading.value = true
    error.value = null

    try {
      // Load comprehensive part data with all related information
      const partData = await pdpApi.getPart(partId, {
        includeSpecifications: true,
        includeImages: true,
        includePrices: true,
        includeAlternatives: false, // Load separately for performance
        includeCrossReferences: false, // Load separately for performance
        ...options
      })
      
      part.value = partData
      console.log('✅ Enhanced part loaded:', partData)
      
      // Load user-specific data if authenticated
      if (isAuthenticated.value) {
        await loadUserData()
      }
      
    } catch (err) {
      console.error('❌ Error loading part:', err)
      error.value = err.message || 'Failed to load part'
    } finally {
      loading.value = false
    }
  }

  const checkCompatibility = async (vehicleInfo) => {
    if (!part.value || !vehicleInfo) return

    try {
      const response = await pdpApi.checkCompatibility(part.value.id, vehicleInfo)
      compatibilityStatus.value = response
      console.log('✅ Compatibility checked:', response)
      return response
    } catch (err) {
      console.error('❌ Error checking compatibility:', err)
      compatibilityStatus.value = {
        part_id: part.value.id,
        vehicle_info: vehicleInfo,
        is_compatible: false,
        compatibility_level: 'unknown',
        confidence_score: 0,
        compatibility_notes: [err.message || 'Compatibility check failed'],
        alternative_suggestions: []
      }
      return compatibilityStatus.value
    }
  }

  const addToCart = async (quantity, priceTier = 'retail') => {
    if (!part.value) return

    try {
      const response = await pdpApi.addToCart(part.value.id, quantity, priceTier)
      cart.value = response
      console.log('Added to cart:', response)
      return { success: true, data: response }
    } catch (err) {
      console.error('Error adding to cart:', err)
      return { success: false, error: err.message || 'Failed to add to cart' }
    }
  }

  const addToQuote = async (quantity, notes) => {
    if (!part.value) return

    try {
      const response = await pdpApi.addToQuote(part.value.id, quantity, notes)
      console.log('Added to quote:', response)
      return { success: true, data: response }
    } catch (err) {
      console.error('Error adding to quote:', err)
      return { success: false, error: err.message || 'Failed to add to quote' }
    }
  }

  const toggleWishlist = async () => {
    if (!part.value) return

    try {
      const isInWishlist = wishlist.value.some(item => item.id === part.value.id)
      
      if (isInWishlist) {
        await pdpApi.removeFromWishlist(part.value.id)
        wishlist.value = wishlist.value.filter(item => item.id !== part.value.id)
      } else {
        await pdpApi.addToWishlist(part.value.id)
        wishlist.value.push(part.value)
      }
      
      console.log('Wishlist toggled:', !isInWishlist)
      return { success: true, inWishlist: !isInWishlist }
    } catch (err) {
      console.error('Error toggling wishlist:', err)
      return { success: false, error: err.message || 'Failed to toggle wishlist' }
    }
  }

  const toggleCompare = async () => {
    if (!part.value) return

    try {
      const isInCompare = compareList.value.some(item => item.id === part.value.id)
      
      if (isInCompare) {
        await pdpApi.removeFromCompare(part.value.id)
        compareList.value = compareList.value.filter(item => item.id !== part.value.id)
      } else {
        await pdpApi.addToCompare(part.value.id)
        compareList.value.push(part.value)
      }
      
      console.log('Compare toggled:', !isInCompare)
      return { success: true, inCompare: !isInCompare }
    } catch (err) {
      console.error('Error toggling compare:', err)
      return { success: false, error: err.message || 'Failed to toggle compare' }
    }
  }

  const loadUserData = async () => {
    if (!isAuthenticated.value) return

    try {
      const [cartData, wishlistData, compareData, vehiclesData] = await Promise.all([
        pdpApi.getCart(),
        pdpApi.getWishlist(),
        pdpApi.getCompareList(),
        pdpApi.getSavedVehicles()
      ])

      cart.value = cartData
      wishlist.value = wishlistData
      compareList.value = compareData
      savedVehicles.value = vehiclesData
    } catch (err) {
      console.error('Error loading user data:', err)
    }
  }

  const trackPDPView = () => {
    if (part.value) {
      // This would integrate with analytics
      console.log('PDP view tracked for:', part.value.part_name)
    }
  }

  // Watch for route changes
  watch(() => route.params.id, (newId) => {
    if (newId) {
      loadPart(newId)
    }
  }, { immediate: true })

  // Load user data when authenticated
  watch(isAuthenticated, (authenticated) => {
    if (authenticated) {
      loadUserData()
    }
  }, { immediate: true })

  return {
    // State
    part,
    loading,
    error,
    compatibilityStatus,
    cart,
    wishlist,
    compareList,
    savedVehicles,
    
    // Computed
    user,
    isProUser,
    isAuthenticated,
    
    // Methods
    loadPart,
    checkCompatibility,
    addToCart,
    addToQuote,
    toggleWishlist,
    toggleCompare,
    loadUserData,
    trackPDPView
  }
}