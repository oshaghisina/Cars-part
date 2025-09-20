<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="bg-white shadow rounded-lg p-6">
      <div class="flex justify-between items-center">
        <div>
          <h1 class="text-2xl font-bold text-gray-900">Category Management</h1>
          <p class="text-gray-600 mt-2">Manage hierarchical part categories with tree structure</p>
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
          <button
            @click="showCategoryForm = true"
            class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
            Add Category
          </button>
        </div>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
      <div class="bg-white overflow-hidden shadow rounded-lg">
        <div class="p-5">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div class="w-8 h-8 bg-blue-500 rounded-md flex items-center justify-center">
                <span class="text-white text-sm font-medium">📁</span>
              </div>
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">Total Categories</dt>
                <dd class="text-lg font-medium text-gray-900">{{ categoriesStore.categoriesCount }}</dd>
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
                <span class="text-white text-sm font-medium">🌳</span>
              </div>
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">Root Categories</dt>
                <dd class="text-lg font-medium text-gray-900">{{ categoriesStore.rootCategories.length }}</dd>
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
                <span class="text-white text-sm font-medium">✅</span>
              </div>
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">Active Categories</dt>
                <dd class="text-lg font-medium text-gray-900">{{ categoriesStore.activeCategories.length }}</dd>
              </dl>
            </div>
          </div>
        </div>
      </div>

      <div class="bg-white overflow-hidden shadow rounded-lg">
        <div class="p-5">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div class="w-8 h-8 bg-orange-500 rounded-md flex items-center justify-center">
                <span class="text-white text-sm font-medium">🔧</span>
              </div>
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">Total Parts</dt>
                <dd class="text-lg font-medium text-gray-900">{{ totalPartsCount }}</dd>
              </dl>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Category Tree -->
      <div class="lg:col-span-2">
        <div class="bg-white shadow rounded-lg">
          <div class="px-6 py-4 border-b border-gray-200">
            <h3 class="text-lg font-medium text-gray-900">Category Tree</h3>
            <p class="text-sm text-gray-500 mt-1">Hierarchical view of all categories</p>
          </div>
          <div class="p-6">
            <CategoryTree
              @select-category="onCategorySelected"
              @edit-category="onEditCategory"
              @delete-category="onDeleteCategory"
            />
          </div>
        </div>
      </div>

      <!-- Category Details -->
      <div class="lg:col-span-1">
        <div class="bg-white shadow rounded-lg">
          <div class="px-6 py-4 border-b border-gray-200">
            <h3 class="text-lg font-medium text-gray-900">Category Details</h3>
          </div>
          <div class="p-6">
            <div v-if="!selectedCategory" class="text-center py-8">
              <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
              <h3 class="mt-2 text-sm font-medium text-gray-900">No category selected</h3>
              <p class="mt-1 text-sm text-gray-500">Select a category from the tree to view details.</p>
            </div>

            <div v-else class="space-y-4">
              <!-- Category Header -->
              <div class="border-b border-gray-200 pb-4">
                <h4 class="text-lg font-medium text-gray-900">{{ selectedCategory.name }}</h4>
                <div v-if="selectedCategory.name_fa" class="text-sm text-gray-600 mt-1">
                  {{ selectedCategory.name_fa }}
                </div>
                <div v-if="selectedCategory.name_cn" class="text-sm text-gray-600 mt-1">
                  {{ selectedCategory.name_cn }}
                </div>
                <div class="mt-2">
                  <span
                    :class="[
                      selectedCategory.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800',
                      'inline-flex px-2 py-1 text-xs font-semibold rounded-full'
                    ]"
                  >
                    {{ selectedCategory.is_active ? 'Active' : 'Inactive' }}
                  </span>
                </div>
              </div>

              <!-- Category Stats -->
              <div class="grid grid-cols-2 gap-4">
                <div class="text-center p-3 bg-gray-50 rounded-lg">
                  <div class="text-2xl font-bold text-gray-900">{{ selectedCategory.children_count || 0 }}</div>
                  <div class="text-sm text-gray-500">Subcategories</div>
                </div>
                <div class="text-center p-3 bg-gray-50 rounded-lg">
                  <div class="text-2xl font-bold text-gray-900">{{ selectedCategory.parts_count || 0 }}</div>
                  <div class="text-sm text-gray-500">Parts</div>
                </div>
              </div>

              <!-- Category Description -->
              <div v-if="selectedCategory.description">
                <h5 class="text-sm font-medium text-gray-900 mb-2">Description</h5>
                <p class="text-sm text-gray-600">{{ selectedCategory.description }}</p>
              </div>

              <!-- Category Code -->
              <div v-if="selectedCategory.code">
                <h5 class="text-sm font-medium text-gray-900 mb-1">Code</h5>
                <p class="text-sm text-gray-600 font-mono">{{ selectedCategory.code }}</p>
              </div>

              <!-- Category Path -->
              <div v-if="categoryPath.length > 1">
                <h5 class="text-sm font-medium text-gray-900 mb-2">Path</h5>
                <div class="flex items-center space-x-1 text-sm text-gray-600">
                  <span v-for="(category, index) in categoryPath" :key="category.id">
                    <span>{{ category.name }}</span>
                    <span v-if="index < categoryPath.length - 1" class="mx-1">›</span>
                  </span>
                </div>
              </div>

              <!-- Actions -->
              <div class="pt-4 border-t border-gray-200">
                <div class="flex space-x-2">
                  <button
                    @click="editSelectedCategory"
                    class="flex-1 inline-flex justify-center items-center px-3 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                  >
                    <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                    Edit
                  </button>
                  <button
                    @click="deleteSelectedCategory"
                    class="flex-1 inline-flex justify-center items-center px-3 py-2 border border-red-300 shadow-sm text-sm font-medium rounded-md text-red-700 bg-white hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                  >
                    <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                    Delete
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Category Form Modal -->
    <CategoryForm
      v-if="showCategoryForm"
      :category="editingCategory"
      @close="closeCategoryForm"
      @saved="onCategorySaved"
    />

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteConfirm" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
        <div class="mt-3">
          <div class="flex items-center justify-center w-12 h-12 mx-auto bg-red-100 rounded-full">
            <svg class="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
          <div class="mt-3 text-center">
            <h3 class="text-lg font-medium text-gray-900">Delete Category</h3>
            <div class="mt-2">
              <p class="text-sm text-gray-500">
                Are you sure you want to delete "<strong>{{ deletingCategory?.name }}</strong>"?
              </p>
              <p v-if="deletingCategory?.children_count > 0" class="text-sm text-red-600 mt-2">
                This category has {{ deletingCategory.children_count }} subcategories that will also be deleted.
              </p>
              <p v-if="deletingCategory?.parts_count > 0" class="text-sm text-red-600 mt-1">
                This category has {{ deletingCategory.parts_count }} parts that will be affected.
              </p>
            </div>
          </div>
          <div class="mt-6 flex justify-center space-x-3">
            <button
              @click="showDeleteConfirm = false"
              class="inline-flex justify-center py-2 px-4 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Cancel
            </button>
            <button
              @click="confirmDelete"
              class="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
            >
              Delete
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useCategoriesStore } from '../../stores/categories'
import CategoryTree from '../../components/categories/CategoryTree.vue'
import CategoryForm from '../../components/categories/CategoryForm.vue'

export default {
  name: 'Categories',
  components: {
    CategoryTree,
    CategoryForm
  },
  setup() {
    const categoriesStore = useCategoriesStore()

    const showCategoryForm = ref(false)
    const showDeleteConfirm = ref(false)
    const editingCategory = ref(null)
    const deletingCategory = ref(null)

    const selectedCategory = computed(() => categoriesStore.selectedCategory)
    
    const categoryPath = computed(() => {
      if (!selectedCategory.value) return []
      return categoriesStore.getCategoryPath(selectedCategory.value.id)
    })

    const totalPartsCount = computed(() => {
      return categoriesStore.categories.reduce((total, cat) => total + (cat.parts_count || 0), 0)
    })

    const refreshData = async () => {
      await categoriesStore.fetchCategories()
    }

    const onCategorySelected = (category) => {
      categoriesStore.setSelectedCategory(category)
    }

    const onEditCategory = (category) => {
      editingCategory.value = category
      showCategoryForm.value = true
    }

    const onDeleteCategory = (category) => {
      deletingCategory.value = category
      showDeleteConfirm.value = true
    }

    const editSelectedCategory = () => {
      if (selectedCategory.value) {
        onEditCategory(selectedCategory.value)
      }
    }

    const deleteSelectedCategory = () => {
      if (selectedCategory.value) {
        onDeleteCategory(selectedCategory.value)
      }
    }

    const closeCategoryForm = () => {
      showCategoryForm.value = false
      editingCategory.value = null
    }

    const onCategorySaved = () => {
      closeCategoryForm()
      categoriesStore.fetchCategories()
    }

    const confirmDelete = async () => {
      if (!deletingCategory.value) return

      try {
        await categoriesStore.deleteCategory(deletingCategory.value.id)
        showDeleteConfirm.value = false
        deletingCategory.value = null
        categoriesStore.clearSelectedCategory()
        await categoriesStore.fetchCategories()
      } catch (error) {
        console.error('Error deleting category:', error)
      }
    }

    onMounted(async () => {
      await refreshData()
    })

    return {
      categoriesStore,
      showCategoryForm,
      showDeleteConfirm,
      editingCategory,
      deletingCategory,
      selectedCategory,
      categoryPath,
      totalPartsCount,
      refreshData,
      onCategorySelected,
      onEditCategory,
      onDeleteCategory,
      editSelectedCategory,
      deleteSelectedCategory,
      closeCategoryForm,
      onCategorySaved,
      confirmDelete
    }
  }
}
</script>
