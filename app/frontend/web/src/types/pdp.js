// PDP TypeScript Types
// Based on the existing API structure and PDP requirements

export interface Part {
  id: number
  part_name: string
  brand_oem: string
  vehicle_make: string
  vehicle_model: string
  vehicle_trim?: string
  oem_code?: string
  category: string
  subcategory?: string
  position?: string
  unit: string
  pack_size?: number
  status: string
  created_at: string
  updated_at: string
  
  // PDP-specific fields (will be added to API)
  description?: string
  price?: number
  stock?: number
  lead_time_days?: number
  warranty?: string
  origin?: string
  material?: string
  is_oem?: boolean
  is_best_seller?: boolean
  is_new?: boolean
  is_authorized?: boolean
  savings_pct?: number
  pro_net_price?: number
  moq?: number
  images?: PartImage[]
  videos?: PartVideo[]
  specifications?: PartSpecification[]
  oem_references?: OEMReference[]
  alternatives?: Part[]
  reviews?: PartReview[]
  faqs?: FAQ[]
}

export interface PartImage {
  id: number
  url: string
  thumbnail_url?: string
  alt: string
  is_primary: boolean
  sort_order: number
}

export interface PartVideo {
  id: number
  url: string
  thumbnail_url?: string
  title: string
  duration?: number
  sort_order: number
}

export interface PartSpecification {
  name: string
  value: string
  unit?: string
  category?: string
}

export interface OEMReference {
  brand: string
  code: string
  description?: string
}

export interface PartReview {
  id: number
  user_name: string
  rating: number
  title: string
  comment: string
  is_verified_purchase: boolean
  created_at: string
  helpful_count: number
}

export interface FAQ {
  id: number
  question: string
  answer: string
  category?: string
  sort_order: number
}

// Compatibility types
export interface CompatibilityCheck {
  method: 'vin' | 'plate' | 'manual'
  result: 'compatible' | 'incompatible' | 'requires_verification' | 'unknown'
  vehicle_id?: string
  confidence?: number
  notes?: string
}

export interface Vehicle {
  id: string
  make: string
  model: string
  year: number
  trim?: string
  display_name: string
}

// Cart and Order types
export interface CartItem {
  part: Part
  quantity: number
  price_tier: 'retail' | 'pro'
  added_at: string
}

export interface QuoteItem {
  part: Part
  quantity: number
  notes?: string
  added_at: string
}

// User types
export interface User {
  id: number
  username: string
  email: string
  role: 'guest' | 'registered' | 'pro' | 'fleet' | 'admin' | 'operator' | 'manager'
  is_authenticated: boolean
  preferences?: UserPreferences
}

export interface UserPreferences {
  saved_vehicles: Vehicle[]
  wishlist: number[] // Part IDs
  compare_list: number[] // Part IDs
  language: 'en' | 'fa'
  currency: 'IRR' | 'USD'
}

// API Response types
export interface APIResponse<T> {
  data: T
  success: boolean
  message?: string
  errors?: string[]
}

export interface PaginatedResponse<T> {
  data: T[]
  total: number
  page: number
  limit: number
  has_next: boolean
  has_prev: boolean
}

// Analytics types
export interface AnalyticsEvent {
  event_type: string
  properties: Record<string, any>
  timestamp: string
  user_id?: number
  session_id?: string
}

// PDP-specific analytics events
export interface PDPViewEvent extends AnalyticsEvent {
  event_type: 'pdp_view'
  properties: {
    sku: string
    category: string
    compatible: boolean
    price_tier: 'retail' | 'pro'
    stock_status: 'in_stock' | 'low_stock' | 'out_of_stock' | 'backorder'
  }
}

export interface FitmentChangeEvent extends AnalyticsEvent {
  event_type: 'fitment_change'
  properties: {
    method: 'vin' | 'plate' | 'manual'
    result: 'compatible' | 'incompatible' | 'requires_verification' | 'unknown'
    vehicle_id?: string
  }
}

export interface AddToCartEvent extends AnalyticsEvent {
  event_type: 'add_to_cart'
  properties: {
    sku: string
    qty: number
    price_tier: 'retail' | 'pro'
    availability: {
      stock_status: string
      available_qty: number
    }
    compatible: boolean
  }
}

export interface BuyNowEvent extends AnalyticsEvent {
  event_type: 'buy_now'
  properties: {
    sku: string
    qty: number
    price_tier: 'retail' | 'pro'
  }
}

export interface AddToQuoteEvent extends AnalyticsEvent {
  event_type: 'add_to_quote'
  properties: {
    sku: string
    qty: number
    price_tier: 'pro'
  }
}

export interface ViewCrossReferenceEvent extends AnalyticsEvent {
  event_type: 'view_cross_reference'
  properties: {
    sku: string
    oem_refs_count: number
    cross_refs_count: number
  }
}

export interface ViewAlternativesEvent extends AnalyticsEvent {
  event_type: 'view_alternatives'
  properties: {
    sku: string
    reason: 'oos' | 'incompatible' | 'backorder'
    shown: number
  }
}

// Error types
export interface APIError {
  message: string
  code: string
  details?: Record<string, any>
}

export interface ValidationError extends APIError {
  code: 'VALIDATION_ERROR'
  details: {
    field: string
    message: string
  }[]
}

// Search and filter types
export interface PartSearchParams {
  query?: string
  category?: string
  vehicle_make?: string
  vehicle_model?: string
  price_min?: number
  price_max?: number
  in_stock?: boolean
  is_oem?: boolean
  sort_by?: 'name' | 'price' | 'created_at' | 'popularity'
  sort_order?: 'asc' | 'desc'
  page?: number
  limit?: number
}

export interface PartFilters {
  categories: string[]
  vehicle_makes: string[]
  price_ranges: { min: number; max: number }[]
  availability: ('in_stock' | 'low_stock' | 'out_of_stock' | 'backorder')[]
  features: ('oem' | 'best_seller' | 'new' | 'authorized')[]
}
