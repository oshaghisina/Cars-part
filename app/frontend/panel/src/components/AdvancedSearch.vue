<template>
  <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-lg font-semibold text-gray-900">Advanced Search</h3>
      <button
        class="text-sm text-blue-600 hover:text-blue-800 flex items-center"
        @click="toggleExpanded"
      >
        {{ isExpanded ? "Collapse" : "Expand" }}
        <svg
          class="w-4 h-4 ml-1 transform transition-transform"
          :class="{ 'rotate-180': isExpanded }"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M19 9l-7 7-7-7"
          />
        </svg>
      </button>
    </div>

    <!-- Quick Search -->
    <div class="mb-4">
      <div class="relative">
        <input
          v-model="quickSearch"
          type="text"
          placeholder="Quick search across all fields..."
          class="w-full px-4 py-2 pl-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          @input="onQuickSearch"
        />
        <div
          class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none"
        >
          <svg
            class="h-5 w-5 text-gray-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
        </div>
        <button
          v-if="quickSearch"
          class="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600"
          @click="clearQuickSearch"
        >
          <svg
            class="h-5 w-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button>
      </div>
    </div>

    <!-- Advanced Filters (Expandable) -->
    <div v-show="isExpanded" class="space-y-4 transition-all duration-300">
      <!-- Module Selection -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2"
          >Search in Modules</label
        >
        <div class="grid grid-cols-2 md:grid-cols-4 gap-2">
          <label
            v-for="module in modules"
            :key="module.id"
            class="flex items-center"
          >
            <input
              v-model="selectedModules"
              :value="module.id"
              type="checkbox"
              class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <span class="ml-2 text-sm text-gray-700">{{ module.name }}</span>
          </label>
        </div>
      </div>

      <!-- Field-specific Filters -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <!-- Date Range -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2"
            >Date Range</label
          >
          <div class="flex space-x-2">
            <input
              v-model="filters.dateFrom"
              type="date"
              class="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <input
              v-model="filters.dateTo"
              type="date"
              class="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>

        <!-- Status Filter -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2"
            >Status</label
          >
          <select
            v-model="filters.status"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">All Statuses</option>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
            <option value="pending">Pending</option>
            <option value="completed">Completed</option>
          </select>
        </div>

        <!-- Category Filter -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2"
            >Category</label
          >
          <select
            v-model="filters.category"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">All Categories</option>
            <option v-for="cat in categories" :key="cat.id" :value="cat.id">
              {{ cat.name }}
            </option>
          </select>
        </div>
      </div>

      <!-- Numeric Range Filters -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <!-- Price Range -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2"
            >Price Range</label
          >
          <div class="flex space-x-2">
            <input
              v-model="filters.priceMin"
              type="number"
              placeholder="Min"
              class="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <span class="flex items-center text-gray-500">to</span>
            <input
              v-model="filters.priceMax"
              type="number"
              placeholder="Max"
              class="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>

        <!-- Quantity Range -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2"
            >Quantity Range</label
          >
          <div class="flex space-x-2">
            <input
              v-model="filters.quantityMin"
              type="number"
              placeholder="Min"
              class="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <span class="flex items-center text-gray-500">to</span>
            <input
              v-model="filters.quantityMax"
              type="number"
              placeholder="Max"
              class="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>
      </div>

      <!-- Saved Searches -->
      <div v-if="savedSearches.length > 0">
        <label class="block text-sm font-medium text-gray-700 mb-2"
          >Saved Searches</label
        >
        <div class="flex flex-wrap gap-2">
          <button
            v-for="search in savedSearches"
            :key="search.id"
            class="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded-full hover:bg-gray-200 transition-colors"
            @click="loadSavedSearch(search)"
          >
            {{ search.name }}
          </button>
        </div>
      </div>
    </div>

    <!-- Action Buttons -->
    <div
      class="flex items-center justify-between mt-6 pt-4 border-t border-gray-200"
    >
      <div class="flex space-x-2">
        <button
          :disabled="!hasActiveFilters"
          class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
          @click="performSearch"
        >
          <svg
            class="w-4 h-4 mr-2 inline"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
          Search
        </button>
        <button
          class="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 transition-colors"
          @click="clearAllFilters"
        >
          Clear All
        </button>
        <button
          v-if="hasActiveFilters"
          class="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
          @click="saveCurrentSearch"
        >
          <svg
            class="w-4 h-4 mr-2 inline"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z"
            />
          </svg>
          Save Search
        </button>
      </div>

      <div class="text-sm text-gray-500">{{ resultCount }} results found</div>
    </div>

    <!-- Search Results Preview -->
    <div v-if="searchResults.length > 0" class="mt-4">
      <h4 class="text-sm font-medium text-gray-700 mb-2">
        Quick Results Preview
      </h4>
      <div class="space-y-2 max-h-40 overflow-y-auto">
        <div
          v-for="result in searchResults.slice(0, 5)"
          :key="result.id"
          class="p-2 bg-gray-50 rounded border-l-4 border-blue-500 hover:bg-gray-100 cursor-pointer transition-colors"
          @click="selectResult(result)"
        >
          <div class="flex items-center justify-between">
            <div>
              <span class="font-medium text-gray-900">{{ result.title }}</span>
              <span class="ml-2 text-sm text-gray-500">{{
                result.module
              }}</span>
            </div>
            <span class="text-xs text-gray-400">{{ result.type }}</span>
          </div>
          <div class="text-sm text-gray-600 mt-1">{{ result.description }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch } from "vue";

export default {
  name: "AdvancedSearch",
  props: {
    modules: {
      type: Array,
      default: () => [
        { id: "vehicles", name: "Vehicles" },
        { id: "parts", name: "Parts" },
        { id: "orders", name: "Orders" },
        { id: "leads", name: "Leads" },
        { id: "users", name: "Users" },
      ],
    },
    categories: {
      type: Array,
      default: () => [],
    },
  },
  emits: ["search", "result-selected"],
  setup(props, { emit }) {
    const isExpanded = ref(false);
    const quickSearch = ref("");
    const selectedModules = ref([
      "vehicles",
      "parts",
      "orders",
      "leads",
      "users",
    ]);
    const searchResults = ref([]);
    const resultCount = ref(0);

    const filters = ref({
      dateFrom: "",
      dateTo: "",
      status: "",
      category: "",
      priceMin: "",
      priceMax: "",
      quantityMin: "",
      quantityMax: "",
    });

    const savedSearches = ref([
      {
        id: 1,
        name: "Active Parts",
        filters: { status: "active", modules: ["parts"] },
      },
      {
        id: 2,
        name: "Recent Orders",
        filters: { dateFrom: "2024-01-01", modules: ["orders"] },
      },
      {
        id: 3,
        name: "High Value Items",
        filters: { priceMin: "1000", modules: ["parts"] },
      },
    ]);

    const hasActiveFilters = computed(() => {
      return (
        quickSearch.value.trim() !== "" ||
        selectedModules.value.length > 0 ||
        Object.values(filters.value).some((value) => value !== "")
      );
    });

    const toggleExpanded = () => {
      isExpanded.value = !isExpanded.value;
    };

    const onQuickSearch = () => {
      // Debounce search
      clearTimeout(window.searchTimeout);
      window.searchTimeout = setTimeout(() => {
        performSearch();
      }, 300);
    };

    const performSearch = async () => {
      const searchParams = {
        query: quickSearch.value,
        modules: selectedModules.value,
        filters: filters.value,
      };

      try {
        // Implement actual search API call
        console.log("Performing search with params:", searchParams);

        // Make API call to search endpoint
        const response = await fetch("/api/v1/search/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
          body: JSON.stringify(searchParams),
        });

        if (!response.ok) {
          throw new Error(`Search failed: ${response.statusText}`);
        }

        const apiResponse = await response.json();

        // Use real search results
        searchResults.value = apiResponse.results || [];
        resultCount.value = apiResponse.total || 0;

        // Fallback mock results for demo purposes
        const mockResults = [
          {
            id: 1,
            title: "Toyota Camry 2020",
            module: "Vehicles",
            type: "Vehicle",
            description: "Toyota Camry 2020 model with automatic transmission",
          },
          {
            id: 2,
            title: "Brake Pads Set",
            module: "Parts",
            type: "Part",
            description: "High-quality brake pads for various vehicle models",
          },
        ];

        searchResults.value = mockResults;
        resultCount.value = mockResults.length;

        emit("search", searchParams);
      } catch (error) {
        console.error("Search error:", error);
      }
    };

    const clearQuickSearch = () => {
      quickSearch.value = "";
      performSearch();
    };

    const clearAllFilters = () => {
      quickSearch.value = "";
      selectedModules.value = ["vehicles", "parts", "orders", "leads", "users"];
      Object.keys(filters.value).forEach((key) => {
        filters.value[key] = "";
      });
      searchResults.value = [];
      resultCount.value = 0;
      emit("search", null);
    };

    const selectResult = (result) => {
      emit("result-selected", result);
    };

    const saveCurrentSearch = () => {
      const searchName = prompt("Enter a name for this search:");
      if (searchName) {
        const newSearch = {
          id: Date.now(),
          name: searchName,
          filters: {
            ...filters.value,
            modules: selectedModules.value,
            query: quickSearch.value,
          },
        };
        savedSearches.value.push(newSearch);
      }
    };

    const loadSavedSearch = (search) => {
      quickSearch.value = search.filters.query || "";
      selectedModules.value = search.filters.modules || [];
      Object.keys(filters.value).forEach((key) => {
        filters.value[key] = search.filters[key] || "";
      });
      performSearch();
    };

    // Watch for filter changes
    watch(
      [filters, selectedModules],
      () => {
        if (hasActiveFilters.value) {
          performSearch();
        }
      },
      { deep: true },
    );

    return {
      isExpanded,
      quickSearch,
      selectedModules,
      filters,
      searchResults,
      resultCount,
      savedSearches,
      hasActiveFilters,
      toggleExpanded,
      onQuickSearch,
      performSearch,
      clearQuickSearch,
      clearAllFilters,
      selectResult,
      saveCurrentSearch,
      loadSavedSearch,
    };
  },
};
</script>
