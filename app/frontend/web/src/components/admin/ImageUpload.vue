<template>
  <div class="image-upload-component">
    <!-- Upload Area -->
    <div 
      class="upload-area"
      :class="{ 
        'drag-over': isDragOver,
        'uploading': isUploading,
        'has-error': uploadError
      }"
      @drop="handleDrop"
      @dragover.prevent="isDragOver = true"
      @dragleave="isDragOver = false"
      @click="triggerFileInput"
    >
      <input
        ref="fileInput"
        type="file"
        multiple
        accept="image/*"
        class="hidden"
        @change="handleFileSelect"
      />
      
      <!-- Upload UI -->
      <div v-if="!isUploading" class="upload-ui">
        <div class="upload-icon">
          <svg class="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>
        </div>
        <p class="text-lg font-medium text-gray-700 mb-2">
          Drag & drop images here or click to browse
        </p>
        <p class="text-sm text-gray-500">
          Supports JPG, PNG, WebP, GIF up to 10MB each
        </p>
      </div>
      
      <!-- Upload Progress -->
      <div v-else class="upload-progress">
        <div class="progress-icon">
          <svg class="w-8 h-8 text-blue-500 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        </div>
        <p class="text-lg font-medium text-gray-700">
          Uploading {{ uploadProgress.current }} of {{ uploadProgress.total }}...
        </p>
        <div class="progress-bar">
          <div 
            class="progress-fill"
            :style="{ width: `${uploadProgress.percentage}%` }"
          ></div>
        </div>
      </div>
      
      <!-- Error State -->
      <div v-if="uploadError" class="upload-error">
        <div class="error-icon">
          <svg class="w-8 h-8 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <p class="text-red-600 font-medium">{{ uploadError }}</p>
        <button 
          @click="clearError"
          class="mt-2 text-sm text-blue-600 hover:text-blue-800"
        >
          Try Again
        </button>
      </div>
    </div>
    
    <!-- Image Type Selection -->
    <div class="mt-4">
      <label class="block text-sm font-medium text-gray-700 mb-2">
        Image Type
      </label>
      <select
        v-model="selectedImageType"
        class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
      >
        <option value="main">Main Product Image</option>
        <option value="detail">Detail View</option>
        <option value="installation">Installation Guide</option>
        <option value="360">360° View Frame</option>
        <option value="gallery">Gallery Image</option>
      </select>
    </div>
    
    <!-- Uploaded Images Preview -->
    <div v-if="uploadedImages.length > 0" class="mt-6">
      <h3 class="text-lg font-medium text-gray-900 mb-4">
        Uploaded Images ({{ uploadedImages.length }})
      </h3>
      
      <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
        <div
          v-for="image in uploadedImages"
          :key="image.id"
          class="image-preview"
        >
          <div class="relative group">
            <img
              :src="image.thumbnails?.small || image.url"
              :alt="image.alt_text"
              class="w-full h-32 object-cover rounded-lg border border-gray-200"
              @error="handleImageError"
            />
            
            <!-- Image Overlay -->
            <div class="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-40 transition-opacity rounded-lg flex items-center justify-center">
              <div class="opacity-0 group-hover:opacity-100 transition-opacity flex space-x-2">
                <button
                  @click="viewImage(image)"
                  class="p-2 bg-white rounded-full text-gray-700 hover:text-blue-600"
                  title="View Image"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                </button>
                <button
                  @click="deleteImage(image)"
                  class="p-2 bg-white rounded-full text-gray-700 hover:text-red-600"
                  title="Delete Image"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>
            </div>
            
            <!-- Image Type Badge -->
            <div class="absolute top-2 left-2">
              <span class="px-2 py-1 text-xs font-medium bg-blue-600 text-white rounded">
                {{ image.type }}
              </span>
            </div>
          </div>
          
          <!-- Image Info -->
          <div class="mt-2">
            <p class="text-sm font-medium text-gray-900 truncate">
              {{ image.alt_text }}
            </p>
            <p class="text-xs text-gray-500">
              {{ formatFileSize(image.size) }}
            </p>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Image Viewer Modal -->
    <div
      v-if="viewerImage"
      class="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50"
      @click="closeViewer"
    >
      <div class="relative max-w-4xl max-h-full p-4" @click.stop>
        <img
          :src="viewerImage.url"
          :alt="viewerImage.alt_text"
          class="max-w-full max-h-full object-contain"
        />
        <button
          @click="closeViewer"
          class="absolute top-4 right-4 text-white hover:text-gray-300"
        >
          <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed } from 'vue'
import axios from 'axios'

export default {
  name: 'ImageUpload',
  props: {
    partId: {
      type: Number,
      required: true
    },
    existingImages: {
      type: Array,
      default: () => []
    }
  },
  emits: ['images-uploaded', 'image-deleted'],
  setup(props, { emit }) {
    const fileInput = ref(null)
    const isDragOver = ref(false)
    const isUploading = ref(false)
    const uploadError = ref('')
    const selectedImageType = ref('main')
    const uploadedImages = ref([...props.existingImages])
    const viewerImage = ref(null)
    
    const uploadProgress = reactive({
      current: 0,
      total: 0,
      percentage: 0
    })
    
    const triggerFileInput = () => {
      if (!isUploading.value) {
        fileInput.value?.click()
      }
    }
    
    const handleDrop = (event) => {
      event.preventDefault()
      isDragOver.value = false
      
      const files = Array.from(event.dataTransfer.files)
      uploadFiles(files)
    }
    
    const handleFileSelect = (event) => {
      const files = Array.from(event.target.files)
      uploadFiles(files)
      
      // Clear input
      event.target.value = ''
    }
    
    const uploadFiles = async (files) => {
      if (!files.length || isUploading.value) return
      
      // Validate files
      const validFiles = files.filter(file => {
        if (!file.type.startsWith('image/')) {
          console.warn(`Skipping non-image file: ${file.name}`)
          return false
        }
        if (file.size > 10 * 1024 * 1024) {
          console.warn(`Skipping large file: ${file.name}`)
          return false
        }
        return true
      })
      
      if (!validFiles.length) {
        uploadError.value = 'No valid image files selected'
        return
      }
      
      isUploading.value = true
      uploadError.value = ''
      uploadProgress.current = 0
      uploadProgress.total = validFiles.length
      uploadProgress.percentage = 0
      
      try {
        for (let i = 0; i < validFiles.length; i++) {
          const file = validFiles[i]
          uploadProgress.current = i + 1
          uploadProgress.percentage = Math.round(((i + 1) / validFiles.length) * 100)
          
          await uploadSingleFile(file)
        }
        
        emit('images-uploaded', uploadedImages.value)
        
      } catch (error) {
        uploadError.value = error.message || 'Upload failed'
      } finally {
        isUploading.value = false
      }
    }
    
    const uploadSingleFile = async (file) => {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('image_type', selectedImageType.value)
      formData.append('alt_text', `${file.name} - ${selectedImageType.value}`)
      
      const response = await axios.post(
        `/api/v1/images/upload/${props.partId}`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
            'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
          }
        }
      )
      
      const uploadedImage = {
        ...response.data,
        size: file.size
      }
      
      uploadedImages.value.push(uploadedImage)
    }
    
    const deleteImage = async (image) => {
      if (!confirm('Are you sure you want to delete this image?')) {
        return
      }
      
      try {
        await axios.delete(`/api/v1/images/${image.id}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
          }
        })
        
        // Remove from local array
        const index = uploadedImages.value.findIndex(img => img.id === image.id)
        if (index > -1) {
          uploadedImages.value.splice(index, 1)
        }
        
        emit('image-deleted', image)
        
      } catch (error) {
        console.error('Error deleting image:', error)
        alert('Failed to delete image')
      }
    }
    
    const viewImage = (image) => {
      viewerImage.value = image
    }
    
    const closeViewer = () => {
      viewerImage.value = null
    }
    
    const clearError = () => {
      uploadError.value = ''
    }
    
    const handleImageError = (event) => {
      event.target.src = 'https://via.placeholder.com/150x150/E5E7EB/9CA3AF?text=Error'
    }
    
    const formatFileSize = (bytes) => {
      if (!bytes) return 'Unknown'
      
      const sizes = ['Bytes', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(1024))
      return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i]
    }
    
    return {
      fileInput,
      isDragOver,
      isUploading,
      uploadError,
      selectedImageType,
      uploadedImages,
      viewerImage,
      uploadProgress,
      triggerFileInput,
      handleDrop,
      handleFileSelect,
      deleteImage,
      viewImage,
      closeViewer,
      clearError,
      handleImageError,
      formatFileSize
    }
  }
}
</script>

<style scoped>
.upload-area {
  @apply border-2 border-dashed border-gray-300 rounded-lg p-8 text-center cursor-pointer transition-all;
}

.upload-area.drag-over {
  @apply border-blue-500 bg-blue-50;
}

.upload-area.uploading {
  @apply cursor-not-allowed bg-gray-50;
}

.upload-area.has-error {
  @apply border-red-300 bg-red-50;
}

.upload-area:hover:not(.uploading):not(.has-error) {
  @apply border-gray-400 bg-gray-50;
}

.progress-bar {
  @apply w-full bg-gray-200 rounded-full h-2 mt-4;
}

.progress-fill {
  @apply bg-blue-600 h-2 rounded-full transition-all duration-300;
}

.image-preview {
  @apply transition-transform hover:scale-105;
}

.hidden {
  display: none;
}
</style>
