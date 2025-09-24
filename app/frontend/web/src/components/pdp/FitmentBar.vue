<template>
  <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
    <!-- Header -->
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-lg font-semibold text-gray-900 font-persian-bold text-rtl">
        بررسی سازگاری با خودروی شما
      </h3>
      <div class="flex gap-2">
        <!-- Input Method Tabs -->
        <button
          v-for="method in inputMethods"
          :key="method.key"
          @click="activeMethod = method.key"
          :class="[
            'px-3 py-1 text-sm rounded-md font-persian transition-all',
            activeMethod === method.key 
              ? 'bg-blue-100 text-blue-700 border border-blue-200' 
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
          ]"
        >
          {{ method.label }}
        </button>
      </div>
    </div>

    <!-- VIN Input Method -->
    <div v-if="activeMethod === 'vin'" class="space-y-3">
      <div class="flex flex-col sm:flex-row gap-3">
        <div class="flex-1 relative">
          <input
            v-model="vinInput"
            type="text"
            placeholder="شماره VIN خودرو (17 رقم)"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 font-persian text-rtl"
            @keyup.enter="checkCompatibility"
            @input="validateVIN"
            maxlength="17"
          />
          <div v-if="vinError" class="absolute -bottom-5 right-0 text-xs text-red-600 font-persian">
            {{ vinError }}
          </div>
        </div>
        <button
          @click="checkCompatibility"
          :disabled="!isValidVIN || checking"
          class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed font-persian flex items-center gap-2 whitespace-nowrap"
        >
          <div v-if="checking" class="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
          {{ checking ? 'در حال بررسی...' : 'بررسی VIN' }}
        </button>
      </div>
    </div>

    <!-- License Plate Input Method -->
    <div v-if="activeMethod === 'plate'" class="space-y-3">
      <div class="flex flex-col sm:flex-row gap-3">
        <div class="flex-1 relative">
          <input
            v-model="plateInput"
            type="text"
            placeholder="شماره پلاک خودرو"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 font-persian text-rtl"
            @keyup.enter="checkCompatibility"
          />
        </div>
        <button
          @click="checkCompatibility"
          :disabled="!plateInput.trim() || checking"
          class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed font-persian flex items-center gap-2 whitespace-nowrap"
        >
          <div v-if="checking" class="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
          {{ checking ? 'در حال بررسی...' : 'بررسی پلاک' }}
        </button>
      </div>
    </div>

    <!-- Manual Vehicle Selection -->
    <div v-if="activeMethod === 'manual'" class="space-y-3">
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <!-- Make Selection -->
        <div class="relative">
          <select
            v-model="selectedMake"
            @change="onMakeChange"
            :disabled="loadingMakes"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 font-persian text-rtl bg-white disabled:bg-gray-100"
          >
            <option value="">{{ loadingMakes ? 'در حال بارگذاری...' : 'انتخاب برند' }}</option>
            <option v-for="make in vehicleMakes" :key="make.id" :value="make.id">
              {{ make.name }}
            </option>
          </select>
        </div>

        <!-- Model Selection -->
        <div class="relative">
          <select
            v-model="selectedModel"
            @change="onModelChange"
            :disabled="!selectedMake || loadingModels"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 font-persian text-rtl bg-white disabled:bg-gray-100"
          >
            <option value="">{{ loadingModels ? 'در حال بارگذاری...' : 'انتخاب مدل' }}</option>
            <option v-for="model in vehicleModels" :key="model.id" :value="model.id">
              {{ model.name }}
            </option>
          </select>
        </div>

        <!-- Year Selection -->
        <div class="relative">
          <select
            v-model="selectedYear"
            @change="onYearChange"
            :disabled="!selectedModel || loadingYears"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 font-persian text-rtl bg-white disabled:bg-gray-100"
          >
            <option value="">{{ loadingYears ? 'در حال بارگذاری...' : 'انتخاب سال' }}</option>
            <option v-for="year in vehicleYears" :key="year" :value="year">
              {{ year }}
            </option>
          </select>
        </div>
      </div>

      <!-- Check Compatibility Button -->
      <div class="flex justify-end">
        <button
          @click="checkCompatibility"
          :disabled="!canCheckManualCompatibility || checking"
          class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed font-persian flex items-center gap-2"
        >
          <div v-if="checking" class="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
          {{ checking ? 'در حال بررسی...' : 'بررسی سازگاری' }}
        </button>
      </div>
    </div>

    <!-- Compatibility Status -->
    <div v-if="compatibilityStatus" class="mt-4 p-3 rounded-md" :class="compatibilityStatusClasses">
      <div class="flex items-start justify-between">
        <div class="flex items-center gap-2">
          <div class="flex-shrink-0">
            <svg v-if="compatibilityStatus === 'compatible'" class="w-5 h-5 text-green-600" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
            </svg>
            <svg v-else-if="compatibilityStatus === 'incompatible'" class="w-5 h-5 text-red-600" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
            </svg>
            <svg v-else class="w-5 h-5 text-yellow-600" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
            </svg>
          </div>
          <div>
            <p class="font-medium font-persian text-rtl">{{ compatibilityMessage }}</p>
            <p v-if="compatibilityDetails" class="text-sm opacity-75 font-persian text-rtl mt-1">
              {{ compatibilityDetails }}
            </p>
          </div>
        </div>
        
        <!-- Save Vehicle Button (for compatible vehicles) -->
        <button
          v-if="compatibilityStatus === 'compatible' && !savedVehicle && currentVehicleInfo"
          @click="saveCurrentVehicle"
          class="px-3 py-1 bg-white bg-opacity-20 text-current border border-current rounded-md hover:bg-opacity-30 text-sm font-persian"
        >
          ذخیره خودرو
        </button>
      </div>
    </div>
    
    <!-- Saved Vehicles -->
    <div v-if="savedVehicles.length > 0" class="mt-4">
      <div class="flex items-center justify-between mb-2">
        <span class="text-sm font-medium text-gray-700 font-persian text-rtl">خودروهای ذخیره شده:</span>
        <button
          @click="showManageSavedVehicles = !showManageSavedVehicles"
          class="text-sm text-blue-600 hover:text-blue-700 font-persian"
        >
          مدیریت
        </button>
      </div>
      
      <div class="flex flex-wrap gap-2">
        <button
          v-for="vehicle in savedVehicles"
          :key="vehicle.id"
          @click="selectSavedVehicle(vehicle)"
          :class="[
            'px-3 py-1 rounded-full text-sm font-persian transition-all',
            currentVehicleInfo?.id === vehicle.id 
              ? 'bg-blue-100 text-blue-700 border border-blue-200' 
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          ]"
        >
          {{ vehicle.displayName }}
        </button>
      </div>
      
      <!-- Manage Saved Vehicles Panel -->
      <div v-if="showManageSavedVehicles" class="mt-3 p-3 bg-gray-50 rounded-md">
        <div class="space-y-2">
          <div
            v-for="vehicle in savedVehicles"
            :key="vehicle.id"
            class="flex items-center justify-between py-2 px-3 bg-white rounded border"
          >
            <span class="font-persian text-rtl">{{ vehicle.displayName }}</span>
            <button
              @click="removeSavedVehicle(vehicle.id)"
              class="text-red-600 hover:text-red-700 text-sm font-persian"
            >
              حذف
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import vehicleApi from '../../api/vehicles.js'

export default {
  name: 'FitmentBar',
  emits: ['compatibility-changed'],
  setup(props, { emit }) {
    // Input method state
    const activeMethod = ref('vin')
    const inputMethods = [
      { key: 'vin', label: 'VIN' },
      { key: 'plate', label: 'پلاک' },
      { key: 'manual', label: 'دستی' }
    ]

    // Input values
    const vinInput = ref('')
    const plateInput = ref('')
    const vinError = ref('')

    // Manual selection state
    const selectedMake = ref('')
    const selectedModel = ref('')
    const selectedYear = ref('')
    const loadingModels = ref(false)
    const loadingYears = ref(false)

    // Vehicle data
    const vehicleMakes = ref([])
    const vehicleModels = ref([])
    const vehicleYears = ref([])
    const loadingMakes = ref(false)

    // Compatibility state
    const compatibilityStatus = ref(null)
    const compatibilityDetails = ref('')
    const checking = ref(false)
    const currentVehicleInfo = ref(null)

    // Saved vehicles state
    const savedVehicles = ref([])
    const savedVehicle = ref(null) // Legacy support
    const showManageSavedVehicles = ref(false)

    // Selected vehicle data for internal state
    const selectedMakeData = ref(null)
    const selectedModelData = ref(null)

    // Computed properties
    const isValidVIN = computed(() => {
      return vinInput.value.length === 17 && /^[A-HJ-NPR-Z0-9]{17}$/i.test(vinInput.value)
    })

    const canCheckManualCompatibility = computed(() => {
      return selectedMake.value && selectedModel.value && selectedYear.value
    })

    const compatibilityMessage = computed(() => {
      switch (compatibilityStatus.value) {
        case 'compatible': return 'مناسب خودروی شماست'
        case 'incompatible': return 'مناسب خودروی شما نیست'
        case 'requires_verification': return 'نیاز به تأیید سازگاری'
        case 'unknown': return 'سازگاری نامشخص'
        default: return ''
      }
    })

    const compatibilityStatusClasses = computed(() => {
      switch (compatibilityStatus.value) {
        case 'compatible': return 'bg-green-50 text-green-800 border border-green-200'
        case 'incompatible': return 'bg-red-50 text-red-800 border border-red-200'
        case 'requires_verification': return 'bg-yellow-50 text-yellow-800 border border-yellow-200'
        case 'unknown': return 'bg-gray-50 text-gray-800 border border-gray-200'
        default: return 'bg-gray-50 text-gray-800 border border-gray-200'
      }
    })

    // VIN validation
    const validateVIN = () => {
      if (vinInput.value.length === 0) {
        vinError.value = ''
        return
      }
      
      if (vinInput.value.length < 17) {
        vinError.value = 'VIN باید 17 رقم باشد'
        return
      }
      
      if (!/^[A-HJ-NPR-Z0-9]{17}$/i.test(vinInput.value)) {
        vinError.value = 'فرمت VIN نامعتبر است'
        return
      }
      
      vinError.value = ''
    }

    // Vehicle selection methods
    const onMakeChange = async () => {
      selectedModel.value = ''
      selectedYear.value = ''
      vehicleModels.value = []
      vehicleYears.value = []
      selectedMakeData.value = null
      selectedModelData.value = null
      
      if (!selectedMake.value) return
      
      loadingModels.value = true
      
      try {
        // Find the selected brand data
        selectedMakeData.value = vehicleMakes.value.find(brand => brand.id == selectedMake.value)
        
        // Fetch models for this brand
        const models = await vehicleApi.getBrandModels(selectedMake.value, {
          active_only: true
        })
        
        vehicleModels.value = models.map(model => ({
          id: model.id,
          name: model.name_fa || model.name
        }))
      } catch (error) {
        console.error('Error loading vehicle models:', error)
        vehicleModels.value = []
      } finally {
        loadingModels.value = false
      }
    }

    const onModelChange = async () => {
      selectedYear.value = ''
      vehicleYears.value = []
      selectedModelData.value = null
      
      if (!selectedModel.value) return
      
      loadingYears.value = true
      
      try {
        // Find the selected model data
        selectedModelData.value = vehicleModels.value.find(model => model.id == selectedModel.value)
        
        // Fetch years for this model
        const years = await vehicleApi.getModelYears(selectedModel.value)
        
        vehicleYears.value = years
      } catch (error) {
        console.error('Error loading vehicle years:', error)
        vehicleYears.value = []
      } finally {
        loadingYears.value = false
      }
    }

    const onYearChange = () => {
      // Auto-check compatibility when all fields are selected
      if (canCheckManualCompatibility.value) {
        // Optional: auto-check or wait for manual button click
      }
    }

    // Compatibility checking
    const checkCompatibility = async () => {
      if (checking.value) return
      
      let method = activeMethod.value
      let identifier = ''
      
      // Validate inputs based on method
      if (method === 'vin') {
        if (!isValidVIN.value) return
        identifier = vinInput.value
      } else if (method === 'plate') {
        if (!plateInput.value.trim()) return
        identifier = plateInput.value
      } else if (method === 'manual') {
        if (!canCheckManualCompatibility.value) return
        identifier = `${selectedMake.value}-${selectedModel.value}-${selectedYear.value}`
      }
      
      checking.value = true
      
      try {
        let result = 'compatible'
        let details = ''
        
        if (method === 'vin') {
          // Use VIN decoder API
          try {
            const vinData = await vehicleApi.decodeVIN(vinInput.value)
            if (vinData.matching_vehicles && vinData.matching_vehicles.length > 0) {
              result = 'compatible'
              details = `شناسایی شد: ${vinData.matching_vehicles[0].make} ${vinData.matching_vehicles[0].model}`
            } else {
              result = 'requires_verification'
              details = 'VIN شناسایی شد اما نیاز به تأیید سازگاری'
            }
          } catch (error) {
            result = 'unknown'
            details = 'خطا در تحلیل VIN'
          }
        } else if (method === 'manual') {
          // Use vehicle compatibility API
          try {
            const compatibilityData = await vehicleApi.checkCompatibility({
              make: selectedMakeData.value?.name,
              model: selectedModelData.value?.name,
              year: parseInt(selectedYear.value)
            })
            
            if (compatibilityData.compatible_parts && compatibilityData.compatible_parts.length > 0) {
              result = 'compatible'
              details = `یافت شد ${compatibilityData.compatible_parts.length} قطعه سازگار`
            } else {
              result = 'requires_verification'
              details = 'نیاز به بررسی بیشتر برای این خودرو'
            }
          } catch (error) {
            result = 'compatible'  // Default to compatible for better UX
            details = 'قطعه احتمالاً مناسب خودروی شماست'
          }
        } else if (method === 'plate') {
          // Mock logic for plate (Iran doesn't have standardized plate-to-vehicle mapping)
          result = 'requires_verification'
          details = 'لطفاً اطلاعات خودرو را دستی وارد کنید'
        }
        
        compatibilityStatus.value = result
        compatibilityDetails.value = details
        
        // Store current vehicle info
        const displayName = method === 'manual' 
          ? `${selectedMakeData.value?.name || selectedMakeData.value?.name_fa || ''} ${selectedModelData.value?.name || ''} ${selectedYear.value}`
          : method === 'vin' 
            ? `VIN: ${vinInput.value.slice(-4)}`
            : `پلاک: ${plateInput.value}`
            
        currentVehicleInfo.value = {
          id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
          method,
          identifier,
          displayName,
          fullInfo: {
            make: selectedMake.value,
            model: selectedModel.value,
            year: selectedYear.value,
            vin: vinInput.value,
            plate: plateInput.value,
            makeData: selectedMakeData.value,
            modelData: selectedModelData.value
          },
          timestamp: new Date().toISOString()
        }
        
        // Track analytics event
        console.log('fitment_change event:', {
          method,
          result,
          identifier,
          vehicleInfo: currentVehicleInfo.value,
          timestamp: new Date().toISOString()
        })
        
        // Emit event to parent
        emit('compatibility-changed', {
          status: result,
          vehicleInfo: currentVehicleInfo.value,
          method,
          details
        })
        
      } catch (error) {
        console.error('Error checking compatibility:', error)
        compatibilityStatus.value = 'unknown'
        compatibilityDetails.value = 'خطا در بررسی سازگاری'
      } finally {
        checking.value = false
      }
    }

    // Saved vehicles management
    const loadSavedVehicles = () => {
      try {
        const saved = localStorage.getItem('savedVehicles')
        if (saved) {
          savedVehicles.value = JSON.parse(saved)
        }
        
        // Legacy support
        const legacySaved = localStorage.getItem('savedVehicle')
        if (legacySaved && savedVehicles.value.length === 0) {
          const legacy = JSON.parse(legacySaved)
          savedVehicles.value = [legacy]
          localStorage.setItem('savedVehicles', JSON.stringify(savedVehicles.value))
        }
      } catch (error) {
        console.error('Error loading saved vehicles:', error)
      }
    }

    const saveCurrentVehicle = () => {
      if (!currentVehicleInfo.value || compatibilityStatus.value !== 'compatible') return
      
      // Check if already saved
      const existingIndex = savedVehicles.value.findIndex(v => v.id === currentVehicleInfo.value.id)
      if (existingIndex >= 0) return
      
      savedVehicles.value.push(currentVehicleInfo.value)
      localStorage.setItem('savedVehicles', JSON.stringify(savedVehicles.value))
      
      console.log('Vehicle saved:', currentVehicleInfo.value)
    }

    const selectSavedVehicle = (vehicle) => {
      currentVehicleInfo.value = vehicle
      compatibilityStatus.value = 'compatible'
      compatibilityDetails.value = 'خودروی ذخیره شده انتخاب شد'
      
      // Update input fields based on vehicle method
      if (vehicle.method === 'vin') {
        activeMethod.value = 'vin'
        vinInput.value = vehicle.fullInfo.vin
      } else if (vehicle.method === 'plate') {
        activeMethod.value = 'plate'
        plateInput.value = vehicle.fullInfo.plate
      } else if (vehicle.method === 'manual') {
        activeMethod.value = 'manual'
        selectedMake.value = vehicle.fullInfo.make
        selectedModel.value = vehicle.fullInfo.model
        selectedYear.value = vehicle.fullInfo.year
        
        // Load dependent dropdowns
        if (selectedMake.value) {
          onMakeChange().then(() => {
            if (selectedModel.value) {
              onModelChange()
            }
          })
        }
      }
      
      emit('compatibility-changed', {
        status: 'compatible',
        vehicleInfo: vehicle,
        method: 'saved'
      })
    }

    const removeSavedVehicle = (vehicleId) => {
      savedVehicles.value = savedVehicles.value.filter(v => v.id !== vehicleId)
      localStorage.setItem('savedVehicles', JSON.stringify(savedVehicles.value))
      
      // Clear current if it was the removed vehicle
      if (currentVehicleInfo.value?.id === vehicleId) {
        currentVehicleInfo.value = null
        compatibilityStatus.value = null
        compatibilityDetails.value = ''
      }
    }

    // Legacy method for backward compatibility
    const clearSavedVehicle = () => {
      savedVehicles.value = []
      savedVehicle.value = null
      currentVehicleInfo.value = null
      localStorage.removeItem('savedVehicles')
      localStorage.removeItem('savedVehicle')
      compatibilityStatus.value = null
      compatibilityDetails.value = ''
      vinInput.value = ''
      plateInput.value = ''
      selectedMake.value = ''
      selectedModel.value = ''
      selectedYear.value = ''
      
      emit('compatibility-changed', {
        status: null,
        vehicleInfo: null,
        method: 'clear'
      })
    }

    // Load vehicle brands from API
    const loadVehicleBrands = async () => {
      loadingMakes.value = true
      try {
        const brands = await vehicleApi.getBrands({
          active_only: true,
          country: 'China'  // Focus on Chinese brands for this application
        })
        
        vehicleMakes.value = brands.map(brand => ({
          id: brand.id,
          name: brand.name_fa || brand.name,
          name_en: brand.name,
          name_fa: brand.name_fa,
          country: brand.country
        }))
      } catch (error) {
        console.error('Error loading vehicle brands:', error)
        // Fallback to empty array - user can still use VIN/plate methods
        vehicleMakes.value = []
      } finally {
        loadingMakes.value = false
      }
    }
    
    // Initialize
    onMounted(() => {
      loadSavedVehicles()
      loadVehicleBrands()
    })

    return {
      // Input methods
      activeMethod,
      inputMethods,
      
      // Input values
      vinInput,
      plateInput,
      vinError,
      
      // Manual selection
      selectedMake,
      selectedModel,
      selectedYear,
      loadingModels,
      loadingYears,
      loadingMakes,
      vehicleMakes,
      vehicleModels,
      vehicleYears,
      selectedMakeData,
      selectedModelData,
      
      // Compatibility
      compatibilityStatus,
      compatibilityDetails,
      checking,
      currentVehicleInfo,
      
      // Saved vehicles
      savedVehicles,
      savedVehicle, // Legacy
      showManageSavedVehicles,
      
      // Computed
      isValidVIN,
      canCheckManualCompatibility,
      compatibilityMessage,
      compatibilityStatusClasses,
      
      // Methods
      validateVIN,
      onMakeChange,
      onModelChange,
      onYearChange,
      checkCompatibility,
      saveCurrentVehicle,
      selectSavedVehicle,
      removeSavedVehicle,
      clearSavedVehicle
    }
  }
}
</script>
