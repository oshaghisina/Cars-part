<template>
  <div class="space-y-4">
    <!-- Main Image -->
    <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div class="aspect-square bg-gray-100 rounded-lg mb-4 flex items-center justify-center relative overflow-hidden">
        <!-- Optimized Main Image with Progressive Loading -->
        <div v-if="currentImage" class="relative w-full h-full">
          <!-- Low Quality Placeholder (LQIP) -->
          <img
            v-if="currentImage.lqip && !mainImageLoaded"
            :src="currentImage.lqip"
            :alt="currentImage.alt"
            class="absolute inset-0 w-full h-full object-contain blur-sm transition-opacity duration-300"
            :class="{ 'opacity-0': mainImageLoaded }"
          />
          
          <!-- Main Optimized Image with Responsive Sizes -->
          <picture>
            <!-- WebP format for modern browsers -->
            <source
              v-if="currentImage.webp"
              :srcset="generateSrcSet(currentImage.webp)"
              sizes="(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 400px"
              type="image/webp"
            />
            <!-- AVIF format for ultra-modern browsers -->
            <source
              v-if="currentImage.avif"
              :srcset="generateSrcSet(currentImage.avif)"
              sizes="(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 400px"
              type="image/avif"
            />
            <!-- Fallback JPEG/PNG -->
            <img
              ref="mainImageRef"
              :src="getOptimizedImageUrl(currentImage.url, { width: 800, quality: 85 })"
              :srcset="generateSrcSet(currentImage.url)"
              :alt="currentImage.alt"
              class="w-full h-full object-contain transition-opacity duration-300"
              :class="{ 'opacity-0': !mainImageLoaded }"
              sizes="(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 400px"
              loading="eager"
              @load="handleMainImageLoad"
              @error="handleImageError"
            />
          </picture>
          
          <!-- Loading Skeleton -->
          <div 
            v-if="!mainImageLoaded"
            class="absolute inset-0 bg-gray-200 animate-pulse rounded-lg flex items-center justify-center"
          >
            <svg class="w-12 h-12 text-gray-400 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          </div>
        </div>
        
        <div v-else class="text-center">
          <span class="text-8xl">🔧</span>
          <p class="text-gray-500 font-persian mt-2">تصویر در دسترس نیست</p>
        </div>
        
        <!-- Zoom Button -->
        <button
          v-if="currentImage && mainImageLoaded"
          @click="openZoomModal"
          class="absolute top-4 right-4 bg-white bg-opacity-90 hover:bg-opacity-100 rounded-full p-2 shadow-md transition-all z-10"
        >
          <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7" />
          </svg>
        </button>
        
        <!-- Image Format Indicator (Dev Mode) -->
        <div 
          v-if="import.meta.env.DEV && currentImage && mainImageLoaded"
          class="absolute bottom-4 left-4 bg-black bg-opacity-75 text-white text-xs px-2 py-1 rounded"
        >
          {{ getImageFormat(currentImage) }}
        </div>
      </div>
      
      <!-- Optimized Thumbnail Navigation -->
      <div class="grid grid-cols-4 gap-2">
        <button
          v-for="(image, index) in images"
          :key="index"
          @click="selectImage(index)"
          :class="[
            'aspect-square rounded cursor-pointer hover:ring-2 hover:ring-blue-500 transition-all relative overflow-hidden',
            currentImageIndex === index ? 'ring-2 ring-blue-500' : 'ring-1 ring-gray-200'
          ]"
        >
          <div v-if="image.url" class="relative w-full h-full">
            <!-- Thumbnail Loading Skeleton -->
            <div 
              v-if="!thumbnailsLoaded.has(index)"
              class="absolute inset-0 bg-gray-200 animate-pulse rounded flex items-center justify-center"
            >
              <svg class="w-4 h-4 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z" clip-rule="evenodd" />
              </svg>
            </div>
            
            <!-- Optimized Thumbnail with Lazy Loading -->
            <picture>
              <source
                v-if="image.webp"
                :srcset="getOptimizedImageUrl(image.webp.thumbnail, { width: 150, quality: 75 })"
                type="image/webp"
              />
              <img
                :data-src="getOptimizedImageUrl(image.thumbnailUrl || image.url, { width: 150, quality: 75 })"
                :alt="image.alt"
                class="w-full h-full object-cover rounded transition-opacity duration-300 lazy-image"
                :class="{ 'opacity-100': thumbnailsLoaded.has(index), 'opacity-0': !thumbnailsLoaded.has(index) }"
                @load="handleThumbnailLoad(index)"
                @error="handleThumbnailError(index)"
              />
            </picture>
          </div>
          <div v-else class="w-full h-full bg-gray-200 rounded flex items-center justify-center">
            <span class="text-2xl">🔧</span>
          </div>
        </button>
      </div>
    </div>

    <!-- Video Section (if available) -->
    <div v-if="videos.length > 0" class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h3 class="text-lg font-semibold text-gray-900 mb-4 font-persian-bold text-rtl">ویدیوهای مرتبط</h3>
      <div class="space-y-4">
        <div
          v-for="(video, index) in videos"
          :key="index"
          class="relative aspect-video bg-gray-100 rounded-lg overflow-hidden"
        >
          <video
            :src="video.url"
            :poster="video.thumbnailUrl"
            controls
            class="w-full h-full object-cover"
          >
            مرورگر شما از پخش ویدیو پشتیبانی نمی‌کند.
          </video>
        </div>
      </div>
    </div>

    <!-- 360° View (if available) -->
    <div v-if="has360View" class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h3 class="text-lg font-semibold text-gray-900 mb-4 font-persian-bold text-rtl">نمای 360 درجه</h3>
      <div class="aspect-square bg-gray-100 rounded-lg relative overflow-hidden cursor-grab" 
           :class="{ 'cursor-grabbing': isDragging360 }"
           @mousedown="start360Drag"
           @mousemove="handle360Drag"
           @mouseup="end360Drag"
           @mouseleave="end360Drag">
        <img
          v-if="view360Images.length > 0"
          :src="view360Images[current360Index]"
          :alt="`نمای 360 درجه - فریم ${current360Index + 1}`"
          class="w-full h-full object-contain select-none"
          draggable="false"
        />
        <div v-else class="flex items-center justify-center h-full text-center">
          <div>
            <span class="text-6xl mb-2">🔄</span>
            <p class="text-gray-500 font-persian">نمای 360 درجه در دسترس نیست</p>
          </div>
        </div>
        
        <!-- 360° Controls -->
        <div v-if="view360Images.length > 0" class="absolute bottom-4 left-1/2 transform -translate-x-1/2">
          <div class="bg-black bg-opacity-60 text-white px-3 py-1 rounded-full text-sm font-persian">
            {{ current360Index + 1 }} / {{ view360Images.length }}
          </div>
        </div>
        
        <!-- Auto-rotation toggle -->
        <button
          v-if="view360Images.length > 0"
          @click="toggleAutoRotation"
          class="absolute top-4 left-4 bg-white bg-opacity-90 hover:bg-opacity-100 rounded-full p-2 shadow-md transition-all"
          :class="{ 'bg-blue-500 text-white': isAutoRotating }"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Enhanced Zoom Modal -->
    <div
      v-if="showZoomModal"
      class="fixed inset-0 bg-black bg-opacity-90 flex items-center justify-center z-50"
      @click="closeZoomModal"
    >
      <div class="relative w-full h-full flex items-center justify-center p-4" @click.stop>
        <!-- Close Button -->
        <button
          @click="closeZoomModal"
          class="absolute top-4 right-4 text-white hover:text-gray-300 z-20 bg-black bg-opacity-50 rounded-full p-2"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
        
        <!-- Zoom Controls -->
        <div class="absolute top-4 left-4 flex flex-col space-y-2 z-20">
          <button
            @click="zoomIn"
            class="bg-black bg-opacity-50 text-white rounded-full p-2 hover:bg-opacity-75 transition-all"
            title="Zoom In"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
          </button>
          <button
            @click="zoomOut"
            class="bg-black bg-opacity-50 text-white rounded-full p-2 hover:bg-opacity-75 transition-all"
            title="Zoom Out"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 12H6" />
            </svg>
          </button>
          <button
            @click="resetZoom"
            class="bg-black bg-opacity-50 text-white rounded-full p-2 hover:bg-opacity-75 transition-all"
            title="Reset Zoom"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </button>
        </div>
        
        <!-- Navigation Arrows -->
        <button
          v-if="currentImageIndex > 0"
          @click="selectImage(currentImageIndex - 1)"
          class="absolute left-4 top-1/2 transform -translate-y-1/2 bg-black bg-opacity-50 text-white rounded-full p-3 hover:bg-opacity-75 transition-all z-20"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
        </button>
        
        <button
          v-if="currentImageIndex < images.length - 1"
          @click="selectImage(currentImageIndex + 1)"
          class="absolute right-4 top-1/2 transform -translate-y-1/2 bg-black bg-opacity-50 text-white rounded-full p-3 hover:bg-opacity-75 transition-all z-20"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
        </button>
        
        <!-- Image Container with Pan and Zoom -->
        <div class="relative w-full h-full flex items-center justify-center overflow-hidden">
          <img
            v-if="currentImage"
            :src="currentImage.url"
            :alt="currentImage.alt"
            class="max-w-none transition-transform duration-200 select-none"
            :style="{ 
              transform: `scale(${zoomLevel}) translate(${panX}px, ${panY}px)`,
              cursor: zoomLevel > 1 ? 'grab' : 'zoom-in'
            }"
            :class="{ 'cursor-grabbing': isPanning }"
            @mousedown="startPan"
            @mousemove="handlePan" 
            @mouseup="endPan"
            @mouseleave="endPan"
            @click="zoomLevel === 1 ? zoomIn() : null"
            draggable="false"
          />
        </div>
        
        <!-- Image Info -->
        <div class="absolute bottom-4 left-1/2 transform -translate-x-1/2 bg-black bg-opacity-50 text-white px-4 py-2 rounded-lg text-sm font-persian">
          {{ currentImageIndex + 1 }} / {{ images.length }} - {{ currentImage?.alt }}
        </div>
        
        <!-- Zoom Level Indicator -->
        <div 
          v-if="zoomLevel !== 1"
          class="absolute bottom-4 right-4 bg-black bg-opacity-50 text-white px-3 py-1 rounded-lg text-sm"
        >
          {{ Math.round(zoomLevel * 100) }}%
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'

export default {
  name: 'MediaGallery',
  props: {
    part: {
      type: Object,
      required: true
    }
  },
  setup(props) {
    const currentImageIndex = ref(0)
    const showZoomModal = ref(false)
    const imageErrors = ref(new Set())
    const mainImageRef = ref(null)
    
    // Image loading states
    const mainImageLoaded = ref(false)
    const thumbnailsLoaded = ref(new Set())
    const intersectionObserver = ref(null)
    
    // 360° view state
    const current360Index = ref(0)
    const isDragging360 = ref(false)
    const isAutoRotating = ref(false)
    const lastMouseX = ref(0)
    const autoRotationInterval = ref(null)

    // Images from API data or fallback to placeholders
    const images = ref([])
    
    // Initialize images from part data
    const initializeImages = () => {
      if (props.part?.images && props.part.images.length > 0) {
        // Use real images from API
        images.value = props.part.images.map(img => ({
          id: img.id,
          url: img.url,
          thumbnailUrl: img.thumbnails?.small || img.url,
          alt: img.alt_text || `${props.part?.name || 'قطعه'} - ${img.type}`,
          type: img.image_type,
          sort_order: img.sort_order,
          // Enhanced optimization data
          webp: img.thumbnails?.webp || null,
          avif: img.thumbnails?.avif || null,
          lqip: generateLQIP(), // Generate placeholder for progressive loading
          sizes: {
            thumbnail: img.thumbnails?.thumbnail,
            small: img.thumbnails?.small,
            medium: img.thumbnails?.medium,
            large: img.thumbnails?.large,
            xlarge: img.thumbnails?.xlarge
          }
        })).sort((a, b) => a.sort_order - b.sort_order)
      } else {
        // Fallback to placeholder images
        images.value = [
          {
            url: 'https://via.placeholder.com/800x600/E74C3C/FFFFFF?text=Main+View', 
            thumbnailUrl: 'https://via.placeholder.com/150x150/E74C3C/FFFFFF?text=Main',
            alt: `${props.part?.name || 'قطعه'} - نمای اصلی`,
            type: 'main',
            sort_order: 0,
            lqip: generateLQIP()
          },
          {
            url: 'https://via.placeholder.com/800x600/3498DB/FFFFFF?text=Side+View',
            thumbnailUrl: 'https://via.placeholder.com/150x150/3498DB/FFFFFF?text=Side',
            alt: `${props.part?.name || 'قطعه'} - نمای جانبی`,
            type: 'detail',
            sort_order: 1,
            lqip: generateLQIP()
          },
          {
            url: 'https://via.placeholder.com/800x600/2ECC71/FFFFFF?text=Back+View',
            thumbnailUrl: 'https://via.placeholder.com/150x150/2ECC71/FFFFFF?text=Back',
            alt: `${props.part?.name || 'قطعه'} - نمای پشت`,
            type: 'detail',
            sort_order: 2,
            lqip: generateLQIP()
          }
        ]
      }
    }
    
    // Generate Low Quality Image Placeholder
    const generateLQIP = () => {
      // Return a simple 1x1 transparent pixel as LQIP
      return 'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/2wBDAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwA/gA'
    }

    const videos = ref([
      // Mock video data
      // {
      //   url: '/videos/part-installation.mp4',
      //   thumbnailUrl: '/images/video-thumbnail.jpg',
      //   title: 'راهنمای نصب'
      // }
    ])

    // Mock 360° view data (24 frames for smooth rotation)
    const view360Images = ref([
      // These would be actual 360° images in production
      // '/images/360/frame-001.jpg',
      // '/images/360/frame-002.jpg',
      // ... up to frame-024.jpg
    ])

    const has360View = computed(() => view360Images.value.length > 0)

    // Computed properties
    const currentImage = computed(() => {
      return images.value[currentImageIndex.value] || null
    })

    // Image Optimization Utilities
    const getOptimizedImageUrl = (url, options = {}) => {
      // In production, this would integrate with your image optimization service
      // For now, we'll simulate query parameters for demonstration
      const { width, height, quality = 85, format } = options
      
      if (!url || url.startsWith('data:')) return url
      
      // Simulate image optimization service (replace with your CDN/service)
      const params = new URLSearchParams()
      if (width) params.append('w', width)
      if (height) params.append('h', height)
      if (quality) params.append('q', quality)
      if (format) params.append('f', format)
      
      const separator = url.includes('?') ? '&' : '?'
      return params.toString() ? `${url}${separator}${params}` : url
    }

    const generateSrcSet = (baseUrl) => {
      if (!baseUrl || baseUrl.startsWith('data:')) return ''
      
      const sizes = [
        { width: 400, descriptor: '400w' },
        { width: 800, descriptor: '800w' },
        { width: 1200, descriptor: '1200w' },
        { width: 1600, descriptor: '1600w' }
      ]
      
      return sizes
        .map(size => `${getOptimizedImageUrl(baseUrl, { width: size.width, quality: 85 })} ${size.descriptor}`)
        .join(', ')
    }

    const getImageFormat = (image) => {
      if (image.avif) return 'AVIF'
      if (image.webp) return 'WebP'
      return 'JPEG/PNG'
    }

    // Image Loading Methods
    const handleMainImageLoad = () => {
      mainImageLoaded.value = true
    }

    const handleThumbnailLoad = (index) => {
      thumbnailsLoaded.value.add(index)
    }

    const resetImageLoadingStates = () => {
      mainImageLoaded.value = false
      thumbnailsLoaded.value.clear()
    }

    // Enhanced Lazy Loading Implementation
    const initLazyLoading = () => {
      if ('IntersectionObserver' in window) {
        intersectionObserver.value = new IntersectionObserver((entries) => {
          entries.forEach(entry => {
            if (entry.isIntersecting) {
              const img = entry.target
              const dataSrc = img.getAttribute('data-src')
              if (dataSrc) {
                // Add loading class for transition
                img.classList.add('loading')
                
                // Create a new image to preload
                const preloadImg = new Image()
                preloadImg.onload = () => {
                  img.src = dataSrc
                  img.removeAttribute('data-src')
                  img.classList.remove('loading')
                  img.classList.add('loaded')
                  
                  // Dispatch custom event for analytics
                  img.dispatchEvent(new CustomEvent('lazyImageLoaded', {
                    detail: { src: dataSrc, loadTime: performance.now() }
                  }))
                }
                preloadImg.onerror = () => {
                  img.classList.remove('loading')
                  img.classList.add('error')
                  console.warn('Failed to load lazy image:', dataSrc)
                }
                preloadImg.src = dataSrc
                
                intersectionObserver.value.unobserve(img)
              }
            }
          })
        }, {
          rootMargin: '50px 0px',
          threshold: 0.01
        })

        // Observe all lazy images with better timing
        const observeLazyImages = () => {
          const lazyImages = document.querySelectorAll('.lazy-image')
          lazyImages.forEach(img => {
            if (img.hasAttribute('data-src')) {
              intersectionObserver.value.observe(img)
            }
          })
        }

        // Use requestAnimationFrame for better performance
        requestAnimationFrame(() => {
          setTimeout(observeLazyImages, 50)
        })
      } else {
        // Enhanced fallback with better error handling
        const lazyImages = document.querySelectorAll('.lazy-image')
        lazyImages.forEach(img => {
          const dataSrc = img.getAttribute('data-src')
          if (dataSrc) {
            const preloadImg = new Image()
            preloadImg.onload = () => {
              img.src = dataSrc
              img.removeAttribute('data-src')
              img.classList.add('loaded')
            }
            preloadImg.onerror = () => {
              img.classList.add('error')
              console.warn('Failed to load image:', dataSrc)
            }
            preloadImg.src = dataSrc
          }
        })
      }
    }

    // Image Prefetching for Performance
    const prefetchNextImages = () => {
      const nextIndex = (currentImageIndex.value + 1) % images.value.length
      const prevIndex = currentImageIndex.value === 0 ? images.value.length - 1 : currentImageIndex.value - 1
      
      [nextIndex, prevIndex].forEach(index => {
        const image = images.value[index]
        if (image && image.url) {
          const link = document.createElement('link')
          link.rel = 'prefetch'
          link.href = getOptimizedImageUrl(image.url, { width: 800, quality: 85 })
          document.head.appendChild(link)
        }
      })
    }

    // Enhanced Methods
    const selectImage = (index) => {
      if (index === currentImageIndex.value) return
      
      currentImageIndex.value = index
      resetImageLoadingStates()
      
      // Prefetch adjacent images for smoother navigation
      setTimeout(() => {
        prefetchNextImages()
      }, 100)
    }

    const openZoomModal = () => {
      showZoomModal.value = true
      // Preload high-resolution version for zoom
      const currentImg = currentImage.value
      if (currentImg && currentImg.url) {
        const highResUrl = getOptimizedImageUrl(currentImg.url, { width: 1600, quality: 90 })
        const img = new Image()
        img.src = highResUrl
      }
    }

    const closeZoomModal = () => {
      showZoomModal.value = false
    }

    const handleImageError = () => {
      console.warn('Main image failed to load')
      mainImageLoaded.value = true // Still hide loading state
    }

    const handleThumbnailError = (index) => {
      imageErrors.value.add(index)
      thumbnailsLoaded.value.add(index) // Hide loading state
      console.warn(`Thumbnail ${index} failed to load`)
    }

    // Keyboard navigation
    const handleKeydown = (event) => {
      if (!showZoomModal.value) return
      
      switch (event.key) {
        case 'Escape':
          closeZoomModal()
          break
        case 'ArrowLeft':
          if (currentImageIndex.value > 0) {
            selectImage(currentImageIndex.value - 1)
          }
          break
        case 'ArrowRight':
          if (currentImageIndex.value < images.value.length - 1) {
            selectImage(currentImageIndex.value + 1)
          }
          break
      }
    }

    // 360° view methods
    const start360Drag = (event) => {
      if (view360Images.value.length === 0) return
      isDragging360.value = true
      lastMouseX.value = event.clientX
      stopAutoRotation()
    }

    const handle360Drag = (event) => {
      if (!isDragging360.value || view360Images.value.length === 0) return
      
      const deltaX = event.clientX - lastMouseX.value
      const sensitivity = 3 // Adjust for rotation sensitivity
      
      if (Math.abs(deltaX) > sensitivity) {
        const direction = deltaX > 0 ? 1 : -1
        const newIndex = (current360Index.value + direction + view360Images.value.length) % view360Images.value.length
        current360Index.value = newIndex
        lastMouseX.value = event.clientX
      }
    }

    const end360Drag = () => {
      isDragging360.value = false
    }

    const toggleAutoRotation = () => {
      if (isAutoRotating.value) {
        stopAutoRotation()
      } else {
        startAutoRotation()
      }
    }

    const startAutoRotation = () => {
      if (view360Images.value.length === 0) return
      isAutoRotating.value = true
      autoRotationInterval.value = setInterval(() => {
        current360Index.value = (current360Index.value + 1) % view360Images.value.length
      }, 150) // Rotate every 150ms for smooth animation
    }

    const stopAutoRotation = () => {
      isAutoRotating.value = false
      if (autoRotationInterval.value) {
        clearInterval(autoRotationInterval.value)
        autoRotationInterval.value = null
      }
    }

    // Enhanced zoom modal with pan and zoom
    const zoomLevel = ref(1)
    const panX = ref(0)
    const panY = ref(0)
    const isPanning = ref(false)
    const lastPanX = ref(0)
    const lastPanY = ref(0)

    const resetZoom = () => {
      zoomLevel.value = 1
      panX.value = 0
      panY.value = 0
    }

    const zoomIn = () => {
      zoomLevel.value = Math.min(zoomLevel.value * 1.5, 5)
    }

    const zoomOut = () => {
      zoomLevel.value = Math.max(zoomLevel.value / 1.5, 0.5)
      if (zoomLevel.value === 1) {
        panX.value = 0
        panY.value = 0
      }
    }

    const enhancedOpenZoomModal = () => {
      showZoomModal.value = true
      resetZoom()
    }

    const enhancedCloseZoomModal = () => {
      showZoomModal.value = false
      resetZoom()
    }

    // Pan functionality for zoomed images
    const startPan = (event) => {
      if (zoomLevel.value <= 1) return
      isPanning.value = true
      lastPanX.value = event.clientX
      lastPanY.value = event.clientY
      event.preventDefault()
    }

    const handlePan = (event) => {
      if (!isPanning.value || zoomLevel.value <= 1) return
      
      const deltaX = event.clientX - lastPanX.value
      const deltaY = event.clientY - lastPanY.value
      
      panX.value += deltaX / zoomLevel.value
      panY.value += deltaY / zoomLevel.value
      
      lastPanX.value = event.clientX
      lastPanY.value = event.clientY
      event.preventDefault()
    }

    const endPan = () => {
      isPanning.value = false
    }

    // Lifecycle
    onMounted(() => {
      document.addEventListener('keydown', handleKeydown)
      
      // Initialize images from part data
      initializeImages()
      
      // Initialize lazy loading
      initLazyLoading()
      
      // Prefetch first image
      setTimeout(() => {
        prefetchNextImages()
      }, 1000)
      
      // Initialize 360° images from API data or create demo data
      if (props.part?.images) {
        const images360 = props.part.images
          .filter(img => img.image_type === '360')
          .sort((a, b) => a.sort_order - b.sort_order)
          .map(img => img.url)
        
        if (images360.length > 0) {
          view360Images.value = images360
        }
      }
      
      // Fallback demo 360° data for testing
      if (view360Images.value.length === 0 && (props.part?.id === 14 || import.meta.env.DEV)) {
        view360Images.value = Array.from({ length: 8 }, (_, i) => 
          `https://via.placeholder.com/400x400/4A90E2/FFFFFF?text=360°+Frame+${i + 1}`
        )
      }
    })

    // Cleanup
    const cleanup = () => {
      if (intersectionObserver.value) {
        intersectionObserver.value.disconnect()
      }
      if (autoRotationInterval.value) {
        clearInterval(autoRotationInterval.value)
      }
      document.removeEventListener('keydown', handleKeydown)
    }

    // Watch for prop changes
    watch(() => props.part, (newPart) => {
      if (newPart) {
        // Re-initialize images when part data changes
        initializeImages()
        resetImageLoadingStates()
        
        // Re-initialize 360° images
        if (newPart.images) {
          const images360 = newPart.images
            .filter(img => img.image_type === '360')
            .sort((a, b) => a.sort_order - b.sort_order)
            .map(img => img.url)
          
          view360Images.value = images360
        }
        
        // Re-initialize lazy loading after component updates
        setTimeout(() => {
          initLazyLoading()
        }, 100)
      }
    }, { deep: true })

    // Cleanup on unmount
    onUnmounted(() => {
      cleanup()
    })

    return {
      // Refs
      mainImageRef,
      currentImageIndex,
      showZoomModal,
      images,
      videos,
      has360View,
      currentImage,
      // Image loading states
      mainImageLoaded,
      thumbnailsLoaded,
      // Image optimization utilities
      getOptimizedImageUrl,
      generateSrcSet,
      getImageFormat,
      initializeImages,
      generateLQIP,
      // Enhanced methods
      selectImage,
      openZoomModal,
      closeZoomModal,
      handleImageError,
      handleThumbnailError,
      handleMainImageLoad,
      handleThumbnailLoad,
      // 360° view
      view360Images,
      current360Index,
      isDragging360,
      isAutoRotating,
      start360Drag,
      handle360Drag,
      end360Drag,
      toggleAutoRotation,
      // Enhanced zoom
      zoomLevel,
      panX,
      panY,
      isPanning,
      zoomIn,
      zoomOut,
      resetZoom,
      startPan,
      handlePan,
      endPan
    }
  }
}
</script>

<style scoped>
/* Lazy loading states */
.lazy-image {
  transition: opacity 0.3s ease-in-out, filter 0.3s ease-in-out;
}

.lazy-image.loading {
  opacity: 0.7;
  filter: blur(2px);
}

.lazy-image.loaded {
  opacity: 1;
  filter: none;
}

.lazy-image.error {
  opacity: 0.5;
  filter: grayscale(100%);
}

/* Progressive image loading animation */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.lazy-image.loaded {
  animation: fadeInUp 0.5s ease-out;
}

/* Loading spinner for images */
.lazy-image.loading::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 20px;
  height: 20px;
  margin: -10px 0 0 -10px;
  border: 2px solid #f3f3f3;
  border-top: 2px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Optimized image container */
.image-container {
  position: relative;
  overflow: hidden;
}

.image-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(90deg, 
    rgba(255,255,255,0) 0%, 
    rgba(255,255,255,0.8) 50%, 
    rgba(255,255,255,0) 100%);
  transform: translateX(-100%);
  animation: shimmer 1.5s infinite;
  opacity: 0;
}

.image-container.loading::before {
  opacity: 1;
}

@keyframes shimmer {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

/* Performance optimizations */
.media-gallery {
  contain: layout style paint;
  will-change: transform;
}

.thumbnail-grid {
  contain: layout;
}

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
  .lazy-image,
  .image-container::before {
    animation: none;
    transition: none;
  }
}
</style>
