<template>
  <div class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
    <div class="relative top-10 mx-auto p-5 border w-full max-w-md shadow-lg rounded-md bg-white">
      <div class="mt-3">
        <!-- Header -->
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-medium text-gray-900">
            {{ isEditing ? 'Edit Category' : 'Add Category' }}
          </h3>
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
          <!-- Parent Category Selection -->
          <div v-if="!isEditing || (isEditing && !category.parent_id)">
            <label for="parent_id" class="block text-sm font-medium text-gray-700">Parent Category</label>
            <select
              id="parent_id"
              v-model="formData.parent_id"
              class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
            >
              <option value="">Root Category (No Parent)</option>
              <option
                v-for="cat in availableParentCategories"
                :key="cat.id"
                :value="cat.id"
                :disabled="isEditing && cat.id === category.id"
              >
                {{ getCategoryIndent(cat) }}{{ cat.name }}
              </option>
            </select>
            <p class="mt-1 text-xs text-gray-500">
              Select a parent category to create a subcategory, or leave empty for a root category.
            </p>
          </div>

          <!-- Category Name (English) -->
          <div>
            <label for="name" class="block text-sm font-medium text-gray-700">Category Name (English) *</label>
            <input
              id="name"
              v-model="formData.name"
              type="text"
              required
              class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              placeholder="e.g., Engine Parts"
            />
          </div>

          <!-- Category Name (Persian) -->
          <div>
            <label for="name_fa" class="block text-sm font-medium text-gray-700">Category Name (Persian)</label>
            <input
              id="name_fa"
              v-model="formData.name_fa"
              type="text"
              class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              placeholder="e.g., قطعات موتور"
            />
          </div>

          <!-- Category Name (Chinese) -->
          <div>
            <label for="name_cn" class="block text-sm font-medium text-gray-700">Category Name (Chinese)</label>
            <input
              id="name_cn"
              v-model="formData.name_cn"
              type="text"
              class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              placeholder="e.g., 发动机零件"
            />
          </div>

          <!-- Description -->
          <div>
            <label for="description" class="block text-sm font-medium text-gray-700">Description</label>
            <textarea
              id="description"
              v-model="formData.description"
              rows="3"
              class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              placeholder="Category description..."
            />
          </div>

          <!-- Category Code -->
          <div>
            <label for="code" class="block text-sm font-medium text-gray-700">Category Code</label>
            <input
              id="code"
              v-model="formData.code"
              type="text"
              class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              placeholder="e.g., ENG001"
            />
            <p class="mt-1 text-xs text-gray-500">
              Unique identifier for this category (optional).
            </p>
          </div>

          <!-- Sort Order -->
          <div>
            <label for="sort_order" class="block text-sm font-medium text-gray-700">Sort Order</label>
            <input
              id="sort_order"
              v-model="formData.sort_order"
              type="number"
              min="0"
              class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              placeholder="0"
            />
            <p class="mt-1 text-xs text-gray-500">
              Lower numbers appear first in the category list.
            </p>
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
              {{ loading ? (isEditing ? 'Updating...' : 'Creating...') : (isEditing ? 'Update Category' : 'Create Category') }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { useCategoriesStore } from '../../stores/categories'

export default {
  name: 'CategoryForm',
  props: {
    category: {
      type: Object,
      default: null
    }
  },
  emits: ['close', 'saved'],
  setup(props, { emit }) {
    const categoriesStore = useCategoriesStore()
    
    const loading = ref(false)
    const error = ref(null)
    
    const isEditing = computed(() => !!props.category && !!props.category.id)
    
    const formData = reactive({
      parent_id: props.category?.parent_id || '',
      name: props.category?.name || '',
      name_fa: props.category?.name_fa || '',
      name_cn: props.category?.name_cn || '',
      description: props.category?.description || '',
      code: props.category?.code || '',
      sort_order: props.category?.sort_order || 0,
      is_active: props.category?.is_active !== false
    })

    // Get available parent categories (excluding current category and its descendants)
    const availableParentCategories = computed(() => {
      if (!isEditing.value) {
        return categoriesStore.categories
      }
      
      // Exclude current category and its descendants
      const currentCategoryId = props.category.id
      const descendants = categoriesStore.getDescendants(currentCategoryId)
      const excludedIds = [currentCategoryId, ...descendants.map(d => d.id)]
      
      return categoriesStore.categories.filter(cat => !excludedIds.includes(cat.id))
    })

    const getCategoryIndent = (category) => {
      const path = categoriesStore.getCategoryPath(category.id)
      return '  '.repeat(path.length - 1)
    }

    const handleSubmit = async () => {
      loading.value = true
      error.value = null
      
      try {
        if (isEditing.value) {
          await categoriesStore.updateCategory(props.category.id, formData)
        } else {
          await categoriesStore.createCategory(formData)
        }
        emit('saved')
      } catch (err) {
        error.value = err.message || `Failed to ${isEditing.value ? 'update' : 'create'} category`
      } finally {
        loading.value = false
      }
    }

    onMounted(async () => {
      if (categoriesStore.categories.length === 0) {
        await categoriesStore.fetchCategories()
      }
    })

    return {
      categoriesStore,
      loading,
      error,
      isEditing,
      formData,
      availableParentCategories,
      getCategoryIndent,
      handleSubmit
    }
  }
}
</script>
