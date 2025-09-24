// API Configuration
// Centralized configuration for API endpoints and settings

export const API_CONFIG = {
  // Base URL for API requests
  BASE_URL: 'http://localhost:8001/api/v1',
  
  // Request timeout in milliseconds
  TIMEOUT: 10000,
  
  // Default headers
  DEFAULT_HEADERS: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  },
  
  // Feature flags
  FEATURES: {
    INSTALLER: true,
    REVIEWS: true,
    VIEW_360: true,
    COMPARE: true,
    WISHLIST: true
  },
  
  // Analytics configuration
  ANALYTICS: {
    ENABLED: true,
    DEBUG: true,
    BATCH_SIZE: 10
  },
  
  // App configuration
  APP: {
    NAME: 'China Car Parts',
    VERSION: '1.0.0',
    ENV: 'development',
    DEBUG: true
  },
  
  // Localization
  LOCALE: {
    DEFAULT_CURRENCY: 'IRR',
    DEFAULT_LANGUAGE: 'fa',
    DEFAULT_LOCALE: 'fa-IR'
  }
}

// API Endpoints configuration
export const ENDPOINTS = {
  // PDP Endpoints
  PDP: {
    PART: (partId) => `/pdp/parts/${partId}`,
    PART_ALTERNATIVES: (partId) => `/pdp/parts/${partId}/alternatives`,
    PART_CROSS_REFS: (partId) => `/pdp/parts/${partId}/cross-references`,
    PART_SPECS: (partId) => `/pdp/parts/${partId}/specifications`,
    PART_IMAGES: (partId) => `/pdp/parts/${partId}/images`,
    PART_PRICING: (partId) => `/pdp/parts/${partId}/pricing`,
    CHECK_COMPATIBILITY: (partId) => `/pdp/parts/${partId}/check-compatibility`,
    SEARCH: '/pdp/search'
  },
  
  // Vehicle Enhanced Endpoints
  VEHICLES_ENHANCED: {
    BRANDS: '/vehicles-enhanced/brands',
    BRAND_MODELS: (brandId) => `/vehicles-enhanced/brands/${brandId}/models`,
    MODEL_TRIMS: (modelId) => `/vehicles-enhanced/models/${modelId}/trims`,
    SEARCH: '/vehicles-enhanced/search',
    DECODE_VIN: '/vehicles-enhanced/decode-vin',
    CHECK_COMPATIBILITY: '/vehicles-enhanced/check-compatibility',
    STATS: '/vehicles-enhanced/stats'
  },
  
  // User Endpoints
  USERS: {
    LOGIN: '/users/login',
    LOGOUT: '/users/logout',
    PROFILE: '/users/me',
    REGISTER: '/users/register'
  },
  
  // Parts Endpoints
  PARTS: {
    LIST: '/parts',
    DETAIL: (partId) => `/parts/${partId}`,
    CATEGORIES: '/categories'
  },
  
  // Cart Endpoints
  CART: {
    ADD: '/cart/add',
    UPDATE: '/cart/update',
    REMOVE: '/cart/remove',
    GET: '/cart'
  },
  
  // Analytics Endpoints
  ANALYTICS: {
    TRACK: '/analytics/track',
    EVENTS: '/analytics/events'
  }
}

// Helper function to get full API URL
export function getApiUrl(endpoint) {
  return `${API_CONFIG.BASE_URL}${endpoint}`
}

// Helper function to check if feature is enabled
export function isFeatureEnabled(feature) {
  return API_CONFIG.FEATURES[feature]
}

// Helper function to get analytics configuration
export function getAnalyticsConfig() {
  return API_CONFIG.ANALYTICS
}

// Helper function to get app configuration
export function getAppConfig() {
  return API_CONFIG.APP
}

// Helper function to get locale configuration
export function getLocaleConfig() {
  return API_CONFIG.LOCALE
}