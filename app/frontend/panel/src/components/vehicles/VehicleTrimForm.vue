<template>
  <div class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
    <div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
      <div class="mt-3">
        <!-- Header -->
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-medium text-gray-900">Add Vehicle Trim</h3>
          <button
            @click="$emit('close')"
            class="text-gray-400 hover:text-gray-600"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Form -->
        <form @submit.prevent="handleSubmit" class="space-y-4">
          <!-- Model Selection -->
          <div>
            <label for="model_id" class="block text-sm font-medium text-gray-700">Model *</label>
            <select
              id="model_id"
              v-model="formData.model_id"
              required
              class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
            >
              <option value="">Select a model</option>
              <option v-for="model in modelsStore.models" :key="model.id" :value="model.id">
                {{ model.brand_name }} - {{ model.name }}
              </option>
            </select>
          </div>

          <!-- Trim Name (English) -->
          <div>
            <label for="name" class="block text-sm font-medium text-gray-700">Trim Name (English) *</label>
            <input
              id="name"
              v-model="formData.name"
              type="text"
              required
              class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              placeholder="e.g., Pro"
            />
          </div>

          <!-- Trim Name (Persian) -->
          <div>
            <label for="name_fa" class="block text-sm font-medium text-gray-700">Trim Name (Persian)</label>
            <input
              id="name_fa"
              v-model="formData.name_fa"
              type="text"
              class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              placeholder="e.g., پرو"
            />
          </div>

          <!-- Trim Name (Chinese) -->
          <div>
            <label for="name_cn" class="block text-sm font-medium text-gray-700">Trim Name (Chinese)</label>
            <input
              id="name_cn"
              v-model="formData.name_cn"
              type="text"
              class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              placeholder="e.g., 专业版"
            />
          </div>

          <!-- Year Range -->
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label for="year_start" class="block text-sm font-medium text-gray-700">Start Year *</label>
              <input
                id="year_start"
                v-model="formData.year_start"
                type="number"
                required
                min="1990"
                :max="new Date().getFullYear()"
                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                placeholder="2020"
              />
            </div>
            <div>
              <label for="year_end" class="block text-sm font-medium text-gray-700">End Year</label>
              <input
                id="year_end"
                v-model="formData.year_end"
                type="number"
                min="1990"
                :max="new Date().getFullYear() + 5"
                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                placeholder="2025"
              />
            </div>
          </div>

          <!-- Engine Type -->
          <div>
            <label for="engine_type" class="block text-sm font-medium text-gray-700">Engine Type</label>
            <input
              id="engine_type"
              v-model="formData.engine_type"
              type="text"
              class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              placeholder="e.g., 1.6L Turbo"
            />
          </div>

          <!-- Transmission -->
          <div>
            <label for="transmission" class="block text-sm font-medium text-gray-700">Transmission</label>
            <select
              id="transmission"
              v-model="formData.transmission"
              class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
            >
              <option value="">Select transmission</option>
              <option value="Manual">Manual</option>
              <option value="Automatic">Automatic</option>
              <option value="CVT">CVT</option>
              <option value="Semi-Automatic">Semi-Automatic</option>
            </select>
          </div>

          <!-- Drive Type -->
          <div>
            <label for="drive_type" class="block text-sm font-medium text-gray-700">Drive Type</label>
            <select
              id="drive_type"
              v-model="formData.drive_type"
              class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
            >
              <option value="">Select drive type</option>
              <option value="FWD">Front Wheel Drive (FWD)</option>
              <option value="RWD">Rear Wheel Drive (RWD)</option>
              <option value="AWD">All Wheel Drive (AWD)</option>
              <option value="4WD">Four Wheel Drive (4WD)</option>
            </select>
          </div>

          <!-- Description -->
          <div>
            <label for="description" class="block text-sm font-medium text-gray-700">Description</label>
            <textarea
              id="description"
              v-model="formData.description"
              rows="3"
              class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              placeholder="Trim description..."
            />
          </div>

          <!-- Active Status -->
          <div class="flex items-center">
            <input
              id="is_active"
              v-model="formData.is_active"
              type="checkbox"
              class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <label for="is_active" class="ml-2 block text-sm text-gray-900">
              Active
            </label>
          </div>

          <!-- Error Message -->
          <div v-if="error" class="rounded-md bg-red-50 p-4">
            <div class="flex">
              <div class="flex-shrink-0">
                <svg class="h-5 w-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                </svg>
              </div>
              <div class="ml-3">
                <h3 class="text-sm font-medium text-red-800">
                  Error
                </h3>
                <div class="mt-2 text-sm text-red-700">
                  {{ error }}
                </div>
              </div>
            </div>
          </div>

          <!-- Form Actions -->
          <div class="flex justify-end space-x-3 pt-4">
            <button
              type="button"
              @click="$emit('close')"
              class="inline-flex justify-center py-2 px-4 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Cancel
            </button>
            <button
              type="submit"
              :disabled="loading"
              class="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
            >
              <svg v-if="loading" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              {{ loading ? 'Creating...' : 'Create Trim' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { useVehicleModelsStore, useVehicleTrimsStore } from '../../stores/vehicles'

export default {
  name: 'VehicleTrimForm',
  emits: ['close', 'saved'],
  setup(props, { emit }) {
    const modelsStore = useVehicleModelsStore()
    const trimsStore = useVehicleTrimsStore()
    
    const loading = ref(false)
    const error = ref(null)
    
    const formData = reactive({
      model_id: '',
      name: '',
      name_fa: '',
      name_cn: '',
      year_start: new Date().getFullYear(),
      year_end: null,
      engine_type: '',
      transmission: '',
      drive_type: '',
      description: '',
      is_active: true
    })

    const handleSubmit = async () => {
      loading.value = true
      error.value = null
      
      try {
        await trimsStore.createTrim(formData)
        emit('saved')
      } catch (err) {
        error.value = err.message || 'Failed to create trim'
      } finally {
        loading.value = false
      }
    }

    onMounted(async () => {
      if (modelsStore.models.length === 0) {
        await modelsStore.fetchModels()
      }
    })

    return {
      modelsStore,
      loading,
      error,
      formData,
      handleSubmit
    }
  }
}
</script>
