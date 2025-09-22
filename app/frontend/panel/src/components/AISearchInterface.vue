<template>
  <div class="ai-search-interface">
    <div class="search-header">
      <h2 class="text-2xl font-bold text-gray-800 mb-4">
        🤖 AI-Powered Search
      </h2>
      <p class="text-gray-600 mb-6">
        Search for car parts using natural language in Persian or English
      </p>
    </div>

    <!-- Search Input -->
    <div class="search-input-container mb-6">
      <div class="relative">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Try: 'لنت ترمز چری تیگو 8 جلو' or 'brake pad for Chery Tiggo 8'"
          class="w-full px-4 py-3 pr-12 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg"
          @keyup.enter="performSearch"
          @input="onQueryChange"
        />
        <button
          :disabled="isLoading || !searchQuery.trim()"
          class="absolute right-2 top-1/2 transform -translate-y-1/2 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          @click="performSearch"
        >
          {{ isLoading ? "Searching..." : "Search" }}
        </button>
      </div>

      <!-- Search Suggestions -->
      <div v-if="suggestions.length > 0" class="suggestions-container mt-2">
        <div class="text-sm text-gray-600 mb-2">Suggestions:</div>
        <div class="flex flex-wrap gap-2">
          <button
            v-for="suggestion in suggestions"
            :key="suggestion"
            class="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm hover:bg-gray-200 transition-colors"
            @click="selectSuggestion(suggestion)"
          >
            {{ suggestion }}
          </button>
        </div>
      </div>
    </div>

    <!-- Query Analysis -->
    <div
      v-if="queryAnalysis"
      class="query-analysis mb-6 p-4 bg-blue-50 rounded-lg"
    >
      <h3 class="font-semibold text-blue-800 mb-2">Query Analysis</h3>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
        <div>
          <span class="font-medium">Language:</span>
          <span class="capitalize">{{ queryAnalysis.language }}</span>
          <span class="text-gray-500"
            >({{ Math.round(queryAnalysis.language_confidence * 100) }}%
            confidence)</span
          >
        </div>
        <div>
          <span class="font-medium">Intent:</span>
          <span class="capitalize">{{ queryAnalysis.intent }}</span>
        </div>
        <div>
          <span class="font-medium">Complexity:</span>
          <span class="capitalize">{{ queryAnalysis.complexity }}</span>
        </div>
        <div>
          <span class="font-medium">Confidence:</span>
          <span>{{ Math.round(queryAnalysis.confidence * 100) }}%</span>
        </div>
      </div>

      <div
        v-if="
          queryAnalysis.entities &&
          Object.keys(queryAnalysis.entities).length > 0
        "
        class="mt-3"
      >
        <div class="font-medium text-blue-800 mb-1">Extracted Entities:</div>
        <div class="flex flex-wrap gap-2">
          <span
            v-for="(values, key) in queryAnalysis.entities"
            :key="key"
            class="text-xs"
          >
            <span class="font-medium">{{ key }}:</span>
            <span class="text-gray-600">{{ values.join(", ") }}</span>
          </span>
        </div>
      </div>
    </div>

    <!-- Search Results -->
    <div v-if="searchResults.length > 0" class="search-results">
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-lg font-semibold text-gray-800">
          Search Results ({{ searchResults.length }})
        </h3>
        <div class="flex gap-2">
          <select
            v-model="searchType"
            class="px-3 py-1 border border-gray-300 rounded text-sm"
            @change="performSearch"
          >
            <option value="hybrid">Hybrid Search</option>
            <option value="semantic">Semantic Search</option>
            <option value="keyword">Keyword Search</option>
            <option value="filter">Filter Search</option>
          </select>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div
          v-for="result in searchResults"
          :key="result.part_id"
          class="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
        >
          <div class="flex justify-between items-start mb-2">
            <h4 class="font-semibold text-gray-800">{{ result.part_name }}</h4>
            <span class="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
              {{ result.match_type }}
            </span>
          </div>

          <div class="text-sm text-gray-600 mb-2">
            <div><strong>Brand:</strong> {{ result.brand_oem }}</div>
            <div>
              <strong>Vehicle:</strong> {{ result.vehicle_make }}
              {{ result.vehicle_model }}
            </div>
            <div><strong>Category:</strong> {{ result.category }}</div>
            <div v-if="result.price">
              <strong>Price:</strong> ${{ result.price }}
            </div>
          </div>

          <div class="flex justify-between items-center">
            <span class="text-xs text-gray-500">
              Score: {{ Math.round(result.search_score * 100) }}%
            </span>
            <span
              :class="result.availability ? 'text-green-600' : 'text-red-600'"
              class="text-xs font-medium"
            >
              {{ result.availability ? "Available" : "Out of Stock" }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- No Results -->
    <div
      v-else-if="hasSearched && !isLoading"
      class="no-results text-center py-8"
    >
      <div class="text-gray-500 text-lg mb-2">No results found</div>
      <div class="text-gray-400 text-sm">
        Try adjusting your search terms or using different keywords
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="loading text-center py-8">
      <div
        class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"
      ></div>
      <div class="mt-2 text-gray-600">Searching with AI...</div>
    </div>

    <!-- Error State -->
    <div
      v-if="error"
      class="error bg-red-50 border border-red-200 rounded-lg p-4 mb-6"
    >
      <div class="text-red-800 font-medium">Search Error</div>
      <div class="text-red-600 text-sm mt-1">{{ error }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from "vue";
import { useAuthStore } from "@/stores/auth";

const authStore = useAuthStore();

// Reactive data
const searchQuery = ref("");
const searchResults = ref([]);
const suggestions = ref([]);
const queryAnalysis = ref(null);
const isLoading = ref(false);
const hasSearched = ref(false);
const error = ref("");
const searchType = ref("hybrid");

// Debounce timer for suggestions
let suggestionTimer = null;

// Methods
const onQueryChange = () => {
  if (suggestionTimer) {
    clearTimeout(suggestionTimer);
  }

  suggestionTimer = setTimeout(() => {
    if (searchQuery.value.trim().length > 2) {
      getSuggestions();
    } else {
      suggestions.value = [];
    }
  }, 300);
};

const getSuggestions = async () => {
  try {
    const response = await fetch(
      `/api/v1/ai/search-suggestions?query=${encodeURIComponent(searchQuery.value)}&limit=5`,
      {
        headers: {
          Authorization: `Bearer ${authStore.token}`,
        },
      },
    );

    if (response.ok) {
      const data = await response.json();
      suggestions.value = data.suggestions || [];
    }
  } catch (err) {
    console.error("Error getting suggestions:", err);
  }
};

const selectSuggestion = (suggestion) => {
  searchQuery.value = suggestion;
  suggestions.value = [];
  performSearch();
};

const performSearch = async () => {
  if (!searchQuery.value.trim()) return;

  isLoading.value = true;
  hasSearched.value = true;
  error.value = "";
  suggestions.value = [];

  try {
    // First, analyze the query
    const analysisResponse = await fetch("/api/v1/ai/query-analysis", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${authStore.token}`,
      },
      body: JSON.stringify({ query: searchQuery.value }),
    });

    if (analysisResponse.ok) {
      const analysisData = await analysisResponse.json();
      queryAnalysis.value = analysisData;
    }

    // Then perform the search
    const searchResponse = await fetch("/api/v1/ai/hybrid-search", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${authStore.token}`,
      },
      body: JSON.stringify({
        query: searchQuery.value,
        search_type: searchType.value,
        limit: 20,
      }),
    });

    if (searchResponse.ok) {
      const searchData = await searchResponse.json();
      searchResults.value = searchData.results || [];
    } else {
      const errorData = await searchResponse.json();
      error.value = errorData.detail || "Search failed";
    }
  } catch (err) {
    console.error("Search error:", err);
    error.value = "An error occurred while searching";
  } finally {
    isLoading.value = false;
  }
};

// Watch for search type changes
watch(searchType, () => {
  if (hasSearched.value) {
    performSearch();
  }
});

onMounted(() => {
  // Initialize component
});
</script>

<style scoped>
.ai-search-interface {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.suggestions-container {
  max-height: 200px;
  overflow-y: auto;
}

.search-results {
  animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.loading {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}
</style>
