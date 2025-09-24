// Analytics Composable
// Provides analytics tracking functionality for the PDP

import { ref } from 'vue'
import { pdpApi } from '@/api/pdp.js'

export function useAnalytics() {
  const isEnabled = ref(true)
  const sessionId = ref(null)

  // Initialize session ID
  const initSession = () => {
    if (!sessionId.value) {
      sessionId.value = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    }
  }

  // Generic event tracking
  const track = async (eventData) => {
    if (!isEnabled.value) return

    try {
      initSession()
      
      const payload = {
        ...eventData,
        session_id: sessionId.value,
        timestamp: new Date().toISOString(),
        url: window.location.href,
        user_agent: navigator.userAgent
      }

      await pdpApi.trackEvent(payload)
      console.log('Analytics event tracked:', payload)
    } catch (error) {
      console.error('Error tracking analytics event:', error)
    }
  }

  // PDP-specific tracking methods
  const trackPDPView = (part) => {
    track({
      event_type: 'pdp_view',
      properties: {
        sku: part.oem_code || part.id,
        category: part.category,
        compatible: part.compatible,
        priceTier: part.price_tier || 'retail',
        stockStatus: part.stock_status || 'unknown'
      }
    })
  }

  const trackFitmentChange = (method, result, vehicleId, sku) => {
    track({
      event_type: 'fitment_change',
      properties: {
        method,
        result,
        vehicleId,
        sku
      }
    })
  }

  const trackAddToCart = (part, quantity, priceTier, compatible) => {
    track({
      event_type: 'add_to_cart',
      properties: {
        sku: part.oem_code || part.id,
        quantity,
        priceTier,
        compatible,
        availability: part.stock_status,
        etaType: part.eta_type || 'standard'
      }
    })
  }

  const trackBuyNow = (part, quantity, priceTier) => {
    track({
      event_type: 'buy_now',
      properties: {
        sku: part.oem_code || part.id,
        quantity,
        priceTier,
        compatible: part.compatible
      }
    })
  }

  const trackAddToQuote = (part, quantity) => {
    track({
      event_type: 'add_to_quote',
      properties: {
        sku: part.oem_code || part.id,
        quantity,
        priceTier: 'pro'
      }
    })
  }

  const trackViewCrossReference = (sku, oemRefsCount, crossRefsCount) => {
    track({
      event_type: 'view_cross_reference',
      properties: {
        sku,
        oemRefsCount,
        crossRefsCount
      }
    })
  }

  const trackViewAlternatives = (sku, reason, shown) => {
    track({
      event_type: 'view_alternatives',
      properties: {
        sku,
        reason,
        shown
      }
    })
  }

  const trackWishlistToggle = (part, action) => {
    track({
      event_type: 'wishlist_toggle',
      properties: {
        sku: part.oem_code || part.id,
        action
      }
    })
  }

  const trackCompareToggle = (part, action) => {
    track({
      event_type: 'compare_toggle',
      properties: {
        sku: part.oem_code || part.id,
        action
      }
    })
  }

  const trackMediaInteraction = (part, mediaType, action) => {
    track({
      event_type: 'media_interaction',
      properties: {
        sku: part.oem_code || part.id,
        mediaType,
        action
      }
    })
  }

  const trackSpecificationView = (part, specName) => {
    track({
      event_type: 'specification_view',
      properties: {
        sku: part.oem_code || part.id,
        specName
      }
    })
  }

  const trackReviewInteraction = (part, action, details) => {
    track({
      event_type: 'review_interaction',
      properties: {
        sku: part.oem_code || part.id,
        action,
        details
      }
    })
  }

  const trackFAQInteraction = (part, faqId, action) => {
    track({
      event_type: 'faq_interaction',
      properties: {
        sku: part.oem_code || part.id,
        faqId,
        action
      }
    })
  }

  const trackShare = (part, platform) => {
    track({
      event_type: 'share',
      properties: {
        sku: part.oem_code || part.id,
        platform
      }
    })
  }

  const trackError = (error, context, part) => {
    track({
      event_type: 'error',
      properties: {
        error,
        context,
        sku: part ? (part.oem_code || part.id) : null
      }
    })
  }

  return {
    isEnabled,
    sessionId,
    track,
    trackPDPView,
    trackFitmentChange,
    trackAddToCart,
    trackBuyNow,
    trackAddToQuote,
    trackViewCrossReference,
    trackViewAlternatives,
    trackWishlistToggle,
    trackCompareToggle,
    trackMediaInteraction,
    trackSpecificationView,
    trackReviewInteraction,
    trackFAQInteraction,
    trackShare,
    trackError
  }
}