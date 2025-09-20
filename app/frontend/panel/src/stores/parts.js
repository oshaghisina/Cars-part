import { defineStore } from 'pinia'
import axios from 'axios'

const API_BASE = 'http://localhost:8001/api/v1'

export const usePartsStore = defineStore('parts', {
  state: () => ({
    parts: [],
    currentPart: null,
    loading: false,
    error: null,
    pagination: {
      page: 1,
      limit: 20,
      total: 0,
      totalPages: 0
    },
    filters: {
      search: '',
      category: '',
      brand: '',
      model: '',
      trim: '',
      priceMin: '',
      priceMax: '',
      isActive: null
    }
  }),

  getters: {
    partsCount: (state) => state.parts.length,
    activeParts: (state) => state.parts.filter(part => part.is_active),
    partsByCategory: (state) => (categoryId) => state.parts.filter(part => part.category_id === categoryId),
    partsByVehicle: (state) => (brandId, modelId, trimId) => {
      return state.parts.filter(part => {
        if (brandId && part.brand_id !== brandId) return false
        if (modelId && part.model_id !== modelId) return false
        if (trimId && part.trim_id !== trimId) return false
        return true
      })
    },
    
    // Get filtered parts based on current filters
    filteredParts: (state) => {
      let filtered = state.parts
      
      if (state.filters.search) {
        const search = state.filters.search.toLowerCase()
        filtered = filtered.filter(part => 
          part.part_name.toLowerCase().includes(search) ||
          (part.brand_oem && part.brand_oem.toLowerCase().includes(search)) ||
          (part.oem_code && part.oem_code.toLowerCase().includes(search)) ||
          (part.category && part.category.toLowerCase().includes(search)) ||
          (part.subcategory && part.subcategory.toLowerCase().includes(search))
        )
      }
      
      if (state.filters.category) {
        filtered = filtered.filter(part => part.category === state.filters.category)
      }
      
      if (state.filters.brand) {
        filtered = filtered.filter(part => part.vehicle_make === state.filters.brand)
      }
      
      if (state.filters.model) {
        filtered = filtered.filter(part => part.vehicle_model === state.filters.model)
      }
      
      if (state.filters.trim) {
        filtered = filtered.filter(part => part.vehicle_trim === state.filters.trim)
      }
      
      if (state.filters.isActive !== null) {
        const activeStatus = state.filters.isActive ? 'active' : 'inactive'
        filtered = filtered.filter(part => part.status === activeStatus)
      }
      
      return filtered
    }
  },

  actions: {
    async fetchParts(params = {}) {
      this.loading = true
      this.error = null
      try {
        const queryParams = new URLSearchParams({
          skip: ((params.page || 1) - 1) * (params.limit || 20),
          limit: params.limit || 20,
          ...params
        })
        
        const response = await axios.get(`${API_BASE}/parts/?${queryParams}`)
        this.parts = response.data
        this.pagination = {
          page: params.page || 1,
          limit: params.limit || 20,
          total: response.headers['x-total-count'] || 0,
          totalPages: Math.ceil((response.headers['x-total-count'] || 0) / (params.limit || 20))
        }
      } catch (error) {
        this.error = error.response?.data?.detail || 'Failed to fetch parts'
        console.error('Error fetching parts:', error)
      } finally {
        this.loading = false
      }
    },

    async createPart(partData) {
      this.loading = true
      this.error = null
      try {
        const response = await axios.post(`${API_BASE}/parts/`, partData)
        this.parts.unshift(response.data)
        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || 'Failed to create part'
        console.error('Error creating part:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    async updatePart(id, partData) {
      this.loading = true
      this.error = null
      try {
        const response = await axios.put(`${API_BASE}/parts/${id}`, partData)
        const index = this.parts.findIndex(part => part.id === id)
        if (index !== -1) {
          this.parts[index] = response.data
        }
        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || 'Failed to update part'
        console.error('Error updating part:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    async deletePart(id) {
      this.loading = true
      this.error = null
      try {
        await axios.delete(`${API_BASE}/parts/${id}`)
        this.parts = this.parts.filter(part => part.id !== id)
        return true
      } catch (error) {
        this.error = error.response?.data?.detail || 'Failed to delete part'
        console.error('Error deleting part:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    async getPart(id) {
      this.loading = true
      this.error = null
      try {
        const response = await axios.get(`${API_BASE}/parts/${id}`)
        this.currentPart = response.data
        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || 'Failed to fetch part'
        console.error('Error fetching part:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    async searchParts(query) {
      this.loading = true
      this.error = null
      try {
        const response = await axios.get(`${API_BASE}/parts/search?q=${encodeURIComponent(query)}`)
        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || 'Failed to search parts'
        console.error('Error searching parts:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    async getPartsByCategory(categoryId) {
      this.loading = true
      this.error = null
      try {
        const response = await axios.get(`${API_BASE}/parts/?category_id=${categoryId}`)
        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || 'Failed to fetch parts by category'
        console.error('Error fetching parts by category:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    async getPartsByVehicle(brandId, modelId = null, trimId = null) {
      this.loading = true
      this.error = null
      try {
        const params = new URLSearchParams({ brand_id: brandId })
        if (modelId) params.append('model_id', modelId)
        if (trimId) params.append('trim_id', trimId)
        
        const response = await axios.get(`${API_BASE}/parts/?${params}`)
        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || 'Failed to fetch parts by vehicle'
        console.error('Error fetching parts by vehicle:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    // Filter actions
    setFilter(key, value) {
      this.filters[key] = value
      this.pagination.page = 1 // Reset to first page when filtering
    },

    setFilters(filters) {
      this.filters = { ...this.filters, ...filters }
      this.pagination.page = 1
    },

    clearFilters() {
      this.filters = {
        search: '',
        category: '',
        brand: '',
        model: '',
        trim: '',
        priceMin: '',
        priceMax: '',
        isActive: null
      }
      this.pagination.page = 1
    },

    // Pagination actions
    setPage(page) {
      this.pagination.page = page
    },

    setLimit(limit) {
      this.pagination.limit = limit
      this.pagination.page = 1
    },

    // Utility actions
    setCurrentPart(part) {
      this.currentPart = part
    },

    clearCurrentPart() {
      this.currentPart = null
    }
  }
})
