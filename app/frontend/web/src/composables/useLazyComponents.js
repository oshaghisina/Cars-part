/**
 * Vue 3 Composable for Advanced Lazy Component Loading
 * Provides utilities for lazy loading, code splitting, and performance optimization
 */

import { ref, reactive, onMounted, onUnmounted, nextTick } from 'vue'

/**
 * Main composable for lazy component management
 */
export function useLazyComponents() {
  const loadedComponents = ref(new Set())
  const loadingComponents = ref(new Set())
  const failedComponents = ref(new Set())
  const componentMetrics = reactive({})

  // Global intersection observer for all lazy components
  let globalObserver = null

  const initGlobalObserver = () => {
    if (globalObserver || !('IntersectionObserver' in window)) {
      return globalObserver
    }

    globalObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const element = entry.target
          const componentId = element.dataset.componentId
          
          if (componentId && !loadedComponents.value.has(componentId)) {
            triggerComponentLoad(componentId, element)
          }
        }
      })
    }, {
      rootMargin: '100px 0px',
      threshold: 0.1
    })

    return globalObserver
  }

  const triggerComponentLoad = async (componentId, element) => {
    if (loadingComponents.value.has(componentId)) return

    loadingComponents.value.add(componentId)
    const startTime = performance.now()

    try {
      // Emit custom event for component loading
      element.dispatchEvent(new CustomEvent('componentLoading', {
        detail: { componentId, startTime }
      }))

      // Mark as loaded (actual loading handled by parent component)
      loadedComponents.value.add(componentId)
      
      const endTime = performance.now()
      const loadTime = endTime - startTime

      // Store metrics
      componentMetrics[componentId] = {
        loadTime,
        loadedAt: new Date().toISOString(),
        element: element
      }

      // Emit loaded event
      element.dispatchEvent(new CustomEvent('componentLoaded', {
        detail: { componentId, loadTime, endTime }
      }))

      // Unobserve after loading
      globalObserver?.unobserve(element)

    } catch (error) {
      failedComponents.value.add(componentId)
      console.error(`Failed to load component ${componentId}:`, error)
      
      element.dispatchEvent(new CustomEvent('componentLoadFailed', {
        detail: { componentId, error }
      }))
    } finally {
      loadingComponents.value.delete(componentId)
    }
  }

  const observeComponent = (element, componentId) => {
    if (!element || !componentId) return

    element.dataset.componentId = componentId
    const observer = initGlobalObserver()
    
    if (observer) {
      observer.observe(element)
    } else {
      // Fallback: load immediately
      triggerComponentLoad(componentId, element)
    }
  }

  const unobserveComponent = (element) => {
    if (element && globalObserver) {
      globalObserver.unobserve(element)
    }
  }

  const cleanup = () => {
    if (globalObserver) {
      globalObserver.disconnect()
      globalObserver = null
    }
    loadedComponents.value.clear()
    loadingComponents.value.clear()
    failedComponents.value.clear()
    Object.keys(componentMetrics).forEach(key => delete componentMetrics[key])
  }

  return {
    loadedComponents,
    loadingComponents,
    failedComponents,
    componentMetrics,
    observeComponent,
    unobserveComponent,
    cleanup
  }
}

/**
 * Composable for individual lazy component
 */
export function useLazyComponent(componentId, options = {}) {
  const isVisible = ref(false)
  const isLoaded = ref(false)
  const isLoading = ref(false)
  const loadError = ref(null)
  const elementRef = ref(null)

  const {
    rootMargin = '100px 0px',
    threshold = 0.1,
    loadDelay = 0,
    retryAttempts = 0,
    onVisible = null,
    onLoaded = null,
    onError = null
  } = options

  let observer = null
  let retryCount = 0

  const load = async () => {
    if (isLoaded.value || isLoading.value) return

    isLoading.value = true
    loadError.value = null

    try {
      if (loadDelay > 0) {
        await new Promise(resolve => setTimeout(resolve, loadDelay))
      }

      // Custom loading logic can be added here
      if (onLoaded) {
        await onLoaded()
      }

      isLoaded.value = true
      
    } catch (error) {
      loadError.value = error
      
      if (onError) {
        onError(error)
      }

      // Retry logic
      if (retryCount < retryAttempts) {
        retryCount++
        console.warn(`Retrying component load (${retryCount}/${retryAttempts}):`, componentId)
        setTimeout(() => load(), 1000 * retryCount)
      }
    } finally {
      isLoading.value = false
    }
  }

  const handleIntersection = (entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting && !isVisible.value) {
        isVisible.value = true
        
        if (onVisible) {
          onVisible(entry)
        }

        load()
      }
    })
  }

  const observe = () => {
    if (!elementRef.value || !('IntersectionObserver' in window)) {
      // Fallback
      isVisible.value = true
      load()
      return
    }

    observer = new IntersectionObserver(handleIntersection, {
      rootMargin,
      threshold
    })

    observer.observe(elementRef.value)
  }

  const unobserve = () => {
    if (observer && elementRef.value) {
      observer.unobserve(elementRef.value)
      observer.disconnect()
      observer = null
    }
  }

  return {
    elementRef,
    isVisible,
    isLoaded,
    isLoading,
    loadError,
    observe,
    unobserve,
    load
  }
}

/**
 * Composable for lazy image loading with progressive enhancement
 */
export function useLazyImage(src, options = {}) {
  const imageRef = ref(null)
  const isLoaded = ref(false)
  const isLoading = ref(false)
  const loadError = ref(null)

  const {
    placeholder = null,
    loadingClass = 'loading',
    loadedClass = 'loaded',
    errorClass = 'error',
    rootMargin = '50px 0px',
    threshold = 0.01
  } = options

  const load = () => {
    if (!src || isLoaded.value || isLoading.value) return

    isLoading.value = true
    const img = new Image()

    img.onload = () => {
      isLoaded.value = true
      isLoading.value = false
      
      if (imageRef.value) {
        imageRef.value.src = src
        imageRef.value.classList.remove(loadingClass)
        imageRef.value.classList.add(loadedClass)
      }
    }

    img.onerror = (error) => {
      loadError.value = error
      isLoading.value = false
      
      if (imageRef.value) {
        imageRef.value.classList.remove(loadingClass)
        imageRef.value.classList.add(errorClass)
      }
    }

    img.src = src
  }

  const handleIntersection = (entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        load()
        if (observer) {
          observer.unobserve(entry.target)
        }
      }
    })
  }

  let observer = null

  const observe = () => {
    if (!imageRef.value || !('IntersectionObserver' in window)) {
      load()
      return
    }

    observer = new IntersectionObserver(handleIntersection, {
      rootMargin,
      threshold
    })

    observer.observe(imageRef.value)
  }

  const init = () => {
    if (imageRef.value) {
      if (placeholder) {
        imageRef.value.src = placeholder
      }
      imageRef.value.classList.add(loadingClass)
      observe()
    }
  }

  return {
    imageRef,
    isLoaded,
    isLoading,
    loadError,
    init,
    load
  }
}

/**
 * Performance monitoring utilities
 */
export function useLazyLoadingMetrics() {
  const metrics = reactive({
    totalComponents: 0,
    loadedComponents: 0,
    failedComponents: 0,
    averageLoadTime: 0,
    totalLoadTime: 0
  })

  const addMetric = (componentId, loadTime, success = true) => {
    metrics.totalComponents++
    
    if (success) {
      metrics.loadedComponents++
      metrics.totalLoadTime += loadTime
      metrics.averageLoadTime = metrics.totalLoadTime / metrics.loadedComponents
    } else {
      metrics.failedComponents++
    }
  }

  const getPerformanceReport = () => {
    return {
      ...metrics,
      successRate: metrics.totalComponents > 0 
        ? (metrics.loadedComponents / metrics.totalComponents) * 100 
        : 0,
      failureRate: metrics.totalComponents > 0 
        ? (metrics.failedComponents / metrics.totalComponents) * 100 
        : 0
    }
  }

  return {
    metrics,
    addMetric,
    getPerformanceReport
  }
}

/**
 * Preloading utilities for critical components
 */
export function useComponentPreloader() {
  const preloadedComponents = ref(new Set())

  const preloadComponent = async (importFunction, componentId) => {
    if (preloadedComponents.value.has(componentId)) {
      return Promise.resolve()
    }

    try {
      await importFunction()
      preloadedComponents.value.add(componentId)
    } catch (error) {
      console.warn(`Failed to preload component ${componentId}:`, error)
    }
  }

  const preloadComponents = async (components) => {
    const promises = components.map(({ importFunction, componentId }) =>
      preloadComponent(importFunction, componentId)
    )

    return Promise.allSettled(promises)
  }

  return {
    preloadedComponents,
    preloadComponent,
    preloadComponents
  }
}

// Default export
export default {
  useLazyComponents,
  useLazyComponent,
  useLazyImage,
  useLazyLoadingMetrics,
  useComponentPreloader
}
