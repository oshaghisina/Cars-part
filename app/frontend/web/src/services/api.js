// API Service for Customer Portal
// Connects to the real backend API

const API_BASE_URL = '/api/v1'

class ApiService {
  constructor() {
    this.baseURL = API_BASE_URL
  }

  // Generic request method
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    }

    try {
      const response = await fetch(url, config)
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`)
      }

      return await response.json()
    } catch (error) {
      console.error(`API request failed: ${endpoint}`, error)
      throw error
    }
  }

  // Parts API - Updated to use new public API with price and stock
  async searchParts(params = {}) {
    try {
      const queryParams = new URLSearchParams()
      
      if (params.search) queryParams.append('search', params.search)
      if (params.category) queryParams.append('category', params.category)
      if (params.category_id) queryParams.append('category_id', params.category_id)
      if (params.vehicle_make) queryParams.append('vehicle_make', params.vehicle_make)
      if (params.vehicle_model) queryParams.append('search', params.vehicle_model) // Use search for model
      if (params.limit) queryParams.append('limit', params.limit)
      if (params.skip) queryParams.append('skip', params.skip)
      if (params.status) queryParams.append('status', params.status)

      const queryString = queryParams.toString()
      const endpoint = queryString ? `/parts/?${queryString}` : '/parts/'
      
      return this.request(endpoint)
    } catch (error) {
      console.warn('Parts API not available, returning mock data:', error.message)
      // Return mock data when API is not available
      return this.getMockParts(params)
    }
  }

  async getPart(partId) {
    try {
      return await this.request(`/parts/${partId}`)
    } catch (error) {
      console.warn('Part API not available, returning mock data:', error.message)
      // Return mock data when API is not available
      return this.getMockPart(partId)
    }
  }

  async getPopularParts(limit = 8) {
    return this.searchParts({ limit, status: 'active' })
  }

  async getCategories() {
    try {
      return await this.request('/parts/categories/')
    } catch (error) {
      console.warn('Categories API not available, returning mock data:', error.message)
      return this.getMockCategories()
    }
  }

  // Leads API
  async createLead(leadData) {
    return this.request('/leads/', {
      method: 'POST',
      body: JSON.stringify({
        telegram_user_id: 'web_customer', // Placeholder for web customers
        phone_e164: leadData.phone,
        first_name: leadData.name,
        last_name: leadData.lastName || '',
        city: leadData.city || '',
        notes: leadData.description || '',
        consent: true
      })
    })
  }

  async getLead(leadId) {
    return this.request(`/leads/${leadId}`)
  }

  // Orders API
  async getOrders(params = {}) {
    const queryParams = new URLSearchParams()
    
    if (params.status) queryParams.append('status', params.status)
    if (params.limit) queryParams.append('limit', params.limit)
    if (params.skip) queryParams.append('skip', params.skip)

    const queryString = queryParams.toString()
    const endpoint = queryString ? `/orders/?${queryString}` : '/orders/'
    
    return this.request(endpoint)
  }

  async getOrder(orderId) {
    return this.request(`/orders/${orderId}`)
  }

  async trackOrder(orderNumber) {
    // For now, we'll search orders by ID or status
    // In a real implementation, you might have a specific tracking endpoint
    try {
      const orders = await this.getOrders({ limit: 100 })
      return orders.find(order => order.id.toString() === orderNumber.toString())
    } catch (error) {
      console.error('Order tracking failed:', error)
      return null
    }
  }

  // Search API
  async advancedSearch(searchData) {
    return this.request('/search/advanced', {
      method: 'POST',
      body: JSON.stringify({
        query: searchData.query,
        modules: ['parts'], // Focus on parts for customer portal
        filters: searchData.filters || {},
        page: searchData.page || 0,
        per_page: searchData.per_page || 20,
        sort_by: searchData.sort_by || 'relevance',
        sort_order: searchData.sort_order || 'desc'
      })
    })
  }

  async getSearchSuggestions(query, module = 'parts') {
    const params = new URLSearchParams({ q: query })
    if (module) params.append('module', module)
    
    return this.request(`/search/suggestions?${params}`)
  }

  // Health check
  async healthCheck() {
    return this.request('/health')
  }

  // Mock data for when API is not available
  getMockParts(params = {}) {
    const mockParts = [
      {
        id: 1,
        part_name: 'Front Brake Pads',
        brand_oem: 'Chery',
        vehicle_make: 'Chery',
        vehicle_model: 'Tiggo 8',
        vehicle_trim: 'Pro',
        oem_code: 'CH123456',
        category: 'Brake System',
        subcategory: 'Brake Pads',
        position: 'Front',
        unit: 'pcs',
        pack_size: 4,
        status: 'active',
        created_at: '2024-01-15T10:30:00Z'
      },
      {
        id: 2,
        part_name: 'Oil Filter',
        brand_oem: 'Geely',
        vehicle_make: 'Geely',
        vehicle_model: 'EC7',
        vehicle_trim: 'Comfort',
        oem_code: 'GE789012',
        category: 'Engine',
        subcategory: 'Oil Filter',
        position: 'Engine',
        unit: 'pcs',
        pack_size: 1,
        status: 'active',
        created_at: '2024-01-15T10:30:00Z'
      },
      {
        id: 3,
        part_name: 'Air Filter',
        brand_oem: 'BYD',
        vehicle_make: 'BYD',
        vehicle_model: 'F3',
        vehicle_trim: 'Standard',
        oem_code: 'BY345678',
        category: 'Engine',
        subcategory: 'Air Filter',
        position: 'Engine',
        unit: 'pcs',
        pack_size: 1,
        status: 'active',
        created_at: '2024-01-15T10:30:00Z'
      },
      {
        id: 4,
        part_name: 'Spark Plugs',
        brand_oem: 'Great Wall',
        vehicle_make: 'Great Wall',
        vehicle_model: 'Haval H6',
        vehicle_trim: 'Premium',
        oem_code: 'GW901234',
        category: 'Engine',
        subcategory: 'Spark Plugs',
        position: 'Engine',
        unit: 'pcs',
        pack_size: 4,
        status: 'active',
        created_at: '2024-01-15T10:30:00Z'
      }
    ]

    // Filter based on search parameters
    let filteredParts = mockParts

    if (params.search) {
      const searchTerm = params.search.toLowerCase()
      filteredParts = filteredParts.filter(part => 
        part.part_name.toLowerCase().includes(searchTerm) ||
        part.brand_oem.toLowerCase().includes(searchTerm) ||
        part.vehicle_model.toLowerCase().includes(searchTerm)
      )
    }

    if (params.vehicle_make) {
      filteredParts = filteredParts.filter(part => 
        part.vehicle_make.toLowerCase() === params.vehicle_make.toLowerCase()
      )
    }

    if (params.category) {
      filteredParts = filteredParts.filter(part => 
        part.category.toLowerCase() === params.category.toLowerCase()
      )
    }

    // Apply limit
    const limit = params.limit || 20
    return filteredParts.slice(0, limit)
  }

  // Utility methods
  formatPartForDisplay(part) {
    return {
      id: part.id,
      name: part.part_name,
      description: `${part.brand_oem} - ${part.oem_code || 'N/A'}`,
      price: part.price ? part.price.effective_price : this.generatePrice(part), // Use real price or mock
      stock: part.stock ? (part.stock.in_stock ? part.stock.current_stock - part.stock.reserved_quantity : 0) : this.generateStock(part), // Use real stock or mock
      inStock: part.stock ? part.stock.in_stock : (this.generateStock(part) > 0), // Use real stock status or mock
      make: part.vehicle_make,
      model: part.vehicle_model,
      year: part.vehicle_trim,
      oemCode: part.oem_code,
      category: part.category,
      subcategory: part.subcategory,
      position: part.position,
      unit: part.unit,
      packSize: part.pack_size,
      status: part.status,
      createdAt: part.created_at,
      // Include full price and stock objects for detailed views
      priceInfo: part.price,
      stockInfo: part.stock
    }
  }

  generatePrice(part) {
    // Mock price generation based on part characteristics
    const basePrice = 25 + (part.id % 100)
    const categoryMultiplier = {
      'Engine': 1.5,
      'Brake': 1.2,
      'Suspension': 1.3,
      'Electrical': 0.8,
      'Body': 1.0
    }[part.category] || 1.0
    
    return (basePrice * categoryMultiplier).toFixed(2)
  }

  generateStock(part) {
    // Mock stock generation
    return Math.floor(Math.random() * 50) + 5
  }

  getMockPart(partId) {
    // Mock single part data
    const mockPart = {
      id: parseInt(partId),
      part_name: `Mock Part ${partId}`,
      brand_oem: 'Mock Brand',
      vehicle_make: 'Mock Make',
      vehicle_model: 'Mock Model',
      vehicle_trim: null,
      category: 'Mock Category',
      subcategory: null,
      oem_code: `MOCK-${partId}`,
      position: null,
      unit: 'pcs',
      pack_size: 1,
      status: 'active',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    }
    return mockPart
  }

  getMockCategories() {
    // Mock categories data
    return [
      { id: 1, name: 'Engine', name_fa: 'موتور', name_cn: '发动机', parent_id: null, level: 0, path: '/Engine', is_active: true, sort_order: 1, created_at: new Date().toISOString(), updated_at: new Date().toISOString() },
      { id: 2, name: 'Brake System', name_fa: 'سیستم ترمز', name_cn: '制动系统', parent_id: null, level: 0, path: '/Brake System', is_active: true, sort_order: 2, created_at: new Date().toISOString(), updated_at: new Date().toISOString() },
      { id: 3, name: 'Suspension', name_fa: 'تعلیق', name_cn: '悬架', parent_id: null, level: 0, path: '/Suspension', is_active: true, sort_order: 3, created_at: new Date().toISOString(), updated_at: new Date().toISOString() }
    ]
  }

  formatOrderForDisplay(order) {
    return {
      id: order.id,
      number: order.id.toString().padStart(6, '0'),
      status: order.status,
      createdAt: order.created_at,
      updatedAt: order.updated_at,
      items: order.items || [],
      total: this.calculateOrderTotal(order.items || [])
    }
  }

  calculateOrderTotal(items) {
    return items.reduce((total, item) => {
      const price = this.generatePrice({ id: item.matched_part_id || 1 })
      return total + (parseFloat(price) * (item.qty || 1))
    }, 0).toFixed(2)
  }
}

// Create and export a singleton instance
const apiService = new ApiService()
export default apiService
