/**
 * Centralized API Client for Admin Panel
 * Provides unified HTTP client with automatic authentication headers
 * and consistent error handling across all admin panel stores.
 */

import axios from 'axios'

import { API_BASE_URL } from './baseUrl'

class AdminApiClient {
  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      }
    })

    // Request interceptor for automatic authentication
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

    // Response interceptor for unified error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Handle unauthorized access - clear token and redirect to login
          localStorage.removeItem('access_token')
          window.location.href = '/login'
        } else if (error.response?.status === 403) {
          // Handle forbidden access - show permission error
          console.error('Permission denied:', error.response.data)
          // You might want to show a toast notification here
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
        details: error.response.data.details,
        status: error.response.status
      }
    }
    return {
      message: error.message || 'Network error',
      code: 'NETWORK_ERROR',
      status: 0
    }
  }

  // Authentication endpoints
  async login(credentials) {
    const response = await this.client.post('/users/login', credentials)
    return response.data
  }

  async logout() {
    const response = await this.client.post('/users/logout')
    return response.data
  }

  async getCurrentUser() {
    const response = await this.client.get('/users/me')
    return response.data
  }

  // User management endpoints
  async getUsers(params = {}) {
    const response = await this.client.get('/users', { params })
    return response.data
  }

  async getUser(userId) {
    const response = await this.client.get(`/users/${userId}`)
    return response.data
  }

  async createUser(userData) {
    const response = await this.client.post('/users', userData)
    return response.data
  }

  async updateUser(userId, userData) {
    const response = await this.client.put(`/users/${userId}`, userData)
    return response.data
  }

  async deleteUser(userId) {
    const response = await this.client.delete(`/users/${userId}`)
    return response.data
  }

  async generatePassword(length = 12, includeSymbols = true) {
    const response = await this.client.get('/users/utils/generate-password', {
      params: { length, include_symbols: includeSymbols }
    })
    return response.data
  }

  // Authentication configuration endpoints
  async getAuthConfig() {
    const response = await this.client.get('/auth/config')
    return response.data
  }

  async getAuthStats() {
    const response = await this.client.get('/auth/stats')
    return response.data
  }

  async getAuthLogs(params = {}) {
    const response = await this.client.get('/auth/logs', { params })
    return response.data
  }

  // Telegram SSO endpoints
  async getTelegramStats() {
    const response = await this.client.get('/telegram/stats')
    return response.data
  }

  async linkTelegramAccount(telegramId) {
    const response = await this.client.post('/telegram/link/request', {
      telegram_id: telegramId,
      action: 'link_account'
    })
    return response.data
  }

  async unlinkTelegramAccount() {
    const response = await this.client.delete('/telegram/link')
    return response.data
  }

  // Health check
  async healthCheck() {
    const response = await this.client.get('/health')
    return response.data
  }

  // Generic methods for custom endpoints
  async get(endpoint, params = {}) {
    const response = await this.client.get(endpoint, { params })
    return response.data
  }

  async post(endpoint, data = {}) {
    const response = await this.client.post(endpoint, data)
    return response.data
  }

  async put(endpoint, data = {}) {
    const response = await this.client.put(endpoint, data)
    return response.data
  }

  async delete(endpoint) {
    const response = await this.client.delete(endpoint)
    return response.data
  }
}

// Create and export singleton instance
export const adminApi = new AdminApiClient()
export default adminApi
