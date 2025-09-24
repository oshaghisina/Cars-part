// PDP Utility Functions
// Common utility functions for the Product Detail Page

import type { Part, CompatibilityCheck } from '@/types/pdp'

// Price formatting
export function formatPrice(price: number, currency: 'IRR' | 'USD' = 'IRR'): string {
  if (!price) return '0'
  
  if (currency === 'IRR') {
    return new Intl.NumberFormat('fa-IR').format(price)
  } else {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(price)
  }
}

// Stock status helpers
export function getStockStatus(stock: number): {
  status: 'in_stock' | 'low_stock' | 'out_of_stock' | 'backorder'
  message: string
  classes: string
} {
  if (stock === 0) {
    return {
      status: 'out_of_stock',
      message: 'ناموجود',
      classes: 'bg-red-100 text-red-800'
    }
  }
  
  if (stock <= 5) {
    return {
      status: 'low_stock',
      message: 'کم موجود',
      classes: 'bg-orange-100 text-orange-800'
    }
  }
  
  return {
    status: 'in_stock',
    message: 'موجود',
    classes: 'bg-green-100 text-green-800'
  }
}

// Compatibility status helpers
export function getCompatibilityStatus(status: CompatibilityCheck['result']): {
  message: string
  classes: string
  icon: string
} {
  switch (status) {
    case 'compatible':
      return {
        message: 'مناسب خودروی شماست',
        classes: 'bg-green-100 text-green-800',
        icon: 'check-circle'
      }
    case 'incompatible':
      return {
        message: 'مناسب خودروی شما نیست',
        classes: 'bg-red-100 text-red-800',
        icon: 'x-circle'
      }
    case 'requires_verification':
      return {
        message: 'نیاز به تأیید سازگاری',
        classes: 'bg-yellow-100 text-yellow-800',
        icon: 'exclamation-triangle'
      }
    case 'unknown':
    default:
      return {
        message: 'سازگاری نامشخص',
        classes: 'bg-gray-100 text-gray-800',
        icon: 'question-mark-circle'
      }
  }
}

// Part validation
export function validatePart(part: any): part is Part {
  return (
    part &&
    typeof part.id === 'number' &&
    typeof part.part_name === 'string' &&
    typeof part.brand_oem === 'string' &&
    typeof part.category === 'string'
  )
}

// VIN validation
export function validateVIN(vin: string): boolean {
  // Basic VIN validation (17 characters, alphanumeric, no I, O, Q)
  const vinRegex = /^[A-HJ-NPR-Z0-9]{17}$/
  return vinRegex.test(vin)
}

// Plate validation (Iranian format)
export function validatePlate(plate: string): boolean {
  // Iranian license plate format: 12-345-67 or 123-456-78
  const plateRegex = /^[0-9]{2,3}-[0-9]{3}-[0-9]{2}$/
  return plateRegex.test(plate)
}

// Image helpers
export function getImageUrl(image: any, size: 'thumbnail' | 'medium' | 'large' = 'medium'): string {
  if (!image) return ''
  
  if (size === 'thumbnail' && image.thumbnail_url) {
    return image.thumbnail_url
  }
  
  if (size === 'large' && image.large_url) {
    return image.large_url
  }
  
  return image.url || ''
}

export function getImageAlt(part: Part, imageIndex: number = 0): string {
  const baseAlt = `${part.part_name} - ${part.brand_oem}`
  const viewTypes = ['نمای اصلی', 'نمای جانبی', 'نمای پشت', 'جزئیات']
  return `${baseAlt} - ${viewTypes[imageIndex] || 'تصویر'}`
}

// SEO helpers
export function generateSEOTitle(part: Part): string {
  return `${part.part_name} - ${part.brand_oem} - ${part.vehicle_make} ${part.vehicle_model}`
}

export function generateSEODescription(part: Part): string {
  return `${part.part_name} برای ${part.vehicle_make} ${part.vehicle_model}. کد OEM: ${part.oem_code || 'نامشخص'}. کیفیت تضمین شده و قیمت مناسب.`
}

export function generateSEOKeywords(part: Part): string[] {
  const keywords = [
    part.part_name,
    part.brand_oem,
    part.vehicle_make,
    part.vehicle_model,
    part.category,
    part.oem_code
  ].filter(Boolean)
  
  if (part.subcategory) keywords.push(part.subcategory)
  if (part.position) keywords.push(part.position)
  
  return keywords
}

// URL helpers
export function generatePartUrl(part: Part): string {
  const slug = part.part_name
    .toLowerCase()
    .replace(/[^a-z0-9\u0600-\u06FF\s-]/g, '')
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
    .trim()
  
  return `/parts/${part.id}/${slug}`
}

export function generateShareUrl(part: Part): string {
  return `${window.location.origin}${generatePartUrl(part)}`
}

// Social sharing
export function generateWhatsAppShareText(part: Part): string {
  return `نگاه کنید به این قطعه: ${part.part_name} - ${part.brand_oem}`
}

export function generateTelegramShareText(part: Part): string {
  return `نگاه کنید به این قطعه: ${part.part_name} - ${part.brand_oem}`
}

// Local storage helpers
export function saveToLocalStorage(key: string, data: any): void {
  try {
    localStorage.setItem(key, JSON.stringify(data))
  } catch (error) {
    console.error('Error saving to localStorage:', error)
  }
}

export function loadFromLocalStorage<T>(key: string, defaultValue: T): T {
  try {
    const item = localStorage.getItem(key)
    return item ? JSON.parse(item) : defaultValue
  } catch (error) {
    console.error('Error loading from localStorage:', error)
    return defaultValue
  }
}

// Debounce utility
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout | null = null
  
  return (...args: Parameters<T>) => {
    if (timeout) clearTimeout(timeout)
    timeout = setTimeout(() => func(...args), wait)
  }
}

// Throttle utility
export function throttle<T extends (...args: any[]) => any>(
  func: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle: boolean
  
  return (...args: Parameters<T>) => {
    if (!inThrottle) {
      func(...args)
      inThrottle = true
      setTimeout(() => inThrottle = false, limit)
    }
  }
}

// Error handling
export function handleApiError(error: any): string {
  if (error.response?.data?.message) {
    return error.response.data.message
  }
  
  if (error.response?.data?.detail) {
    return error.response.data.detail
  }
  
  if (error.message) {
    return error.message
  }
  
  return 'خطایی رخ داده است. لطفاً دوباره تلاش کنید.'
}

// Date formatting
export function formatDate(date: string | Date, locale: 'fa' | 'en' = 'fa'): string {
  const dateObj = typeof date === 'string' ? new Date(date) : date
  
  if (locale === 'fa') {
    return new Intl.DateTimeFormat('fa-IR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    }).format(dateObj)
  }
  
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  }).format(dateObj)
}

// Quantity validation
export function validateQuantity(quantity: number, maxStock: number): {
  isValid: boolean
  message?: string
} {
  if (quantity <= 0) {
    return {
      isValid: false,
      message: 'تعداد باید بیشتر از صفر باشد'
    }
  }
  
  if (quantity > maxStock) {
    return {
      isValid: false,
      message: `تعداد نمی‌تواند بیشتر از ${maxStock} باشد`
    }
  }
  
  return { isValid: true }
}

// Part comparison helpers
export function canCompareParts(parts: Part[]): boolean {
  return parts.length >= 2 && parts.length <= 4
}

export function getComparisonFields(parts: Part[]): string[] {
  const fields = new Set<string>()
  
  parts.forEach(part => {
    Object.keys(part).forEach(key => {
      if (typeof part[key as keyof Part] === 'string' || typeof part[key as keyof Part] === 'number') {
        fields.add(key)
      }
    })
  })
  
  return Array.from(fields)
}
