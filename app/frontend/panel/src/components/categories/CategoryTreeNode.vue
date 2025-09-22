<template>
  <div class="tree-node">
    <div
      class="node-content"
      :class="{
        selected: isSelected,
        'hover:bg-gray-50': !isSelected,
      }"
      :style="{ paddingLeft: `${level * 20 + 8}px` }"
    >
      <!-- Expand/Collapse Button -->
      <button
        v-if="hasChildren"
        class="expand-button"
        :class="{ expanded: isExpanded }"
        @click="toggleExpansion"
      >
        <svg
          class="w-4 h-4 transition-transform"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M9 5l7 7-7 7"
          />
        </svg>
      </button>
      <div v-else class="expand-placeholder"></div>

      <!-- Category Info -->
      <div class="category-info" @click="selectCategory">
        <div class="flex items-center justify-between w-full">
          <div class="flex items-center space-x-2">
            <!-- Category Icon -->
            <div class="category-icon">
              <svg
                class="w-4 h-4 text-gray-500"
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
            </div>

            <!-- Category Name -->
            <div class="category-details">
              <div class="category-name">{{ category.name }}</div>
              <div v-if="category.name_fa" class="category-name-fa">
                {{ category.name_fa }}
              </div>
              <div v-if="category.name_cn" class="category-name-cn">
                {{ category.name_cn }}
              </div>
            </div>
          </div>

          <!-- Category Stats and Actions -->
          <div class="flex items-center space-x-2">
            <!-- Stats -->
            <div class="category-stats">
              <span v-if="category.children_count > 0" class="stat-item">
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
                    d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
                  />
                </svg>
                {{ category.children_count }}
              </span>
              <span v-if="category.parts_count > 0" class="stat-item">
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
                    d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"
                  />
                </svg>
                {{ category.parts_count }}
              </span>
            </div>

            <!-- Status Badge -->
            <span
              :class="[
                category.is_active
                  ? 'bg-green-100 text-green-800'
                  : 'bg-red-100 text-red-800',
                'inline-flex px-2 py-1 text-xs font-semibold rounded-full',
              ]"
            >
              {{ category.is_active ? "Active" : "Inactive" }}
            </span>

            <!-- Actions Menu -->
            <div class="relative">
              <button
                class="actions-button"
                :class="{ active: showActionsMenu }"
                @click.stop="toggleActionsMenu"
              >
                <svg
                  class="w-4 h-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z"
                  />
                </svg>
              </button>

              <!-- Actions Dropdown -->
              <div v-if="showActionsMenu" class="actions-dropdown" @click.stop>
                <button class="action-item" @click="editCategory">
                  <svg
                    class="w-4 h-4 mr-2"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                    />
                  </svg>
                  Edit
                </button>
                <button class="action-item" @click="addSubCategory">
                  <svg
                    class="w-4 h-4 mr-2"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M12 6v6m0 0v6m0-6h6m-6 0H6"
                    />
                  </svg>
                  Add Subcategory
                </button>
                <button
                  class="action-item text-red-600 hover:bg-red-50"
                  @click="deleteCategory"
                >
                  <svg
                    class="w-4 h-4 mr-2"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                    />
                  </svg>
                  Delete
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Children Nodes -->
    <div v-if="hasChildren && isExpanded" class="children-nodes">
      <CategoryTreeNode
        v-for="child in children"
        :key="child.id"
        :category="child"
        :level="level + 1"
        :expanded-nodes="expandedNodes"
        :selected-category="selectedCategory"
        @toggle-expansion="$emit('toggle-expansion', $event)"
        @select-category="$emit('select-category', $event)"
        @edit-category="$emit('edit-category', $event)"
        @delete-category="$emit('delete-category', $event)"
      />
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from "vue";
import { useCategoriesStore } from "../../stores/categories";

export default {
  name: "CategoryTreeNode",
  props: {
    category: {
      type: Object,
      required: true,
    },
    level: {
      type: Number,
      default: 0,
    },
    expandedNodes: {
      type: Set,
      required: true,
    },
    selectedCategory: {
      type: Object,
      default: null,
    },
  },
  emits: [
    "toggle-expansion",
    "select-category",
    "edit-category",
    "delete-category",
  ],
  setup(props, { emit }) {
    const categoriesStore = useCategoriesStore();
    const showActionsMenu = ref(false);

    const isExpanded = computed(() =>
      props.expandedNodes.has(props.category.id),
    );
    const isSelected = computed(
      () => props.selectedCategory?.id === props.category.id,
    );
    const hasChildren = computed(() => props.category.children_count > 0);
    const children = computed(() =>
      categoriesStore.getChildren(props.category.id),
    );

    const toggleExpansion = () => {
      emit("toggle-expansion", props.category.id);
    };

    const selectCategory = () => {
      emit("select-category", props.category);
    };

    const editCategory = () => {
      showActionsMenu.value = false;
      emit("edit-category", props.category);
    };

    const deleteCategory = () => {
      showActionsMenu.value = false;
      emit("delete-category", props.category);
    };

    const addSubCategory = () => {
      showActionsMenu.value = false;
      emit("edit-category", { parent_id: props.category.id });
    };

    const toggleActionsMenu = () => {
      showActionsMenu.value = !showActionsMenu.value;
    };

    const closeActionsMenu = () => {
      showActionsMenu.value = false;
    };

    onMounted(() => {
      document.addEventListener("click", closeActionsMenu);
    });

    onUnmounted(() => {
      document.removeEventListener("click", closeActionsMenu);
    });

    return {
      showActionsMenu,
      isExpanded,
      isSelected,
      hasChildren,
      children,
      toggleExpansion,
      selectCategory,
      editCategory,
      deleteCategory,
      addSubCategory,
      toggleActionsMenu,
    };
  },
};
</script>

<style scoped>
.tree-node {
  position: relative;
}

.node-content {
  display: flex;
  align-items: center;
  padding: 8px 0;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.node-content.selected {
  background-color: #eff6ff;
  border-left: 3px solid #3b82f6;
}

.expand-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  margin-right: 8px;
  border: none;
  background: none;
  cursor: pointer;
  border-radius: 2px;
  transition: background-color 0.2s;
}

.expand-button:hover {
  background-color: #f3f4f6;
}

.expand-button.expanded svg {
  transform: rotate(90deg);
}

.expand-placeholder {
  width: 20px;
  margin-right: 8px;
}

.category-info {
  flex: 1;
  min-width: 0;
}

.category-details {
  min-width: 0;
}

.category-name {
  font-weight: 500;
  color: #111827;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.category-name-fa {
  font-size: 0.75rem;
  color: #6b7280;
  margin-top: 1px;
}

.category-name-cn {
  font-size: 0.75rem;
  color: #6b7280;
  margin-top: 1px;
}

.category-stats {
  display: flex;
  align-items: center;
  gap: 4px;
}

.stat-item {
  display: flex;
  align-items: center;
  font-size: 0.75rem;
  color: #6b7280;
  margin-right: 8px;
}

.actions-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border: none;
  background: none;
  cursor: pointer;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.actions-button:hover,
.actions-button.active {
  background-color: #f3f4f6;
}

.actions-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  z-index: 50;
  margin-top: 4px;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  box-shadow:
    0 10px 15px -3px rgba(0, 0, 0, 0.1),
    0 4px 6px -2px rgba(0, 0, 0, 0.05);
  min-width: 160px;
}

.action-item {
  display: flex;
  align-items: center;
  width: 100%;
  padding: 8px 12px;
  text-align: left;
  border: none;
  background: none;
  cursor: pointer;
  font-size: 0.875rem;
  color: #374151;
  transition: background-color 0.2s;
}

.action-item:hover {
  background-color: #f9fafb;
}

.children-nodes {
  border-left: 1px solid #e5e7eb;
  margin-left: 10px;
}
</style>
