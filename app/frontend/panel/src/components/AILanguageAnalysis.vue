<template>
  <div class="ai-language-analysis">
    <div class="analysis-header mb-6">
      <h2 class="text-2xl font-bold text-gray-800 mb-2">
        🌐 AI Language Analysis
      </h2>
      <p class="text-gray-600">
        Analyze text for language detection, entity extraction, and search
        optimization
      </p>
    </div>

    <!-- Text Input -->
    <div class="text-input-container mb-6">
      <label class="block text-sm font-medium text-gray-700 mb-2">
        Enter text to analyze:
      </label>
      <div class="relative">
        <textarea
          v-model="inputText"
          placeholder="Enter text in Persian or English, e.g., 'لنت ترمز چری تیگو 8 جلو' or 'brake pad for Chery Tiggo 8'"
          class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
          rows="4"
          @input="onTextChange"
        ></textarea>
        <button
          :disabled="isLoading || !inputText.trim()"
          class="absolute bottom-2 right-2 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          @click="analyzeText"
        >
          {{ isLoading ? "Analyzing..." : "Analyze" }}
        </button>
      </div>
    </div>

    <!-- Analysis Results -->
    <div v-if="analysisResult" class="analysis-results">
      <!-- Language Detection -->
      <div class="result-section mb-6 p-4 bg-blue-50 rounded-lg">
        <h3 class="font-semibold text-blue-800 mb-3">Language Detection</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <span class="font-medium">Detected Language:</span>
            <span
              class="ml-2 px-2 py-1 bg-blue-100 text-blue-800 rounded text-sm font-medium"
            >
              {{ analysisResult.language }}
            </span>
          </div>
          <div>
            <span class="font-medium">Confidence:</span>
            <span class="ml-2"
              >{{ Math.round(analysisResult.language_confidence * 100) }}%</span
            >
          </div>
          <div>
            <span class="font-medium">Contains Persian:</span>
            <span
              class="ml-2"
              :class="
                analysisResult.contains_persian
                  ? 'text-green-600'
                  : 'text-gray-600'
              "
            >
              {{ analysisResult.contains_persian ? "Yes" : "No" }}
            </span>
          </div>
          <div>
            <span class="font-medium">Contains English:</span>
            <span
              class="ml-2"
              :class="
                analysisResult.contains_english
                  ? 'text-green-600'
                  : 'text-gray-600'
              "
            >
              {{ analysisResult.contains_english ? "Yes" : "No" }}
            </span>
          </div>
        </div>
      </div>

      <!-- Text Normalization -->
      <div class="result-section mb-6 p-4 bg-green-50 rounded-lg">
        <h3 class="font-semibold text-green-800 mb-3">Text Normalization</h3>
        <div class="space-y-2">
          <div>
            <span class="font-medium text-sm">Original Text:</span>
            <div class="mt-1 p-2 bg-white border rounded text-sm">
              {{ analysisResult.original_text }}
            </div>
          </div>
          <div>
            <span class="font-medium text-sm">Normalized Text:</span>
            <div class="mt-1 p-2 bg-white border rounded text-sm">
              {{ analysisResult.normalized_text }}
            </div>
          </div>
        </div>
      </div>

      <!-- Entity Extraction -->
      <div
        v-if="
          analysisResult.entities &&
          Object.keys(analysisResult.entities).length > 0
        "
        class="result-section mb-6 p-4 bg-purple-50 rounded-lg"
      >
        <h3 class="font-semibold text-purple-800 mb-3">Extracted Entities</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div
            v-for="(values, key) in analysisResult.entities"
            :key="key"
            class="space-y-1"
          >
            <div class="font-medium text-sm capitalize">
              {{ key.replace("_", " ") }}:
            </div>
            <div v-if="values.length > 0" class="flex flex-wrap gap-1">
              <span
                v-for="value in values"
                :key="value"
                class="px-2 py-1 bg-purple-100 text-purple-800 rounded text-xs"
              >
                {{ value }}
              </span>
            </div>
            <div v-else class="text-gray-500 text-xs">None detected</div>
          </div>
        </div>
      </div>

      <!-- Search Variants -->
      <div
        v-if="
          analysisResult.search_variants &&
          analysisResult.search_variants.length > 0
        "
        class="result-section mb-6 p-4 bg-yellow-50 rounded-lg"
      >
        <h3 class="font-semibold text-yellow-800 mb-3">Search Variants</h3>
        <div class="text-sm text-yellow-700 mb-2">
          AI-generated search variants for better matching:
        </div>
        <div class="flex flex-wrap gap-2">
          <span
            v-for="(variant, index) in analysisResult.search_variants"
            :key="index"
            class="px-3 py-1 bg-yellow-100 text-yellow-800 rounded text-sm"
          >
            {{ variant }}
          </span>
        </div>
      </div>

      <!-- Language Features -->
      <div class="result-section mb-6 p-4 bg-gray-50 rounded-lg">
        <h3 class="font-semibold text-gray-800 mb-3">Language Features</h3>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
          <div>
            <span class="font-medium">Is Mixed Language:</span>
            <span
              class="ml-2"
              :class="
                analysisResult.is_mixed ? 'text-orange-600' : 'text-gray-600'
              "
            >
              {{ analysisResult.is_mixed ? "Yes" : "No" }}
            </span>
          </div>
          <div>
            <span class="font-medium">Text Length:</span>
            <span class="ml-2"
              >{{ analysisResult.original_text?.length || 0 }} characters</span
            >
          </div>
          <div>
            <span class="font-medium">Word Count:</span>
            <span class="ml-2"
              >{{
                analysisResult.original_text?.split(" ").length || 0
              }}
              words</span
            >
          </div>
        </div>
      </div>
    </div>

    <!-- No Analysis -->
    <div
      v-else-if="hasAnalyzed && !isLoading"
      class="no-analysis text-center py-8"
    >
      <div class="text-gray-500 text-lg mb-2">No analysis available</div>
      <div class="text-gray-400 text-sm">Enter some text to analyze</div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="loading text-center py-8">
      <div
        class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"
      ></div>
      <div class="mt-2 text-gray-600">Analyzing text with AI...</div>
    </div>

    <!-- Error State -->
    <div
      v-if="error"
      class="error bg-red-50 border border-red-200 rounded-lg p-4 mb-6"
    >
      <div class="text-red-800 font-medium">Analysis Error</div>
      <div class="text-red-600 text-sm mt-1">{{ error }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useAuthStore } from "@/stores/auth";

const authStore = useAuthStore();

// Reactive data
const inputText = ref("");
const analysisResult = ref(null);
const isLoading = ref(false);
const hasAnalyzed = ref(false);
const error = ref("");

// Debounce timer for auto-analysis
let analysisTimer = null;

// Methods
const onTextChange = () => {
  if (analysisTimer) {
    clearTimeout(analysisTimer);
  }

  analysisTimer = setTimeout(() => {
    if (inputText.value.trim().length > 3) {
      analyzeText();
    }
  }, 1000); // Auto-analyze after 1 second of no typing
};

const analyzeText = async () => {
  if (!inputText.value.trim()) return;

  isLoading.value = true;
  hasAnalyzed.value = true;
  error.value = "";

  try {
    const response = await fetch("/api/v1/ai/language-analysis", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${authStore.token}`,
      },
      body: JSON.stringify({ text: inputText.value }),
    });

    if (response.ok) {
      const data = await response.json();
      analysisResult.value = data;
    } else {
      const errorData = await response.json();
      error.value = errorData.detail || "Analysis failed";
    }
  } catch (err) {
    console.error("Analysis error:", err);
    error.value = "An error occurred while analyzing text";
  } finally {
    isLoading.value = false;
  }
};

onMounted(() => {
  // Initialize component
});
</script>

<style scoped>
.ai-language-analysis {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.result-section {
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
