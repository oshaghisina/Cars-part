<template>
  <div class="space-y-6">
    <div class="bg-white shadow rounded-lg p-6">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold text-gray-900">Search</h1>
          <p class="text-gray-600 mt-1">
            Showing results for
            <span class="font-semibold">"{{ searchTerm || "All" }}"</span>
          </p>
        </div>
      </div>
    </div>

    <div class="bg-white shadow rounded-lg">
      <div
        class="px-6 py-4 border-b border-gray-200 flex items-center justify-between"
      >
        <span class="text-sm text-gray-500">
          {{ results.length }} result{{ results.length === 1 ? "" : "s" }}
        </span>
        <button
          class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          @click="refresh"
        >
          Refresh
        </button>
      </div>

      <div v-if="loading" class="px-6 py-10 text-center text-gray-500">
        Searching...
      </div>

      <div v-else-if="error" class="px-6 py-10 text-center">
        <p class="text-red-500">{{ error }}</p>
      </div>

      <div
        v-else-if="!results.length"
        class="px-6 py-10 text-center text-gray-500"
      >
        No matches found. Try a different query.
      </div>

      <ul v-else class="divide-y divide-gray-200">
        <li
          v-for="part in results"
          :key="part.id"
          class="px-6 py-4 flex justify-between items-center hover:bg-gray-50"
        >
          <div>
            <p class="text-sm font-medium text-gray-900">
              {{ part.part_name || part.name || "Unnamed Part" }}
            </p>
            <p v-if="part.vehicle_make" class="text-xs text-gray-500">
              {{ part.vehicle_make }} {{ part.vehicle_model }}
            </p>
            <p v-if="part.oem_code" class="text-xs text-gray-400">
              OEM: {{ part.oem_code }}
            </p>
          </div>
          <router-link
            :to="{ path: '/parts', query: { highlight: part.id } }"
            class="text-sm text-blue-600 hover:text-blue-800"
          >
            View in Parts
          </router-link>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from "vue";
import { useRoute } from "vue-router";

import { usePartsStore } from "../../stores/parts";

const route = useRoute();
const partsStore = usePartsStore();

const searchTerm = ref(route.query.q?.toString() || "");
const results = ref([]);
const loading = ref(false);
const error = ref(null);

const normaliseResults = (payload) => {
  if (Array.isArray(payload?.items)) return payload.items;
  if (Array.isArray(payload?.results)) return payload.results;
  if (Array.isArray(payload?.data)) return payload.data;
  if (Array.isArray(payload)) return payload;
  return [];
};

const loadResults = async (term) => {
  if (!term) {
    results.value = [];
    return;
  }

  loading.value = true;
  error.value = null;
  try {
    const payload = await partsStore.searchParts(term);
    results.value = normaliseResults(payload);
  } catch (err) {
    error.value = err?.message || "Search failed";
    console.error("Search error:", err);
  } finally {
    loading.value = false;
  }
};

const refresh = () => loadResults(searchTerm.value);

watch(
  () => route.query.q,
  (newQuery) => {
    const term = newQuery?.toString() || "";
    searchTerm.value = term;
    loadResults(term);
  },
  { immediate: true },
);
</script>
