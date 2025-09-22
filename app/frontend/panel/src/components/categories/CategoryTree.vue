<template>
  <div class="category-tree">
    <!-- Tree Controls -->
    <div class="flex justify-between items-center mb-4">
      <div class="flex space-x-2">
        <button
          class="inline-flex items-center px-3 py-1 border border-gray-300 rounded-md shadow-sm text-xs font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          @click="expandAll"
        >
          <svg
            class="w-3 h-3 mr-1"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4"
            />
          </svg>
          Expand All
        </button>
        <button
          class="inline-flex items-center px-3 py-1 border border-gray-300 rounded-md shadow-sm text-xs font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          @click="collapseAll"
        >
          <svg
            class="w-3 h-3 mr-1"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M20 12H4m16 0l-4-4m4 4l-4 4"
            />
          </svg>
          Collapse All
        </button>
      </div>

      <div class="text-sm text-gray-500">{{ totalCategories }} categories</div>
    </div>

    <!-- Tree Structure -->
    <div class="tree-container border border-gray-200 rounded-lg bg-white">
      <div v-if="loading" class="p-4 text-center">
        <div
          class="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"
        ></div>
        <p class="mt-2 text-sm text-gray-500">Loading categories...</p>
      </div>

      <div
        v-else-if="categoriesStore.categories.length === 0"
        class="p-8 text-center"
      >
        <svg
          class="mx-auto h-12 w-12 text-gray-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
          />
        </svg>
        <h3 class="mt-2 text-sm font-medium text-gray-900">No categories</h3>
        <p class="mt-1 text-sm text-gray-500">
          Get started by creating a new category.
        </p>
      </div>

      <div v-else class="tree-nodes">
        <CategoryTreeNode
          v-for="category in rootCategories"
          :key="category.id"
          :category="category"
          :level="0"
          :expanded-nodes="categoriesStore.expandedNodes"
          :selected-category="categoriesStore.selectedCategory"
          @toggle-expansion="toggleNodeExpansion"
          @select-category="selectCategory"
          @edit-category="editCategory"
          @delete-category="deleteCategory"
        />
      </div>
    </div>
  </div>
</template>

<script>
import { computed, onMounted } from "vue";
import { useCategoriesStore } from "../../stores/categories";
import CategoryTreeNode from "./CategoryTreeNode.vue";

export default {
  name: "CategoryTree",
  components: {
    CategoryTreeNode,
  },
  emits: ["select-category", "edit-category", "delete-category"],
  setup(props, { emit }) {
    const categoriesStore = useCategoriesStore();

    const rootCategories = computed(() => categoriesStore.rootCategories);
    const totalCategories = computed(() => categoriesStore.categoriesCount);

    const expandAll = () => {
      categoriesStore.expandAll();
    };

    const collapseAll = () => {
      categoriesStore.collapseAll();
    };

    const toggleNodeExpansion = (categoryId) => {
      categoriesStore.toggleNodeExpansion(categoryId);
    };

    const selectCategory = (category) => {
      categoriesStore.setSelectedCategory(category);
      emit("select-category", category);
    };

    const editCategory = (category) => {
      emit("edit-category", category);
    };

    const deleteCategory = (category) => {
      emit("delete-category", category);
    };

    onMounted(async () => {
      if (categoriesStore.categories.length === 0) {
        await categoriesStore.fetchCategories();
      }
    });

    return {
      categoriesStore,
      rootCategories,
      totalCategories,
      expandAll,
      collapseAll,
      toggleNodeExpansion,
      selectCategory,
      editCategory,
      deleteCategory,
    };
  },
};
</script>

<style scoped>
.tree-container {
  max-height: 600px;
  overflow-y: auto;
}

.tree-nodes {
  padding: 8px;
}
</style>
