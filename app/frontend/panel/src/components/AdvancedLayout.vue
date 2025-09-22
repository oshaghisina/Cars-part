<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Advanced Navigation -->
    <AdvancedNavBar @search="handleGlobalSearch" />

    <!-- Main Content Area -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      <!-- Page Header -->
      <div class="mb-6">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-2xl font-bold text-gray-900">{{ pageTitle }}</h1>
            <p class="mt-1 text-sm text-gray-600">{{ pageDescription }}</p>
          </div>
          <div class="flex items-center space-x-3">
            <!-- Quick Actions -->
            <div class="flex items-center space-x-2">
              <button
                v-for="action in quickActions"
                :key="action.id"
                :class="[
                  'inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md transition-colors',
                  action.variant === 'primary'
                    ? 'text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500'
                    : 'text-gray-700 bg-white border-gray-300 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500',
                ]"
                @click="action.handler"
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
                    :d="action.icon"
                  />
                </svg>
                {{ action.label }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Toolbar -->
      <div
        class="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6"
      >
        <div class="flex items-center justify-between">
          <!-- Left Side - Search and Filters -->
          <div class="flex items-center space-x-4">
            <!-- Advanced Search Toggle -->
            <button
              :class="[
                'inline-flex items-center px-3 py-2 border text-sm font-medium rounded-md transition-colors',
                showAdvancedSearch
                  ? 'border-blue-300 text-blue-700 bg-blue-50'
                  : 'border-gray-300 text-gray-700 bg-white hover:bg-gray-50',
              ]"
              @click="toggleAdvancedSearch"
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
                  d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.414A1 1 0 013 6.707V4z"
                />
              </svg>
              Advanced Search
            </button>

            <!-- Bulk Operations Toggle -->
            <button
              :class="[
                'inline-flex items-center px-3 py-2 border text-sm font-medium rounded-md transition-colors',
                showBulkOperations
                  ? 'border-green-300 text-green-700 bg-green-50'
                  : 'border-gray-300 text-gray-700 bg-white hover:bg-gray-50',
              ]"
              @click="toggleBulkOperations"
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
                  d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              Bulk Operations
            </button>

            <!-- View Options -->
            <div class="flex items-center space-x-2">
              <button
                :class="[
                  'p-2 rounded-md transition-colors',
                  viewMode === 'grid'
                    ? 'bg-blue-100 text-blue-600'
                    : 'text-gray-400 hover:text-gray-600',
                ]"
                @click="setViewMode('grid')"
              >
                <svg
                  class="w-5 h-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"
                  />
                </svg>
              </button>
              <button
                :class="[
                  'p-2 rounded-md transition-colors',
                  viewMode === 'list'
                    ? 'bg-blue-100 text-blue-600'
                    : 'text-gray-400 hover:text-gray-600',
                ]"
                @click="setViewMode('list')"
              >
                <svg
                  class="w-5 h-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M4 6h16M4 10h16M4 14h16M4 18h16"
                  />
                </svg>
              </button>
            </div>
          </div>

          <!-- Right Side - Selection Info and Actions -->
          <div class="flex items-center space-x-4">
            <div
              v-if="selectedItems.length > 0"
              class="flex items-center space-x-2"
            >
              <span class="text-sm text-gray-600"
                >{{ selectedItems.length }} selected</span
              >
              <button
                class="text-sm text-gray-500 hover:text-gray-700"
                @click="clearSelection"
              >
                Clear
              </button>
            </div>

            <!-- Refresh Button -->
            <button
              :disabled="isLoading"
              class="inline-flex items-center p-2 border border-gray-300 rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              @click="refreshData"
            >
              <svg
                class="w-4 h-4"
                :class="{ 'animate-spin': isLoading }"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                />
              </svg>
            </button>
          </div>
        </div>
      </div>

      <!-- Advanced Search Panel -->
      <div v-if="showAdvancedSearch" class="mb-6">
        <AdvancedSearch
          :modules="searchModules"
          :categories="categories"
          @search="handleAdvancedSearch"
          @result-selected="handleSearchResultSelected"
        />
      </div>

      <!-- Bulk Operations Panel -->
      <div v-if="showBulkOperations" class="mb-6">
        <BulkOperations
          :selected-items="selectedItems"
          :categories="categories"
          @import-complete="handleImportComplete"
          @export-complete="handleExportComplete"
          @batch-operation="handleBatchOperation"
          @clear-selection="clearSelection"
        />
      </div>

      <!-- Main Content Area -->
      <div class="bg-white rounded-lg shadow-sm border border-gray-200">
        <!-- Content Header -->
        <div class="px-6 py-4 border-b border-gray-200">
          <div class="flex items-center justify-between">
            <h2 class="text-lg font-medium text-gray-900">
              {{ contentTitle }}
            </h2>
            <div class="flex items-center space-x-2">
              <!-- Pagination Info -->
              <span class="text-sm text-gray-600">
                Showing {{ pagination.start }} to {{ pagination.end }} of
                {{ pagination.total }} results
              </span>
              <!-- Items per page -->
              <select
                v-model="pagination.perPage"
                class="text-sm border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                @change="onPerPageChange"
              >
                <option value="10">10 per page</option>
                <option value="25">25 per page</option>
                <option value="50">50 per page</option>
                <option value="100">100 per page</option>
              </select>
            </div>
          </div>
        </div>

        <!-- Content Body -->
        <div class="p-6">
          <slot
            :view-mode="viewMode"
            :selected-items="selectedItems"
            :pagination="pagination"
            :is-loading="isLoading"
          />
        </div>

        <!-- Content Footer - Pagination -->
        <div
          v-if="pagination.total > pagination.perPage"
          class="px-6 py-4 border-t border-gray-200"
        >
          <div class="flex items-center justify-between">
            <div class="flex-1 flex justify-between sm:hidden">
              <button
                :disabled="pagination.currentPage === 1"
                class="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                @click="goToPreviousPage"
              >
                Previous
              </button>
              <button
                :disabled="pagination.currentPage === pagination.totalPages"
                class="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                @click="goToNextPage"
              >
                Next
              </button>
            </div>
            <div
              class="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between"
            >
              <div>
                <nav
                  class="relative z-0 inline-flex rounded-md shadow-sm -space-x-px"
                  aria-label="Pagination"
                >
                  <button
                    :disabled="pagination.currentPage === 1"
                    class="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                    @click="goToPreviousPage"
                  >
                    <svg
                      class="h-5 w-5"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path
                        fill-rule="evenodd"
                        d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z"
                        clip-rule="evenodd"
                      />
                    </svg>
                  </button>
                  <button
                    v-for="page in visiblePages"
                    :key="page"
                    :class="[
                      'relative inline-flex items-center px-4 py-2 border text-sm font-medium',
                      page === pagination.currentPage
                        ? 'z-10 bg-blue-50 border-blue-500 text-blue-600'
                        : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50',
                    ]"
                    @click="goToPage(page)"
                  >
                    {{ page }}
                  </button>
                  <button
                    :disabled="pagination.currentPage === pagination.totalPages"
                    class="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                    @click="goToNextPage"
                  >
                    <svg
                      class="h-5 w-5"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path
                        fill-rule="evenodd"
                        d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z"
                        clip-rule="evenodd"
                      />
                    </svg>
                  </button>
                </nav>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading Overlay -->
    <div
      v-if="isLoading"
      class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50"
    >
      <div
        class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white"
      >
        <div class="mt-3 text-center">
          <div
            class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-blue-100"
          >
            <svg
              class="animate-spin h-6 w-6 text-blue-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
              />
            </svg>
          </div>
          <h3 class="text-lg font-medium text-gray-900 mt-2">Loading...</h3>
          <p class="text-sm text-gray-500 mt-1">{{ loadingMessage }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch } from "vue";
import AdvancedNavBar from "./AdvancedNavBar.vue";
import AdvancedSearch from "./AdvancedSearch.vue";
import BulkOperations from "./BulkOperations.vue";

export default {
  name: "AdvancedLayout",
  components: {
    AdvancedNavBar,
    AdvancedSearch,
    BulkOperations,
  },
  props: {
    pageTitle: {
      type: String,
      default: "Dashboard",
    },
    pageDescription: {
      type: String,
      default: "Manage your data efficiently",
    },
    contentTitle: {
      type: String,
      default: "Content",
    },
    quickActions: {
      type: Array,
      default: () => [],
    },
    searchModules: {
      type: Array,
      default: () => [],
    },
    categories: {
      type: Array,
      default: () => [],
    },
    totalItems: {
      type: Number,
      default: 0,
    },
    isLoading: {
      type: Boolean,
      default: false,
    },
    loadingMessage: {
      type: String,
      default: "Please wait...",
    },
  },
  emits: [
    "search",
    "refresh",
    "page-change",
    "per-page-change",
    "view-mode-change",
    "selection-change",
    "batch-operation",
  ],
  setup(props, { emit }) {
    const showAdvancedSearch = ref(false);
    const showBulkOperations = ref(false);
    const viewMode = ref("list");
    const selectedItems = ref([]);

    const pagination = ref({
      currentPage: 1,
      perPage: 25,
      total: props.totalItems,
      totalPages: Math.ceil(props.totalItems / 25),
    });

    const paginationStart = computed(() => {
      return (pagination.value.currentPage - 1) * pagination.value.perPage + 1;
    });

    const paginationEnd = computed(() => {
      return Math.min(
        pagination.value.currentPage * pagination.value.perPage,
        pagination.value.total,
      );
    });

    const visiblePages = computed(() => {
      const current = pagination.value.currentPage;
      const total = pagination.value.totalPages;
      const pages = [];

      if (total <= 7) {
        for (let i = 1; i <= total; i++) {
          pages.push(i);
        }
      } else {
        if (current <= 4) {
          for (let i = 1; i <= 5; i++) pages.push(i);
          pages.push("...");
          pages.push(total);
        } else if (current >= total - 3) {
          pages.push(1);
          pages.push("...");
          for (let i = total - 4; i <= total; i++) pages.push(i);
        } else {
          pages.push(1);
          pages.push("...");
          for (let i = current - 1; i <= current + 1; i++) pages.push(i);
          pages.push("...");
          pages.push(total);
        }
      }

      return pages.filter(
        (page) =>
          page !== "..." || pages.indexOf(page) !== pages.lastIndexOf(page),
      );
    });

    const toggleAdvancedSearch = () => {
      showAdvancedSearch.value = !showAdvancedSearch.value;
      if (showAdvancedSearch.value) {
        showBulkOperations.value = false;
      }
    };

    const toggleBulkOperations = () => {
      showBulkOperations.value = !showBulkOperations.value;
      if (showBulkOperations.value) {
        showAdvancedSearch.value = false;
      }
    };

    const setViewMode = (mode) => {
      viewMode.value = mode;
      emit("view-mode-change", mode);
    };

    const clearSelection = () => {
      selectedItems.value = [];
      emit("selection-change", []);
    };

    const refreshData = () => {
      emit("refresh");
    };

    const handleGlobalSearch = (query) => {
      emit("search", { type: "global", query });
    };

    const handleAdvancedSearch = (searchParams) => {
      emit("search", { type: "advanced", ...searchParams });
    };

    const handleSearchResultSelected = (result) => {
      emit("search", { type: "result-selected", result });
    };

    const handleImportComplete = (result) => {
      if (result.success) {
        refreshData();
      }
    };

    const handleExportComplete = (result) => {
      console.log("Export completed:", result);
    };

    const handleBatchOperation = (operation) => {
      emit("batch-operation", operation);
    };

    const goToPage = (page) => {
      if (
        page !== pagination.value.currentPage &&
        page >= 1 &&
        page <= pagination.value.totalPages
      ) {
        pagination.value.currentPage = page;
        emit("page-change", page);
      }
    };

    const goToPreviousPage = () => {
      if (pagination.value.currentPage > 1) {
        goToPage(pagination.value.currentPage - 1);
      }
    };

    const goToNextPage = () => {
      if (pagination.value.currentPage < pagination.value.totalPages) {
        goToPage(pagination.value.currentPage + 1);
      }
    };

    const onPerPageChange = () => {
      pagination.value.currentPage = 1;
      pagination.value.totalPages = Math.ceil(
        pagination.value.total / pagination.value.perPage,
      );
      emit("per-page-change", pagination.value.perPage);
    };

    // Watch for total items changes
    watch(
      () => props.totalItems,
      (newTotal) => {
        pagination.value.total = newTotal;
        pagination.value.totalPages = Math.ceil(
          newTotal / pagination.value.perPage,
        );
      },
    );

    return {
      showAdvancedSearch,
      showBulkOperations,
      viewMode,
      selectedItems,
      pagination: computed(() => ({
        ...pagination.value,
        start: paginationStart.value,
        end: paginationEnd.value,
      })),
      visiblePages,
      toggleAdvancedSearch,
      toggleBulkOperations,
      setViewMode,
      clearSelection,
      refreshData,
      handleGlobalSearch,
      handleAdvancedSearch,
      handleSearchResultSelected,
      handleImportComplete,
      handleExportComplete,
      handleBatchOperation,
      goToPage,
      goToPreviousPage,
      goToNextPage,
      onPerPageChange,
    };
  },
};
</script>
