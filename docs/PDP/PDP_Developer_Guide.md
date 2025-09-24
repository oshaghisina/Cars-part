# Product Detail Page (PDP) - Developer Guide

## Table of Contents
- [Architecture Overview](#architecture-overview)
- [Component Structure](#component-structure)
- [State Management](#state-management)
- [API Integration](#api-integration)
- [Customization Guide](#customization-guide)
- [Performance Optimization](#performance-optimization)
- [Testing Strategy](#testing-strategy)
- [Debugging & Troubleshooting](#debugging--troubleshooting)

## Architecture Overview

### Technology Stack
- **Frontend Framework**: Vue.js 3 with Composition API
- **State Management**: Pinia
- **Styling**: Tailwind CSS
- **HTTP Client**: Axios
- **Build Tool**: Vite
- **Backend**: FastAPI
- **Database**: SQLite (dev) / PostgreSQL (prod)

### Design Patterns
- **Component-Based Architecture**: Modular, reusable components
- **Composition API**: Reactive state and logic composition
- **Store Pattern**: Centralized state management with Pinia
- **API Client Pattern**: Centralized HTTP requests
- **Event-Driven**: Component communication via events

## Component Structure

```
src/
├── views/
│   └── PartDetail.vue              # Main PDP view
├── components/
│   └── pdp/
│       ├── FitmentBar.vue          # Vehicle compatibility
│       ├── MediaGallery.vue        # Product images/videos
│       ├── TitleBlock.vue          # Product title & badges
│       ├── BuyBox.vue              # Purchase interface
│       ├── CrossReferences.vue     # OEM/Alternatives
│       ├── PDPTest.vue             # Development testing
│       └── shared/
│           ├── StockIndicator.vue  # Reusable stock status
│           └── CompatibilityStatus.vue # Reusable compatibility
├── composables/
│   ├── usePDP.js                   # PDP state & logic
│   └── useAnalytics.js             # Event tracking
├── stores/
│   └── auth.js                     # Authentication state
├── api/
│   └── pdp.js                      # API client
└── config/
    └── api.js                      # API configuration
```

### Component Hierarchy

```
PartDetail.vue
├── Breadcrumb Navigation
├── FitmentBar.vue
│   ├── VIN Input
│   ├── License Plate Input
│   ├── Manual Selection
│   └── Saved Vehicles
├── MediaGallery.vue
│   ├── Main Image Display
│   ├── Thumbnail Navigation
│   ├── Zoom Modal
│   └── 360° View
├── TitleBlock.vue
│   ├── Brand & Product Name
│   ├── SKU/MPN Display
│   ├── Badge System
│   └── Wishlist/Compare Actions
├── BuyBox.vue
│   ├── Pricing Tiers
│   ├── Stock Status
│   ├── Quantity Selector
│   ├── Delivery Estimation
│   └── Purchase Actions
├── CrossReferences.vue
│   ├── OEM References Tab
│   ├── Alternatives Tab
│   ├── Supersessions Tab
│   └── Compatibility Matrix Tab
├── Specifications Section
└── PDPTest.vue (development only)
```

## State Management

### Pinia Stores

#### Auth Store (`stores/auth.js`)
```javascript
// State
state: {
  user: null,
  token: null,
  isAuthenticated: false
}

// Getters
getters: {
  isProUser: (state) => state.user?.user_type === 'pro',
  isAdminUser: (state) => state.user?.user_type === 'admin'
}

// Actions
actions: {
  login(credentials),
  logout(),
  initializeAuth()
}
```

### Composables

#### usePDP Composable (`composables/usePDP.js`)
```javascript
// Reactive State
const part = ref(null)
const loading = ref(false)
const error = ref(null)
const compatibilityStatus = ref('unknown')
const cart = ref([])
const wishlist = ref([])
const compareList = ref([])
const savedVehicles = ref([])

// Methods
const loadPart = async (partId)
const checkCompatibility = async (vehicleData)
const addToCart = async (partId, quantity)
const toggleWishlist = async (partId)
// ... more methods
```

## API Integration

### API Client Structure (`api/pdp.js`)

```javascript
class PDPApiClient {
  constructor() {
    this.axiosInstance = axios.create({
      baseURL: API_CONFIG.BASE_URL,
      timeout: API_CONFIG.TIMEOUT,
      headers: API_CONFIG.DEFAULT_HEADERS
    })
    
    // Request interceptor for authentication
    this.axiosInstance.interceptors.request.use(config => {
      const token = localStorage.getItem('auth_token')
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
      return config
    })
  }

  // Part Management
  async getPart(partId)
  async getPartBySku(sku)
  async getPartAlternatives(partId)
  
  // Compatibility
  async checkCompatibility(partId, vehicleData)
  
  // Cart Operations
  async addToCart(partId, quantity)
  
  // User Operations
  async addToWishlist(partId)
  
  // Analytics
  async trackEvent(eventData)
}
```

### API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/parts/{id}` | GET | Get part details |
| `/api/v1/parts/{id}/alternatives` | GET | Get alternative parts |
| `/api/v1/parts/{id}/compatibility` | POST | Check compatibility |
| `/api/v1/cart` | POST | Add to cart |
| `/api/v1/wishlist` | POST | Add to wishlist |
| `/api/v1/analytics/track` | POST | Track events |

## Customization Guide

### 1. Adding New Components

Create a new component in `components/pdp/`:

```vue
<template>
  <div class="new-component">
    <!-- Component template -->
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { usePDP } from '@/composables/usePDP.js'

// Component logic
const { part } = usePDP()
const localState = ref('')

// Computed properties
const computedValue = computed(() => {
  return part.value ? processData(part.value) : null
})

// Methods
const handleAction = () => {
  // Component method
}

// Events
const emit = defineEmits(['custom-event'])
</script>
```

### 2. Customizing Existing Components

#### Modifying Buy Box Pricing
```javascript
// In BuyBox.vue, modify pricing logic
const calculatePrice = computed(() => {
  if (!props.part) return 0
  
  const basePrice = props.part.price
  const userTier = authStore.isProUser ? 'pro' : 'retail'
  const discount = getQuantityDiscount(quantity.value)
  
  // Custom pricing logic here
  return applyCustomPricing(basePrice, userTier, discount)
})
```

#### Adding Custom Badges
```javascript
// In TitleBlock.vue, extend badge system
const customBadges = computed(() => {
  const badges = []
  
  if (props.part.is_premium) {
    badges.push({ text: 'Premium', class: 'bg-gold' })
  }
  
  if (props.part.fast_shipping) {
    badges.push({ text: 'Fast Ship', class: 'bg-green' })
  }
  
  return badges
})
```

### 3. Extending API Client

```javascript
// In api/pdp.js, add new methods
class PDPApiClient {
  // ... existing methods
  
  async getCustomData(partId) {
    const response = await this.axiosInstance.get(
      ENDPOINTS.CUSTOM_DATA(partId)
    )
    return response.data
  }
  
  async submitCustomForm(formData) {
    const response = await this.axiosInstance.post(
      ENDPOINTS.CUSTOM_FORM(),
      formData
    )
    return response.data
  }
}
```

### 4. Custom Styling

#### Using Tailwind CSS
```vue
<template>
  <div class="custom-component bg-gray-50 rounded-lg p-4 shadow-md">
    <h3 class="text-lg font-semibold text-gray-800 mb-2">
      Custom Section
    </h3>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <!-- Content -->
    </div>
  </div>
</template>
```

#### Custom CSS Classes
```css
/* In assets/main.css */
.pdp-custom-section {
  @apply bg-white rounded-lg shadow-sm border border-gray-200 p-6;
}

.pdp-highlight-price {
  @apply text-2xl font-bold text-red-600;
}

.pdp-badge-premium {
  @apply bg-gradient-to-r from-yellow-400 to-yellow-600 text-white;
}
```

### 5. Adding Analytics Events

```javascript
// In composables/useAnalytics.js
export function useAnalytics() {
  const trackCustomEvent = async (eventName, eventData) => {
    try {
      await pdpApi.trackEvent({
        event_type: eventName,
        timestamp: new Date().toISOString(),
        user_id: authStore.user?.id,
        session_id: getSessionId(),
        data: eventData
      })
    } catch (error) {
      console.error('Analytics tracking failed:', error)
    }
  }
  
  return {
    trackCustomEvent,
    trackProductView: (partId) => trackCustomEvent('product_view', { partId }),
    trackCustomAction: (action, data) => trackCustomEvent(action, data)
  }
}
```

## Performance Optimization

### 1. Component Lazy Loading
```javascript
// In router/index.js
const PartDetail = () => import('@/views/PartDetail.vue')

// In components
const LazyComponent = defineAsyncComponent(() => 
  import('@/components/heavy/LazyComponent.vue')
)
```

### 2. Image Optimization
```vue
<template>
  <!-- Lazy loading with intersection observer -->
  <img 
    v-lazy="imageUrl"
    :alt="imageAlt"
    class="w-full h-auto"
    loading="lazy"
  />
  
  <!-- Responsive images -->
  <picture>
    <source 
      media="(min-width: 768px)" 
      :srcset="desktopImage"
    />
    <img 
      :src="mobileImage" 
      :alt="imageAlt"
      class="w-full h-auto"
    />
  </picture>
</template>
```

### 3. Data Fetching Optimization
```javascript
// In composables/usePDP.js
const loadPartOptimized = async (partId) => {
  loading.value = true
  
  try {
    // Parallel data fetching
    const [partData, compatibilityData, alternativesData] = await Promise.all([
      pdpApi.getPart(partId),
      pdpApi.getPartCompatibility(partId),
      pdpApi.getPartAlternatives(partId)
    ])
    
    part.value = partData
    compatibility.value = compatibilityData
    alternatives.value = alternativesData
  } catch (error) {
    handleError(error)
  } finally {
    loading.value = false
  }
}
```

## Testing Strategy

### 1. Unit Testing
```javascript
// tests/components/BuyBox.test.js
import { mount } from '@vue/test-utils'
import { createPinia } from 'pinia'
import BuyBox from '@/components/pdp/BuyBox.vue'

describe('BuyBox Component', () => {
  let wrapper
  
  beforeEach(() => {
    const pinia = createPinia()
    wrapper = mount(BuyBox, {
      global: {
        plugins: [pinia]
      },
      props: {
        part: mockPartData
      }
    })
  })
  
  it('displays correct price', () => {
    expect(wrapper.find('.price').text()).toBe('$99.99')
  })
  
  it('handles add to cart', async () => {
    await wrapper.find('.add-to-cart-btn').trigger('click')
    expect(wrapper.emitted('add-to-cart')).toBeTruthy()
  })
})
```

### 2. Integration Testing
```javascript
// tests/integration/pdp-flow.test.js
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import PartDetail from '@/views/PartDetail.vue'

describe('PDP Integration', () => {
  it('complete user flow', async () => {
    const wrapper = mount(PartDetail, {
      global: {
        plugins: [router, pinia]
      }
    })
    
    // Test compatibility check
    await wrapper.find('#vin-input').setValue('1234567890')
    await wrapper.find('#check-compatibility').trigger('click')
    
    // Test add to cart
    await wrapper.find('.add-to-cart').trigger('click')
    
    // Verify events
    expect(mockApi.checkCompatibility).toHaveBeenCalled()
    expect(mockApi.addToCart).toHaveBeenCalled()
  })
})
```

## Debugging & Troubleshooting

### 1. Development Tools

#### Enable Debug Mode
```javascript
// In config/api.js
export const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001',
  DEBUG: import.meta.env.DEV,
  TIMEOUT: 10000
}
```

#### Debug Component
```vue
<!-- PDPTest.vue for debugging -->
<template>
  <div v-if="showDebug" class="debug-panel">
    <h3>Debug Information</h3>
    <pre>{{ debugData }}</pre>
  </div>
</template>

<script setup>
const showDebug = import.meta.env.DEV
const debugData = computed(() => ({
  part: part.value,
  user: authStore.user,
  compatibility: compatibilityStatus.value
}))
</script>
```

### 2. Common Issues

#### Issue: Component Not Updating
```javascript
// Solution: Ensure reactivity
const part = ref(null) // ✅ Reactive
// const part = null    // ❌ Not reactive

// Watch for changes
watch(() => route.params.id, (newId) => {
  if (newId) {
    loadPart(newId)
  }
}, { immediate: true })
```

#### Issue: API Calls Failing
```javascript
// Solution: Add error handling
const apiCall = async () => {
  try {
    const response = await pdpApi.getPart(partId)
    return response
  } catch (error) {
    console.error('API Error:', error)
    if (error.response?.status === 401) {
      authStore.logout()
    }
    throw error
  }
}
```

#### Issue: State Not Persisting
```javascript
// Solution: Use proper state management
// In stores/auth.js
const initializeAuth = () => {
  const savedToken = localStorage.getItem('auth_token')
  const savedUser = localStorage.getItem('user_data')
  
  if (savedToken && savedUser) {
    token.value = savedToken
    user.value = JSON.parse(savedUser)
    isAuthenticated.value = true
  }
}
```

### 3. Performance Debugging

#### Bundle Analysis
```bash
# Analyze bundle size
npm run build
npx vite-bundle-analyzer dist
```

#### Performance Monitoring
```javascript
// In main.js
if (import.meta.env.DEV) {
  import('@/utils/performance-monitor.js').then(({ startMonitoring }) => {
    startMonitoring()
  })
}
```

## Best Practices

### 1. Code Organization
- Keep components small and focused
- Use composition functions for reusable logic
- Implement proper error boundaries
- Follow Vue.js style guide

### 2. Performance
- Implement lazy loading for heavy components
- Use v-memo for expensive computations
- Optimize images and assets
- Implement proper caching strategies

### 3. Accessibility
- Use semantic HTML elements
- Implement proper ARIA attributes
- Ensure keyboard navigation
- Test with screen readers

### 4. Security
- Sanitize user inputs
- Implement proper authentication
- Use HTTPS in production
- Validate API responses

---

*This developer guide provides comprehensive information for maintaining and extending the PDP. For specific implementation questions, refer to the component source code and API documentation.*
