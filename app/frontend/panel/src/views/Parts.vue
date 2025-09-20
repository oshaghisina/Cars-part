<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="bg-white shadow rounded-lg p-6">
      <div class="flex justify-between items-center">
        <div>
          <h1 class="text-2xl font-bold text-gray-900">Parts Management</h1>
          <p class="text-gray-600 mt-2">Manage parts database and pricing</p>
        </div>
        <div class="flex space-x-3">
          <button
            @click="showAddPartModal = true"
            class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
            aria-label="Add new part"
          >
            Add Part
          </button>
          <button
            @click="showImportModal = true"
            class="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 transition-colors"
            aria-label="Import parts from Excel"
          >
            Import Excel
          </button>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white shadow rounded-lg p-6">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700">Search</label>
          <input
            v-model="filters.search"
            type="text"
            placeholder="Search parts..."
            class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700">Category</label>
          <select
            v-model="filters.category"
            class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Categories</option>
            <option v-for="category in categories" :key="category" :value="category">
              {{ category }}
            </option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700">Vehicle Make</label>
          <select
            v-model="filters.vehicle_make"
            class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Makes</option>
            <option v-for="make in vehicleMakes" :key="make" :value="make">
              {{ make }}
            </option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700">Status</label>
          <select
            v-model="filters.status"
            class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Status</option>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
          </select>
        </div>
      </div>
      <div class="mt-4">
        <button
          @click="applyFilters"
          class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          Apply Filters
        </button>
        <button
          @click="clearFilters"
          class="ml-2 px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700"
        >
          Clear
        </button>
      </div>
    </div>

    <!-- Parts Table -->
    <div class="bg-white shadow rounded-lg">
      <div class="px-4 py-5 sm:p-6">
        <div v-if="loading" class="text-center py-8">
          <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p class="mt-2 text-sm text-gray-500">Loading parts...</p>
        </div>
        
        <div v-else-if="error" class="text-center py-8">
          <p class="text-red-500">{{ error }}</p>
          <button
            @click="fetchParts"
            class="mt-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
        
        <div v-else-if="parts.length === 0" class="text-center py-8">
          <p class="text-gray-500">No parts found</p>
        </div>
        
        <div v-else class="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
          <table class="min-w-full divide-y divide-gray-300">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Part Name
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Vehicle
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  OEM Code
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Category
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="part in parts" :key="part.id">
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="text-sm font-medium text-gray-900">{{ part.part_name }}</div>
                  <div class="text-sm text-gray-500">{{ part.brand_oem }}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {{ part.vehicle_make }} {{ part.vehicle_model }}
                  <div v-if="part.vehicle_trim" class="text-xs text-gray-500">{{ part.vehicle_trim }}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ part.oem_code || 'N/A' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ part.category }}
                  <div v-if="part.subcategory" class="text-xs text-gray-400">{{ part.subcategory }}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span :class="getStatusBadgeClass(part.status)" class="inline-flex px-2 py-1 text-xs font-semibold rounded-full">
                    {{ part.status }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                  <button
                    @click="editPart(part)"
                    class="text-blue-600 hover:text-blue-900"
                  >
                    Edit
                  </button>
                  <button
                    @click="viewPart(part)"
                    class="text-green-600 hover:text-green-900"
                  >
                    View
                  </button>
                  <button
                    @click="deletePart(part.id)"
                    class="text-red-600 hover:text-red-900"
                  >
                    Delete
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <!-- Pagination -->
        <div v-if="parts.length > 0" class="mt-4 flex justify-between items-center">
          <div class="text-sm text-gray-500">
            Showing {{ parts.length }} parts
          </div>
          <div class="flex space-x-2">
            <button
              @click="previousPage"
              :disabled="currentPage === 1"
              class="px-3 py-1 text-sm border rounded-md disabled:opacity-50"
            >
              Previous
            </button>
            <span class="px-3 py-1 text-sm">{{ currentPage }}</span>
            <button
              @click="nextPage"
              class="px-3 py-1 text-sm border rounded-md"
            >
              Next
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Add Part Modal -->
    <div v-if="showAddPartModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
        <div class="mt-3">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Add New Part</h3>
          <form @submit.prevent="createPart">
            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700">Part Name *</label>
                <input
                  v-model="newPart.part_name"
                  type="text"
                  required
                  class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700">Brand OEM *</label>
                <input
                  v-model="newPart.brand_oem"
                  type="text"
                  required
                  class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700">Vehicle Make *</label>
                  <input
                    v-model="newPart.vehicle_make"
                    type="text"
                    required
                    class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700">Vehicle Model *</label>
                  <input
                    v-model="newPart.vehicle_model"
                    type="text"
                    required
                    class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700">OEM Code</label>
                <input
                  v-model="newPart.oem_code"
                  type="text"
                  class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700">Category *</label>
                <input
                  v-model="newPart.category"
                  type="text"
                  required
                  class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
            <div class="mt-6 flex justify-end space-x-3">
              <button
                type="button"
                @click="showAddPartModal = false"
                class="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400"
              >
                Cancel
              </button>
              <button
                type="submit"
                class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                Create Part
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Import Modal -->
    <div v-if="showImportModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
        <div class="mt-3">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Import Parts from Excel</h3>
          <div class="mb-4">
            <p class="text-sm text-gray-600 mb-2">Upload an Excel file with the following columns:</p>
            <ul class="text-xs text-gray-500 list-disc list-inside">
              <li>part_name (required)</li>
              <li>brand_oem (required)</li>
              <li>vehicle_make (required)</li>
              <li>vehicle_model (required)</li>
              <li>category (required)</li>
              <li>oem_code (optional)</li>
              <li>vehicle_trim (optional)</li>
              <li>subcategory (optional)</li>
              <li>position (optional)</li>
              <li>unit (optional, default: pcs)</li>
              <li>pack_size (optional)</li>
            </ul>
          </div>
          <input
            ref="fileInput"
            type="file"
            accept=".xlsx,.xls,.csv"
            @change="handleFileUpload"
            class="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
          />
          <div class="mt-6 flex justify-end space-x-3">
            <button
              @click="showImportModal = false"
              class="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400"
            >
              Cancel
            </button>
            <button
              @click="importParts"
              :disabled="!selectedFile"
              class="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50"
            >
              Import
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, reactive } from 'vue'
import axios from 'axios'

const API_BASE = 'http://localhost:8001/api/v1'

export default {
  name: 'Parts',
  setup() {
    const parts = ref([])
    const categories = ref([])
    const vehicleMakes = ref([])
    const loading = ref(false)
    const error = ref(null)
    const currentPage = ref(1)
    const showAddPartModal = ref(false)
    const showImportModal = ref(false)
    const selectedFile = ref(null)
    
    const filters = reactive({
      search: '',
      category: '',
      vehicle_make: '',
      status: ''
    })
    
    const newPart = reactive({
      part_name: '',
      brand_oem: '',
      vehicle_make: '',
      vehicle_model: '',
      oem_code: '',
      category: '',
      vehicle_trim: '',
      subcategory: '',
      position: '',
      unit: 'pcs',
      pack_size: null
    })
    
    const fetchParts = async () => {
      loading.value = true
      error.value = null
      
      try {
        const params = new URLSearchParams({
          skip: (currentPage.value - 1) * 20,
          limit: 20
        })
        
        if (filters.search) params.append('search', filters.search)
        if (filters.category) params.append('category', filters.category)
        if (filters.vehicle_make) params.append('vehicle_make', filters.vehicle_make)
        if (filters.status) params.append('status', filters.status)
        
        const response = await axios.get(`${API_BASE}/parts/?${params}`)
        parts.value = response.data
      } catch (err) {
        error.value = err.response?.data?.detail || 'Failed to fetch parts'
        console.error('Error fetching parts:', err)
      } finally {
        loading.value = false
      }
    }
    
    const fetchCategories = async () => {
      try {
        const response = await axios.get(`${API_BASE}/parts/categories/list`)
        categories.value = response.data.categories
      } catch (err) {
        console.error('Error fetching categories:', err)
      }
    }
    
    const fetchVehicleMakes = async () => {
      try {
        const response = await axios.get(`${API_BASE}/parts/vehicle-makes/list`)
        vehicleMakes.value = response.data.vehicle_makes
      } catch (err) {
        console.error('Error fetching vehicle makes:', err)
      }
    }
    
    const createPart = async () => {
      try {
        await axios.post(`${API_BASE}/parts/`, newPart)
        showAddPartModal.value = false
        resetNewPart()
        fetchParts()
      } catch (err) {
        error.value = err.response?.data?.detail || 'Failed to create part'
        console.error('Error creating part:', err)
      }
    }
    
    const editPart = (part) => {
      // Implement edit functionality
      console.log('Edit part:', part)
      // Navigate to edit form or open modal
      // For now, just log the part data
      selectedPart.value = part
      showEditModal.value = true
    }
    
    const viewPart = (part) => {
      // Implement view functionality
      console.log('View part:', part)
      // Navigate to detail view or open modal
      // For now, just log the part data
      selectedPart.value = part
      showDetailModal.value = true
    }
    
    const deletePart = async (partId) => {
      if (!confirm('Are you sure you want to delete this part?')) return
      
      try {
        await axios.delete(`${API_BASE}/parts/${partId}`)
        fetchParts()
      } catch (err) {
        error.value = err.response?.data?.detail || 'Failed to delete part'
        console.error('Error deleting part:', err)
      }
    }
    
    const handleFileUpload = (event) => {
      selectedFile.value = event.target.files[0]
    }
    
    const importParts = async () => {
      if (!selectedFile.value) return
      
      try {
        const formData = new FormData()
        formData.append('file', selectedFile.value)
        
        const response = await axios.post(`${API_BASE}/parts/bulk-import`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })
        
        alert(`Import completed: ${response.data.imported} parts imported, ${response.data.errors} errors`)
        showImportModal.value = false
        selectedFile.value = null
        fetchParts()
      } catch (err) {
        error.value = err.response?.data?.detail || 'Failed to import parts'
        console.error('Error importing parts:', err)
      }
    }
    
    const applyFilters = () => {
      currentPage.value = 1
      fetchParts()
    }
    
    const clearFilters = () => {
      Object.keys(filters).forEach(key => {
        filters[key] = ''
      })
      applyFilters()
    }
    
    const resetNewPart = () => {
      Object.keys(newPart).forEach(key => {
        if (typeof newPart[key] === 'string') {
          newPart[key] = ''
        } else if (typeof newPart[key] === 'number') {
          newPart[key] = null
        }
      })
      newPart.unit = 'pcs'
    }
    
    const previousPage = () => {
      if (currentPage.value > 1) {
        currentPage.value--
        fetchParts()
      }
    }
    
    const nextPage = () => {
      currentPage.value++
      fetchParts()
    }
    
    const getStatusBadgeClass = (status) => {
      return status === 'active' 
        ? 'bg-green-100 text-green-800'
        : 'bg-red-100 text-red-800'
    }
    
    onMounted(() => {
      fetchParts()
      fetchCategories()
      fetchVehicleMakes()
    })
    
    return {
      parts,
      categories,
      vehicleMakes,
      loading,
      error,
      currentPage,
      filters,
      newPart,
      showAddPartModal,
      showImportModal,
      selectedFile,
      fetchParts,
      createPart,
      editPart,
      viewPart,
      deletePart,
      handleFileUpload,
      importParts,
      applyFilters,
      clearFilters,
      previousPage,
      nextPage,
      getStatusBadgeClass
    }
  }
}
</script>
