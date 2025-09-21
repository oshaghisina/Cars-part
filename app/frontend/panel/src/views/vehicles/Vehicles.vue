<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="bg-white shadow rounded-lg p-6">
      <div class="flex justify-between items-center">
        <div>
          <h1 class="text-2xl font-bold text-gray-900">Vehicle Management</h1>
          <p class="text-gray-600 mt-2">Manage vehicle brands, models, and trims</p>
        </div>
        <div class="flex space-x-3">
          <button
            @click="refreshData"
            class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Refresh
          </button>
        </div>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div class="bg-white overflow-hidden shadow rounded-lg">
        <div class="p-5">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div class="w-8 h-8 bg-blue-500 rounded-md flex items-center justify-center">
                <span class="text-white text-sm font-medium">🏭</span>
              </div>
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">Total Brands</dt>
                <dd class="text-lg font-medium text-gray-900">{{ brandsStore.brandsCount }}</dd>
              </dl>
            </div>
          </div>
        </div>
      </div>

      <div class="bg-white overflow-hidden shadow rounded-lg">
        <div class="p-5">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div class="w-8 h-8 bg-green-500 rounded-md flex items-center justify-center">
                <span class="text-white text-sm font-medium">🚗</span>
              </div>
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">Total Models</dt>
                <dd class="text-lg font-medium text-gray-900">{{ modelsStore.modelsCount }}</dd>
              </dl>
            </div>
          </div>
        </div>
      </div>

      <div class="bg-white overflow-hidden shadow rounded-lg">
        <div class="p-5">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div class="w-8 h-8 bg-purple-500 rounded-md flex items-center justify-center">
                <span class="text-white text-sm font-medium">⚙️</span>
              </div>
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">Total Trims</dt>
                <dd class="text-lg font-medium text-gray-900">{{ trimsStore.trimsCount }}</dd>
              </dl>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Navigation Tabs -->
    <div class="bg-white shadow rounded-lg">
      <div class="border-b border-gray-200">
        <nav class="-mb-px flex space-x-8 px-6" aria-label="Tabs">
          <button
            @click="activeTab = 'brands'"
            :class="[
              activeTab === 'brands'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
              'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm'
            ]"
          >
            Brands ({{ brandsStore.brandsCount }})
          </button>
          <button
            @click="activeTab = 'models'"
            :class="[
              activeTab === 'models'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
              'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm'
            ]"
          >
            Models ({{ modelsStore.modelsCount }})
          </button>
          <button
            @click="activeTab = 'trims'"
            :class="[
              activeTab === 'trims'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
              'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm'
            ]"
          >
            Trims ({{ trimsStore.trimsCount }})
          </button>
        </nav>
      </div>

      <!-- Tab Content -->
      <div class="p-6">
        <!-- Brands Tab -->
        <div v-if="activeTab === 'brands'" class="space-y-4">
          <div class="flex justify-between items-center">
            <h3 class="text-lg font-medium text-gray-900">Vehicle Brands</h3>
            <button
              @click="showBrandForm = true"
              class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
              </svg>
              Add Brand
            </button>
          </div>

          <div v-if="brandsStore.loading" class="text-center py-8">
            <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <p class="mt-2 text-sm text-gray-500">Loading brands...</p>
          </div>

          <div v-else-if="brandsStore.brands.length === 0" class="text-center py-8">
            <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
            <h3 class="mt-2 text-sm font-medium text-gray-900">No brands</h3>
            <p class="mt-1 text-sm text-gray-500">Get started by creating a new brand.</p>
          </div>

          <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div
              v-for="brand in brandsStore.brands"
              :key="brand.id"
              class="bg-gray-50 rounded-lg p-4 hover:bg-gray-100 transition-colors cursor-pointer"
              @click="selectBrand(brand)"
            >
              <div class="flex justify-between items-start">
                <div>
                  <h4 class="text-lg font-medium text-gray-900">{{ brand.name }}</h4>
                  <p class="text-sm text-gray-500">{{ brand.name_fa || 'No Persian name' }}</p>
                  <p class="text-sm text-gray-500">{{ brand.name_cn || 'No Chinese name' }}</p>
                </div>
                <span
                  :class="[
                    brand.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800',
                    'inline-flex px-2 py-1 text-xs font-semibold rounded-full'
                  ]"
                >
                  {{ brand.is_active ? 'Active' : 'Inactive' }}
                </span>
              </div>
              <div class="mt-2 text-xs text-gray-500">
                Models: {{ brand.models_count || 0 }}
              </div>
            </div>
          </div>
        </div>

        <!-- Models Tab -->
        <div v-if="activeTab === 'models'" class="space-y-4">
          <div class="flex justify-between items-center">
            <h3 class="text-lg font-medium text-gray-900">Vehicle Models</h3>
            <button
              @click="showModelForm = true"
              class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
              </svg>
              Add Model
            </button>
          </div>

          <div v-if="modelsStore.loading" class="text-center py-8">
            <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <p class="mt-2 text-sm text-gray-500">Loading models...</p>
          </div>

          <div v-else-if="modelsStore.models.length === 0" class="text-center py-8">
            <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
            <h3 class="mt-2 text-sm font-medium text-gray-900">No models</h3>
            <p class="mt-1 text-sm text-gray-500">Get started by creating a new model.</p>
          </div>

          <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div
              v-for="model in modelsStore.models"
              :key="model.id"
              class="bg-gray-50 rounded-lg p-4 hover:bg-gray-100 transition-colors cursor-pointer"
              @click="selectModel(model)"
            >
              <div class="flex justify-between items-start">
                <div>
                  <h4 class="text-lg font-medium text-gray-900">{{ model.name }}</h4>
                  <p class="text-sm text-gray-500">{{ model.name_fa || 'No Persian name' }}</p>
                  <p class="text-sm text-gray-500">{{ model.name_cn || 'No Chinese name' }}</p>
                  <p class="text-sm text-gray-500">Brand: {{ model.brand_name || 'Unknown' }}</p>
                </div>
                <span
                  :class="[
                    model.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800',
                    'inline-flex px-2 py-1 text-xs font-semibold rounded-full'
                  ]"
                >
                  {{ model.is_active ? 'Active' : 'Inactive' }}
                </span>
              </div>
              <div class="mt-2 text-xs text-gray-500">
                Trims: {{ model.trims_count || 0 }}
              </div>
            </div>
          </div>
        </div>

        <!-- Trims Tab -->
        <div v-if="activeTab === 'trims'" class="space-y-4">
          <div class="flex justify-between items-center">
            <h3 class="text-lg font-medium text-gray-900">Vehicle Trims</h3>
            <button
              @click="showTrimForm = true"
              class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
              </svg>
              Add Trim
            </button>
          </div>

          <div v-if="trimsStore.loading" class="text-center py-8">
            <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <p class="mt-2 text-sm text-gray-500">Loading trims...</p>
          </div>

          <div v-else-if="trimsStore.trims.length === 0" class="text-center py-8">
            <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
            <h3 class="mt-2 text-sm font-medium text-gray-900">No trims</h3>
            <p class="mt-1 text-sm text-gray-500">Get started by creating a new trim.</p>
          </div>

          <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div
              v-for="trim in trimsStore.trims"
              :key="trim.id"
              class="bg-gray-50 rounded-lg p-4 hover:bg-gray-100 transition-colors cursor-pointer"
              @click="selectTrim(trim)"
            >
              <div class="flex justify-between items-start">
                <div>
                  <h4 class="text-lg font-medium text-gray-900">{{ trim.name }}</h4>
                  <p class="text-sm text-gray-500">{{ trim.name_fa || 'No Persian name' }}</p>
                  <p class="text-sm text-gray-500">{{ trim.name_cn || 'No Chinese name' }}</p>
                  <p class="text-sm text-gray-500">Model: {{ trim.model_name || 'Unknown' }}</p>
                </div>
                <span
                  :class="[
                    trim.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800',
                    'inline-flex px-2 py-1 text-xs font-semibold rounded-full'
                  ]"
                >
                  {{ trim.is_active ? 'Active' : 'Inactive' }}
                </span>
              </div>
              <div class="mt-2 text-xs text-gray-500">
                Year: {{ trim.year_start }} - {{ trim.year_end || 'Present' }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Forms will be added here -->
    <VehicleBrandForm v-if="showBrandForm" @close="showBrandForm = false" @saved="onBrandSaved" />
    <VehicleModelForm v-if="showModelForm" @close="showModelForm = false" @saved="onModelSaved" />
    <VehicleTrimForm v-if="showTrimForm" @close="showTrimForm = false" @saved="onTrimSaved" />
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useVehicleBrandsStore, useVehicleModelsStore, useVehicleTrimsStore } from '../../stores/vehicles'
import VehicleBrandForm from '../../components/vehicles/VehicleBrandForm.vue'
import VehicleModelForm from '../../components/vehicles/VehicleModelForm.vue'
import VehicleTrimForm from '../../components/vehicles/VehicleTrimForm.vue'

export default {
  name: 'Vehicles',
  components: {
    VehicleBrandForm,
    VehicleModelForm,
    VehicleTrimForm
  },
  setup() {
    const brandsStore = useVehicleBrandsStore()
    const modelsStore = useVehicleModelsStore()
    const trimsStore = useVehicleTrimsStore()

    const activeTab = ref('brands')
    const showBrandForm = ref(false)
    const showModelForm = ref(false)
    const showTrimForm = ref(false)
    const selectedBrand = ref(null)
    const showBrandDetail = ref(false)
    const selectedModel = ref(null)
    const showModelDetail = ref(false)
    const selectedTrim = ref(null)
    const showTrimDetail = ref(false)

    const refreshData = async () => {
      await Promise.all([
        brandsStore.fetchBrands(),
        modelsStore.fetchModels(),
        trimsStore.fetchTrims()
      ])
    }

    const selectBrand = (brand) => {
      console.log('Selected brand:', brand)
      // Navigate to brand detail or open edit form
      selectedBrand.value = brand
      showBrandDetail.value = true
      // Could also navigate to a dedicated brand page: router.push(`/vehicles/brands/${brand.id}`)
    }

    const selectModel = (model) => {
      console.log('Selected model:', model)
      // Navigate to model detail or open edit form
      selectedModel.value = model
      showModelDetail.value = true
      // Could also navigate to a dedicated model page: router.push(`/vehicles/models/${model.id}`)
    }

    const selectTrim = (trim) => {
      console.log('Selected trim:', trim)
      // Navigate to trim detail or open edit form
      selectedTrim.value = trim
      showTrimDetail.value = true
      // Could also navigate to a dedicated trim page: router.push(`/vehicles/trims/${trim.id}`)
    }

    const onBrandSaved = () => {
      showBrandForm.value = false
      brandsStore.fetchBrands()
    }

    const onModelSaved = () => {
      showModelForm.value = false
      modelsStore.fetchModels()
    }

    const onTrimSaved = () => {
      showTrimForm.value = false
      trimsStore.fetchTrims()
    }

    onMounted(() => {
      refreshData()
    })

    return {
      brandsStore,
      modelsStore,
      trimsStore,
      activeTab,
      showBrandForm,
      showModelForm,
      showTrimForm,
      selectedBrand,
      showBrandDetail,
      selectedModel,
      showModelDetail,
      selectedTrim,
      showTrimDetail,
      refreshData,
      selectBrand,
      selectModel,
      selectTrim,
      onBrandSaved,
      onModelSaved,
      onTrimSaved
    }
  }
}
</script>
