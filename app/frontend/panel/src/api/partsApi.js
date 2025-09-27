/**
 * Central API client for parts management in admin panel.
 */

import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1'

// Create axios instance with auth interceptor
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('access_token')
      console.log('API: 401 Unauthorized - token cleared')
      // Don't redirect - let the panel handle authentication state
    }
    return Promise.reject(error)
  }
)

/**
 * Parts API functions
 */
export const partsApi = {
  // Get parts list (admin view)
  async getParts(params = {}) {
    const response = await apiClient.get('/admin/parts', { params })
    return response.data
  },

  // Get single part detail
  async getPart(partId) {
    const response = await apiClient.get(`/admin/parts/${partId}`)
    return response.data
  },

  // Create new part
  async createPart(partData) {
    const response = await apiClient.post('/admin/parts', partData)
    return response.data
  },

  // Update part
  async updatePart(partId, partData) {
    const response = await apiClient.put(`/admin/parts/${partId}`, partData)
    return response.data
  },

  // Set part price
  async setPartPrice(partId, priceData) {
    const response = await apiClient.put(`/admin/parts/${partId}/price`, priceData)
    return response.data
  },

  // Set part stock
  async setPartStock(partId, stockData) {
    const response = await apiClient.put(`/admin/parts/${partId}/stock`, stockData)
    return response.data
  },

  // Get categories
  async getCategories() {
    const response = await apiClient.get('/parts/categories')
    return response.data
  },
}

export default apiClient
