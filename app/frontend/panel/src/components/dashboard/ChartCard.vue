<template>
  <div class="bg-white shadow rounded-lg">
    <div class="px-6 py-4 border-b border-gray-200">
      <div class="flex justify-between items-center">
        <h3 class="text-lg font-medium text-gray-900">{{ title }}</h3>
        <div class="flex space-x-2">
          <button
            v-if="refreshable"
            class="text-gray-400 hover:text-gray-600"
            :disabled="loading"
            @click="$emit('refresh')"
          >
            <svg
              class="w-5 h-5"
              :class="{ 'animate-spin': loading }"
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
          <button
            v-if="expandable"
            class="text-gray-400 hover:text-gray-600"
            @click="$emit('expand')"
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
                d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4"
              />
            </svg>
          </button>
        </div>
      </div>
    </div>

    <div class="p-6">
      <!-- Loading State -->
      <div v-if="loading" class="flex items-center justify-center h-64">
        <div
          class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"
        ></div>
        <p class="ml-3 text-sm text-gray-500">Loading chart data...</p>
      </div>

      <!-- Empty State -->
      <div v-else-if="!hasData" class="flex items-center justify-center h-64">
        <div class="text-center">
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
              d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
            />
          </svg>
          <h3 class="mt-2 text-sm font-medium text-gray-900">
            No data available
          </h3>
          <p class="mt-1 text-sm text-gray-500">{{ emptyMessage }}</p>
        </div>
      </div>

      <!-- Chart Content -->
      <div v-else class="h-64">
        <slot :data="data" :loading="loading">
          <!-- Default chart placeholder -->
          <div
            class="flex items-center justify-center h-full bg-gray-50 rounded-lg"
          >
            <div class="text-center">
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
                  d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                />
              </svg>
              <p class="mt-2 text-sm text-gray-500">Chart component needed</p>
            </div>
          </div>
        </slot>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "ChartCard",
  props: {
    title: {
      type: String,
      required: true,
    },
    data: {
      type: [Array, Object],
      default: () => [],
    },
    loading: {
      type: Boolean,
      default: false,
    },
    refreshable: {
      type: Boolean,
      default: true,
    },
    expandable: {
      type: Boolean,
      default: true,
    },
    emptyMessage: {
      type: String,
      default: "No data to display",
    },
  },
  emits: ["refresh", "expand"],
  computed: {
    hasData() {
      if (Array.isArray(this.data)) {
        return this.data.length > 0;
      }
      return Object.keys(this.data || {}).length > 0;
    },
  },
};
</script>
