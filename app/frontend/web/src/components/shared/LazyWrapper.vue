<template>
  <div ref="containerRef" class="lazy-wrapper">
    <!-- Loading Skeleton -->
    <div 
      v-if="!isVisible" 
      :class="[
        'animate-pulse bg-gray-200 rounded-lg',
        skeletonClasses
      ]"
      :style="{ height: skeletonHeight }"
    >
      <div v-if="showSkeletonContent" class="p-6 space-y-4">
        <!-- Skeleton Title -->
        <div class="h-6 bg-gray-300 rounded w-1/3"></div>
        
        <!-- Skeleton Content Lines -->
        <div class="space-y-3">
          <div class="h-4 bg-gray-300 rounded w-full"></div>
          <div class="h-4 bg-gray-300 rounded w-3/4"></div>
          <div class="h-4 bg-gray-300 rounded w-1/2"></div>
        </div>
        
        <!-- Skeleton Actions -->
        <div class="flex space-x-3 pt-4">
          <div class="h-8 w-20 bg-gray-300 rounded"></div>
          <div class="h-8 w-20 bg-gray-300 rounded"></div>
        </div>
      </div>
    </div>
    
    <!-- Actual Content (Lazy Loaded) -->
    <div v-if="isVisible" class="lazy-content">
      <slot />
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'

export default {
  name: 'LazyWrapper',
  props: {
    // Intersection observer options
    rootMargin: {
      type: String,
      default: '100px 0px'
    },
    threshold: {
      type: Number,
      default: 0.1
    },
    // Skeleton appearance
    skeletonHeight: {
      type: String,
      default: '300px'
    },
    skeletonClasses: {
      type: String,
      default: ''
    },
    showSkeletonContent: {
      type: Boolean,
      default: true
    },
    // Performance options
    unobserveAfterLoad: {
      type: Boolean,
      default: true
    },
    // Custom loading delay
    loadDelay: {
      type: Number,
      default: 0
    }
  },
  emits: ['visible', 'loaded'],
  setup(props, { emit }) {
    const containerRef = ref(null)
    const isVisible = ref(false)
    const observer = ref(null)
    const loadTimeout = ref(null)

    const handleIntersection = (entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting && !isVisible.value) {
          emit('visible', entry)
          
          if (props.loadDelay > 0) {
            loadTimeout.value = setTimeout(() => {
              loadComponent()
            }, props.loadDelay)
          } else {
            loadComponent()
          }
        }
      })
    }

    const loadComponent = () => {
      isVisible.value = true
      emit('loaded')
      
      if (props.unobserveAfterLoad && observer.value && containerRef.value) {
        observer.value.unobserve(containerRef.value)
      }
    }

    const initObserver = () => {
      if (!('IntersectionObserver' in window)) {
        // Fallback for browsers without IntersectionObserver
        loadComponent()
        return
      }

      observer.value = new IntersectionObserver(handleIntersection, {
        rootMargin: props.rootMargin,
        threshold: props.threshold
      })

      if (containerRef.value) {
        observer.value.observe(containerRef.value)
      }
    }

    onMounted(() => {
      initObserver()
    })

    onUnmounted(() => {
      if (observer.value) {
        observer.value.disconnect()
      }
      if (loadTimeout.value) {
        clearTimeout(loadTimeout.value)
      }
    })

    return {
      containerRef,
      isVisible
    }
  }
}
</script>

<style scoped>
.lazy-wrapper {
  transition: opacity 0.3s ease-in-out;
}

.lazy-content {
  animation: fadeIn 0.5s ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Loading skeleton styles */
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
</style>
