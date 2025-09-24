/**
 * Lazy Loading Utilities for Image Optimization
 * Provides intersection observer-based lazy loading for better performance
 */

// Global lazy loading observer instance
let globalObserver = null
const observedElements = new WeakSet()

/**
 * Initialize global intersection observer for lazy loading
 */
const initGlobalObserver = () => {
  if (globalObserver || !('IntersectionObserver' in window)) {
    return globalObserver
  }

  globalObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const element = entry.target
        
        // Handle different types of lazy loading
        if (element.hasAttribute('data-src')) {
          // Image lazy loading
          const dataSrc = element.getAttribute('data-src')
          element.src = dataSrc
          element.removeAttribute('data-src')
          element.classList.add('lazy-loaded')
        }
        
        if (element.hasAttribute('data-bg')) {
          // Background image lazy loading
          const dataBg = element.getAttribute('data-bg')
          element.style.backgroundImage = `url(${dataBg})`
          element.removeAttribute('data-bg')
          element.classList.add('lazy-loaded')
        }
        
        // Trigger custom event for additional handling
        element.dispatchEvent(new CustomEvent('lazyLoaded', {
          detail: { element }
        }))
        
        globalObserver.unobserve(element)
        observedElements.delete(element)
      }
    })
  }, {
    rootMargin: '50px 0px',
    threshold: 0.01
  })

  return globalObserver
}

/**
 * Add element to lazy loading observation
 * @param {HTMLElement} element - Element to observe
 * @param {Object} options - Configuration options
 */
export const observeElement = (element, options = {}) => {
  if (!element || observedElements.has(element)) {
    return
  }

  const observer = initGlobalObserver()
  if (!observer) {
    // Fallback for browsers without IntersectionObserver
    fallbackLoad(element)
    return
  }

  // Apply lazy loading class for styling
  element.classList.add('lazy-loading')
  
  observer.observe(element)
  observedElements.add(element)
}

/**
 * Remove element from lazy loading observation
 * @param {HTMLElement} element - Element to unobserve
 */
export const unobserveElement = (element) => {
  if (!element || !globalObserver) {
    return
  }

  globalObserver.unobserve(element)
  observedElements.delete(element)
}

/**
 * Fallback loading for browsers without IntersectionObserver
 * @param {HTMLElement} element - Element to load
 */
const fallbackLoad = (element) => {
  if (element.hasAttribute('data-src')) {
    element.src = element.getAttribute('data-src')
    element.removeAttribute('data-src')
  }
  
  if (element.hasAttribute('data-bg')) {
    element.style.backgroundImage = `url(${element.getAttribute('data-bg')})`
    element.removeAttribute('data-bg')
  }
  
  element.classList.add('lazy-loaded')
}

/**
 * Lazy load all images in a container
 * @param {HTMLElement} container - Container element
 * @param {string} selector - Image selector (default: 'img[data-src], [data-bg]')
 */
export const lazyLoadContainer = (container, selector = 'img[data-src], [data-bg]') => {
  if (!container) return

  const elements = container.querySelectorAll(selector)
  elements.forEach(element => {
    observeElement(element)
  })
}

/**
 * Preload images for better user experience
 * @param {Array<string>} urls - Array of image URLs to preload
 * @param {Object} options - Preload options
 */
export const preloadImages = (urls, options = {}) => {
  const { 
    priority = 'low',
    crossOrigin = null,
    onLoad = null,
    onError = null 
  } = options

  return Promise.allSettled(
    urls.map(url => {
      return new Promise((resolve, reject) => {
        const link = document.createElement('link')
        link.rel = 'prefetch'
        link.href = url
        
        if (crossOrigin) {
          link.crossOrigin = crossOrigin
        }
        
        link.onload = () => {
          if (onLoad) onLoad(url)
          resolve(url)
        }
        
        link.onerror = (error) => {
          if (onError) onError(url, error)
          reject(new Error(`Failed to preload: ${url}`))
        }
        
        document.head.appendChild(link)
        
        // Clean up after a delay
        setTimeout(() => {
          if (link.parentNode) {
            link.parentNode.removeChild(link)
          }
        }, 5000)
      })
    })
  )
}

/**
 * Create optimized image URLs with parameters
 * @param {string} baseUrl - Base image URL
 * @param {Object} options - Optimization options
 */
export const getOptimizedImageUrl = (baseUrl, options = {}) => {
  if (!baseUrl || baseUrl.startsWith('data:') || baseUrl.startsWith('blob:')) {
    return baseUrl
  }

  const {
    width,
    height,
    quality = 85,
    format = 'auto',
    dpr = 1,
    fit = 'contain',
    optimize = true
  } = options

  // In production, replace this with your CDN/image service
  // Examples: Cloudinary, ImageKit, AWS CloudFront, etc.
  const params = new URLSearchParams()
  
  if (width) params.append('w', width * dpr)
  if (height) params.append('h', height * dpr)
  if (quality && optimize) params.append('q', quality)
  if (format !== 'auto') params.append('f', format)
  if (fit) params.append('fit', fit)
  if (optimize) params.append('auto', 'compress,format')
  
  const separator = baseUrl.includes('?') ? '&' : '?'
  return params.toString() ? `${baseUrl}${separator}${params}` : baseUrl
}

/**
 * Generate responsive srcset for images
 * @param {string} baseUrl - Base image URL
 * @param {Array<Object>} sizes - Array of size configurations
 */
export const generateSrcSet = (baseUrl, sizes = null) => {
  if (!baseUrl || baseUrl.startsWith('data:')) {
    return ''
  }

  const defaultSizes = [
    { width: 400, descriptor: '400w' },
    { width: 800, descriptor: '800w' },
    { width: 1200, descriptor: '1200w' },
    { width: 1600, descriptor: '1600w' }
  ]

  const sizesToUse = sizes || defaultSizes

  return sizesToUse
    .map(size => {
      const url = getOptimizedImageUrl(baseUrl, { 
        width: size.width, 
        quality: 85 
      })
      return `${url} ${size.descriptor}`
    })
    .join(', ')
}

/**
 * Check if image format is supported by browser
 * @param {string} format - Image format (webp, avif, etc.)
 */
export const isFormatSupported = (format) => {
  if (!('createImageBitmap' in window)) {
    return false
  }

  const testImages = {
    webp: 'data:image/webp;base64,UklGRiIAAABXRUJQVlA4IBYAAAAwAQCdASoBAAEADsD+JaQAA3AAAAAA',
    avif: 'data:image/avif;base64,AAAAIGZ0eXBhdmlmAAAAAGF2aWZtaWYxbWlhZk1BMUIAAADybWV0YQAAAAAAAAAoaGRscgAAAAAAAAAAcGljdAAAAAAAAAAAAAAAAGxpYmF2aWYAAAAADnBpdG0AAAAAAAEAAAAeaWxvYwAAAABEAAABAAEAAAABAAABGgAAABcAAAAoaWluZgAAAAAAAQAAABppbmZlAgAAAAABAABhdjAxQ29sb3IAAAAAamlwcnAAAABLaXBjbwAAABRpc3BlAAAAAAAAAAEAAAABAAAAEHBpeGkAAAAAAwgICAAAAAxhdjFDgQ0MAAAAABNjb2xybmNseAACAAIAAYAAAAAXaXBtYQAAAAAAAAABAAEEAQKDBAAAACNtZGF0EgAKCBgABogQEAwgMg=='
  }

  const testImage = testImages[format.toLowerCase()]
  if (!testImage) return false

  try {
    return createImageBitmap(fetch(testImage).then(r => r.blob()))
      .then(() => true)
      .catch(() => false)
  } catch {
    return false
  }
}

/**
 * Cleanup global observer and resources
 */
export const cleanup = () => {
  if (globalObserver) {
    globalObserver.disconnect()
    globalObserver = null
  }
  observedElements.clear && observedElements.clear()
}

/**
 * Vue 3 Composable for lazy loading
 */
export const useLazyLoading = () => {
  const observedElements = ref(new Set())

  const observe = (element) => {
    if (element && !observedElements.value.has(element)) {
      observeElement(element)
      observedElements.value.add(element)
    }
  }

  const unobserve = (element) => {
    if (element && observedElements.value.has(element)) {
      unobserveElement(element)
      observedElements.value.delete(element)
    }
  }

  const cleanupAll = () => {
    observedElements.value.forEach(element => {
      unobserveElement(element)
    })
    observedElements.value.clear()
  }

  return {
    observe,
    unobserve,
    cleanup: cleanupAll,
    preloadImages,
    getOptimizedImageUrl,
    generateSrcSet,
    isFormatSupported
  }
}

// Default export
export default {
  observeElement,
  unobserveElement,
  lazyLoadContainer,
  preloadImages,
  getOptimizedImageUrl,
  generateSrcSet,
  isFormatSupported,
  useLazyLoading,
  cleanup
}
