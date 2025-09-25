// PDP API Client
// Connects to the existing FastAPI backend for PDP functionality

import axios from 'axios'

const API_BASE_URL = 'http://localhost:8001/api/v1'

class PDPApiClient {
  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      }
    })

    // Request interceptor for authentication
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('access_token')
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
        return config
      },
      (error) => Promise.reject(error)
    )

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Handle unauthorized access
          localStorage.removeItem('access_token')
          window.location.href = '/login'
        }
        return Promise.reject(this.handleApiError(error))
      }
    )
  }

  handleApiError(error) {
    if (error.response?.data) {
      return {
        message: error.response.data.detail || error.response.data.message || 'An error occurred',
        code: error.response.data.code || 'UNKNOWN_ERROR',
        details: error.response.data.details
      }
    }
    return {
      message: error.message || 'Network error',
      code: 'NETWORK_ERROR'
    }
  }

  // Enhanced PDP API
  async getPart(partId, options = {}) {
    const {
      includeSpecifications = true,
      includeImages = true,
      includePrices = true,
      includeAlternatives = false,
      includeCrossReferences = false,
      ...otherOptions
    } = options

    const response = await this.client.get(`/pdp/parts/${partId}`, {
      params: {
        include_specifications: includeSpecifications,
        include_images: includeImages,
        include_prices: includePrices,
        include_alternatives: includeAlternatives,
        include_cross_references: includeCrossReferences,
        ...otherOptions
      }
    })
    return response.data
  }

  async getParts(params = {}) {
    const response = await this.client.get('/parts', { params })
    return response.data
  }

  async getPartAlternatives(partId, options = {}) {
    const {
      limit = 20,
      sortBy = 'compatibility'
    } = options

    const response = await this.client.get(`/pdp/parts/${partId}/alternatives`, {
      params: { limit, sort_by: sortBy }
    })
    return response.data
  }

  async getPartCrossReferences(partId) {
    const response = await this.client.get(`/pdp/parts/${partId}/cross-references`)
    return response.data
  }

  async getPartSpecifications(partId) {
    const response = await this.client.get(`/pdp/parts/${partId}/specifications`)
    return response.data
  }

  async getPartImages(partId, imageType = null) {
    const params = imageType ? { image_type: imageType } : {}
    const response = await this.client.get(`/pdp/parts/${partId}/images`, { params })
    return response.data
  }

  async getPartPricing(partId) {
    const response = await this.client.get(`/pdp/parts/${partId}/pricing`)
    return response.data
  }

  // Enhanced Compatibility API
  async checkCompatibility(partId, vehicleInfo) {
    const response = await this.client.post(`/pdp/parts/${partId}/check-compatibility`, {
      vehicle: vehicleInfo
    })
    return response.data
  }

  // Search API
  async searchParts(searchParams = {}) {
    const {
      query,
      category,
      vehicleMake,
      vehicleModel,
      minPrice,
      maxPrice,
      page = 1,
      pageSize = 20,
      sortBy = 'relevance'
    } = searchParams

    const response = await this.client.get('/pdp/search', {
      params: {
        query,
        category,
        vehicle_make: vehicleMake,
        vehicle_model: vehicleModel,
        min_price: minPrice,
        max_price: maxPrice,
        page,
        page_size: pageSize,
        sort_by: sortBy
      }
    })
    return response.data
  }

  // Cart API
  async addToCart(partId, quantity, priceTier = 'retail') {
    const response = await this.client.post('/cart/items', {
      part_id: partId,
      quantity,
      price_tier: priceTier
    })
    return response.data
  }

  async getCart() {
    const response = await this.client.get('/cart')
    return response.data
  }

  // User API
  async getCurrentUser() {
    const response = await this.client.get('/users/me')
    return response.data
  }

  // Telegram SSO API
  async createTelegramLink(telegramId, action = 'link_account') {
    const response = await this.client.post('/telegram/link/request', {
      telegram_id: telegramId,
      action: action
    })
    return response.data
  }

  async createTelegramDeepLink(telegramId, action = 'login', targetUrl = null) {
    const response = await this.client.post('/telegram/deep-link/create', {
      telegram_id: telegramId,
      action: action,
      target_url: targetUrl
    })
    return response.data
  }

  async verifyTelegramToken(token, action = 'login') {
    const response = await this.client.post('/telegram/verify', {
      token: token,
      action: action
    })
    return response.data
  }

  async linkTelegramAccount(token) {
    const response = await this.client.post('/telegram/link/verify', {
      token: token
    })
    return response.data
  }

  async unlinkTelegramAccount() {
    const response = await this.client.delete('/telegram/link')
    return response.data
  }

  async getTelegramStats() {
    const response = await this.client.get('/telegram/stats')
    return response.data
  }

  // Health check
  async healthCheck() {
    const response = await this.client.get('/health')
    return response.data
  }
}

// Create and export a singleton instance
export const pdpApi = new PDPApiClient()
export default pdpApi